from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .composition_search import (
    SearchEvaluation,
    depth_one_search,
    evaluate_candidate,
    random_search,
    structured_search,
)
from .compositional_realization import fit_composed_representation
from .compositional_worlds import HELD_OUT_FAMILY, generate_heldout_world
from .conditions import Condition, PromptSpec, ProposalSource, _public_payload, build_prompt
from .executable import (
    evaluate_executable,
    expression_loss,
    freeze_theory,
    parse_theory,
    program_expression,
)
from .expressions import Expression
from .external_reasoning_calibration import _arrow_table, _manifest, _prediction_table
from .generic_primitives import ComposedRepresentation, GenericPrimitive, apply_primitive
from .llm import OpenAICompatibleClient, extract_json_object
from .primary_experiment import _thresholds
from .proposals import select_external_proposals
from .realization import fit_representation
from .worlds import FAMILIES, World, generate_world

PRIMARY_CONDITIONS = (
    Condition.C0_FIXED_SPACE,
    Condition.C2_GENERIC_DEPTH_1,
    Condition.C3_GENERIC_COMPOSITION,
    Condition.C_SELF_LLM_COMPOSITION,
    Condition.C_RAND_RANDOM_PRIMITIVES,
)


def _world(config: dict[str, Any], family: str, seed: int) -> World:
    no_jump = bool(config.get("no_jump", False))
    if family == HELD_OUT_FAMILY:
        return generate_heldout_world(seed, no_jump=no_jump)
    return generate_world(family, seed, no_jump=no_jump)


def _translate_expression(expression: Expression, names: dict[str, str]) -> Expression:
    def walk(value: Any) -> Any:
        if isinstance(value, dict):
            result = {key: walk(item) for key, item in value.items()}
            if result.get("op") in {"var", "raw_var", "history_sum"}:
                result["name"] = names.get(str(result["name"]), str(result["name"]))
            return result
        if isinstance(value, list):
            return [walk(item) for item in value]
        return value

    return Expression(walk(expression.tree))


def _primitive_contract() -> dict[str, Any]:
    return {
        "portfolio": "GENERIC_PRIMITIVE_SET_V1",
        "operators": [operator.value for operator in GenericPrimitive if operator is not GenericPrimitive.SUBGRAPH_CROSSOVER],
        "forbidden": [
            "LATENTIZE",
            "ADD_STATE",
            "PROPERTY_TO_RELATION",
            "ADD_REGIME",
            "COMMON_CAUSE",
            "META_LAW",
            "UNIFY_MECHANISMS",
            "CAUSAL_CONFOUNDER",
            "COORDINATE_TRANSFORM",
        ],
        "steps_per_plan": 4,
        "plans_required": 16,
        "step_schema": {"operator": "OPERATOR_NAME", "arguments": {"argument_name": "string_value"}},
        "rules": [
            "ADD_NODE accepts only id and creates Primitive",
            "scientific type requires CHANGE_NODE_TYPE",
            "observability, arity, temporal index, dependencies, and bindings are separate edits",
            "every argument node id must already exist at that step",
            "do not use family names or claim prospective outcomes",
        ],
    }


def _self_prompt(world: World) -> PromptSpec:
    payload = _public_payload(world.public())
    payload["generic_primitive_contract"] = _primitive_contract()
    system = (
        "You explore representation graphs using only a frozen vocabulary of local rewrites. "
        "Return exactly one compact JSON object and no markdown. Do not predict or invent outcomes."
    )
    user = (
        "Construct exactly 16 independent plans of exactly four primitive steps. Plans may use "
        "only the supplied generic vocabulary. A node created by ADD_NODE starts as Primitive; "
        "typing and every other structural property require later steps. Return schema "
        '{"plans":[[{"operator":"...","arguments":{}}]]}. World: '
        + json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )
    return PromptSpec(
        "generic-self-composition-v1",
        Condition.C_SELF_LLM_COMPOSITION,
        ProposalSource.LLM_COMPOSITION,
        system,
        user,
    )


def _parse_self_plans(
    world: World, output: str, seed: int, *, required_plans: int = 16
) -> tuple[list[SearchEvaluation], list[dict[str, Any]]]:
    payload = extract_json_object(output)
    plans = payload.get("plans")
    if not isinstance(plans, list):
        raise TypeError("plans must be a list")
    evaluations: list[SearchEvaluation] = []
    trace: list[dict[str, Any]] = []
    for plan_index in range(required_plans):
        if plan_index >= len(plans) or not isinstance(plans[plan_index], list):
            trace.append({"plan_index": plan_index, "valid": False, "error": "missing_plan"})
            continue
        plan = plans[plan_index]
        if len(plan) != 4:
            trace.append({"plan_index": plan_index, "valid": False, "error": "depth_not_four"})
            continue
        current = ComposedRepresentation(world.incumbent, ())
        try:
            for depth, step in enumerate(plan, start=1):
                if not isinstance(step, dict) or set(step) != {"operator", "arguments"}:
                    raise ValueError("invalid step schema")
                operator = GenericPrimitive(str(step["operator"]))
                if operator is GenericPrimitive.SUBGRAPH_CROSSOVER:
                    raise ValueError("crossover requires a donor and is unavailable to self plans")
                if not isinstance(step["arguments"], dict):
                    raise TypeError("arguments must be an object")
                arguments = {str(key): str(value) for key, value in step["arguments"].items()}
                child, record = apply_primitive(
                    current.representation,
                    operator,
                    arguments,
                    seed + plan_index * 10 + depth,
                    depth=depth,
                )
                current = ComposedRepresentation(child, current.ancestry + (record,))
            evaluation = evaluate_candidate(world.public(), current)
            evaluations.append(evaluation)
            trace.append(
                {
                    "plan_index": plan_index,
                    "valid": True,
                    "operators": list(current.operators),
                    "candidate_hash": current.representation.structural_hash,
                    "signature": evaluation.fit.structural_signature,
                }
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            trace.append(
                {"plan_index": plan_index, "valid": False, "error": f"{type(exc).__name__}:{exc}"}
            )
    return evaluations, trace


def _fixed_candidates(world: World, slots: int) -> list[SearchEvaluation]:
    base = ComposedRepresentation(world.incumbent, ())
    evaluation = evaluate_candidate(world.public(), base)
    return [evaluation] * slots


def _condition_candidates(
    world: World, condition: Condition, seed: int, slots: int, config: dict[str, Any]
) -> tuple[list[SearchEvaluation], dict[str, Any]]:
    if condition is Condition.C0_FIXED_SPACE:
        # Execute the matched number of within-space candidate evaluations. They are
        # intentionally identical in representation and cannot create a J1 opportunity.
        for _ in range(int(config["primitive_operation_budget"])):
            evaluate_candidate(world.public(), ComposedRepresentation(world.incumbent, ()))
        return _fixed_candidates(world, slots), {
            "primitive_operation_capacity": int(config["primitive_operation_budget"]),
            "primitive_operations_used": 0,
            "candidate_evaluations": int(config["primitive_operation_budget"]),
            "search": "fixed-space deterministic value evaluation",
        }
    if condition is Condition.C1_ATOMIC_HIGH_LEVEL:
        proposals = select_external_proposals(world.public(), seed, slots, diverse=False)
        evaluations = [
            evaluate_candidate(
                world.public(), ComposedRepresentation(item.representation, ())
            )
            for item in proposals
        ]
        return evaluations, {
            "primitive_operation_capacity": slots,
            "primitive_operations_used": slots,
            "candidate_evaluations": slots,
            "search": "frozen AJ5 atomic high-level portfolio",
            "legacy_ancestry": [list(item.operators) for item in proposals],
        }
    if condition is Condition.C2_GENERIC_DEPTH_1:
        result = depth_one_search(
            world.public(), seed, operation_budget=int(config["primitive_operation_budget"])
        )
    elif condition is Condition.C3_GENERIC_COMPOSITION:
        result = structured_search(
            world.public(),
            seed,
            breadth=int(config["search_breadth"]),
            max_depth=int(config["max_depth"]),
        )
    elif condition is Condition.C_RAND_RANDOM_PRIMITIVES:
        result = random_search(
            world.public(),
            seed,
            breadth=int(config["search_breadth"]),
            max_depth=int(config["max_depth"]),
        )
    elif condition is Condition.C5_ORACLE_REPRESENTATION:
        base = ComposedRepresentation(world.truth.representation, ())
        evaluation = evaluate_candidate(world.public(), base)
        return [evaluation] * slots, {
            "primitive_operation_capacity": 0,
            "primitive_operations_used": 0,
            "candidate_evaluations": slots,
            "search": "oracle representation ceiling",
        }
    else:
        raise ValueError(condition)
    return list(result.selected), {
        "primitive_operation_capacity": int(config["primitive_operation_budget"]),
        "primitive_operations_used": result.primitive_operations,
        "candidate_evaluations": result.candidate_evaluations,
        "search": condition.value,
    }


def _fit_for_condition(world: World, condition: Condition, representation: Any) -> tuple[Expression, float, str]:
    if condition is Condition.C1_ATOMIC_HIGH_LEVEL:
        fitted = fit_representation(world.public(), representation)
        return fitted.expression, fitted.observational_loss, "AJ5_HIGH_LEVEL_FITTER_FROZEN"
    if condition is Condition.C5_ORACLE_REPRESENTATION:
        expression = _translate_expression(program_expression(world.truth.program), dict(world.variable_names))
        internal_expression = program_expression(world.truth.program)
        return expression, expression_loss(internal_expression, world.observations), "ORACLE_PROGRAM_COMPILER"
    fitted = fit_composed_representation(world.public(), representation)
    return fitted.expression, fitted.observational_loss, fitted.structural_signature


def _run_world_condition(
    *,
    config: dict[str, Any],
    family: str,
    world_seed: int,
    condition: Condition,
    base_url: str,
    log_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    world = _world(config, family, world_seed)
    public = world.public()
    slots = int(config["candidate_slots"])
    search_seed = int(config["search_seed_base"]) + world_seed * 101 + list(Condition).index(condition)
    family_index = [*FAMILIES, HELD_OUT_FAMILY].index(family)
    client = OpenAICompatibleClient(base_url, _manifest(config), log_path)
    search_trace: list[dict[str, Any]] = []
    if condition is Condition.C_SELF_LLM_COMPOSITION:
        candidates: list[SearchEvaluation] = []
        self_calls: list[Any] = []
        for slot in range(slots):
            prompt = _self_prompt(world)
            output, call = client.generate(
                prompt,
                world_id=world.world_id,
                world_seed=world_seed,
                decoding_seed=int(config["decoding_seed_base"])
                + list(Condition).index(condition) * 10_000_000
                + family_index * 100_000
                + world_seed * 100
                + slot * 2,
                candidate_parent=world.incumbent.structural_hash,
            )
            self_calls.append(call)
            try:
                evaluated, trace = _parse_self_plans(
                    world,
                    output,
                    search_seed + slot * 1000,
                    required_plans=int(config["self_plans_per_slot"]),
                )
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                evaluated, trace = [], [{"valid": False, "error": f"{type(exc).__name__}:{exc}"}]
            search_trace.extend({"slot": slot, **row} for row in trace)
            candidates.append(
                max(
                    evaluated,
                    key=lambda item: (item.score, item.candidate.representation.structural_hash),
                    default=_fixed_candidates(world, 1)[0],
                )
            )
        search_meta = {
            "primitive_operation_capacity": int(config["primitive_operation_budget"]),
            "primitive_operations_used": sum(bool(row.get("valid")) * 4 for row in search_trace),
            "candidate_evaluations": int(config["primitive_operation_budget"]),
            "search": "LLM-selected generic composition",
            "phase_one_calls": self_calls,
        }
    else:
        candidates, search_meta = _condition_candidates(world, condition, search_seed, slots, config)

    candidate_rows: list[dict[str, Any]] = []
    for slot, candidate in enumerate(candidates[:slots]):
        representation = candidate.candidate.representation
        expression, obs_loss, signature = _fit_for_condition(world, condition, representation)
        table = _prediction_table(world, expression)
        exact_choice = max(table, key=lambda row: (float(row["absolute_separation"]), str(row["case_id"])))
        phase_one_call = None
        phase_one_valid = condition is Condition.C_SELF_LLM_COMPOSITION
        if condition is not Condition.C_SELF_LLM_COMPOSITION:
            phase_one_prompt = build_prompt(
                public,
                condition,
                ProposalSource.P1_EXTERNAL,
                representation,
            )
            phase_one_output, phase_one_call = client.generate(
                phase_one_prompt,
                world_id=world.world_id,
                world_seed=world_seed,
                decoding_seed=int(config["decoding_seed_base"])
                + list(Condition).index(condition) * 10_000_000
                + family_index * 100_000
                + world_seed * 100
                + slot * 2,
                candidate_parent=world.incumbent.structural_hash,
                mutation_ancestry=candidate.candidate.operators,
                representation_hash=representation.structural_hash,
            )
            try:
                extract_json_object(phase_one_output)
                phase_one_valid = True
            except ValueError:
                phase_one_valid = False
        phase_two_prompt = build_prompt(
            public,
            condition,
            ProposalSource.P2_ORACLE if condition is Condition.C5_ORACLE_REPRESENTATION else ProposalSource.COMPOSITION_SEARCH,
            representation,
            expression,
            obs_loss,
            table,
        )
        phase_two_output, phase_two_call = client.generate(
            phase_two_prompt,
            world_id=world.world_id,
            world_seed=world_seed,
            decoding_seed=int(config["decoding_seed_base"])
            + list(Condition).index(condition) * 10_000_000
            + family_index * 100_000
            + world_seed * 100
            + slot * 2
            + 1,
            candidate_parent=world.incumbent.structural_hash,
            mutation_ancestry=candidate.candidate.operators,
            representation_hash=representation.structural_hash,
        )
        row: dict[str, Any] = {
            "condition": condition.value,
            "family": family,
            "world_id": world.world_id,
            "world_seed": world_seed,
            "no_jump": world.no_jump,
            "slot": slot,
            "representation_hash": representation.structural_hash,
            "ancestry_depth": candidate.candidate.depth,
            "mutation_ancestry": list(candidate.candidate.operators),
            "structural_signature": signature,
            "observational_loss": obs_loss,
            "search_prediction_separation": candidate.max_prediction_separation,
            "phase_one_valid": phase_one_valid,
            "phase_two_valid": False,
            "validated_jump": False,
            "compositional_jump": False,
            "phase_one_tokens": phase_one_call.completion_tokens if phase_one_call else search_meta["phase_one_calls"][slot].completion_tokens,
            "phase_two_tokens": phase_two_call.completion_tokens,
            "primitive_operation_capacity": search_meta["primitive_operation_capacity"],
            "primitive_operations_used": search_meta["primitive_operations_used"],
            "candidate_evaluations": search_meta["candidate_evaluations"],
            "exact_designer_intervention_id": exact_choice["case_id"],
        }
        try:
            payload = extract_json_object(phase_two_output)
            payload["representation"] = representation.canonical_dict()
            payload["expression"] = expression.tree
            payload["selected_intervention_ids"] = [exact_choice["case_id"]]
            theory = parse_theory(
                payload,
                {public_name: internal for internal, public_name in world.variable_names},
            )
            result = evaluate_executable(world, theory, freeze_theory(world, theory), _thresholds(config))
            row.update(asdict(result))
            row["phase_two_valid"] = True
            row["validated_jump"] = result.validated_jump
            row["compositional_jump"] = bool(
                result.validated_jump
                and candidate.candidate.depth >= 2
                and condition
                in {
                    Condition.C3_GENERIC_COMPOSITION,
                    Condition.C_SELF_LLM_COMPOSITION,
                    Condition.C_RAND_RANDOM_PRIMITIVES,
                }
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            row["phase_two_error_type"] = type(exc).__name__
            row["phase_two_error"] = str(exc)
        candidate_rows.append(row)

    world_row = {
        "condition": condition.value,
        "family": family,
        "world_id": world.world_id,
        "world_seed": world_seed,
        "no_jump": world.no_jump,
        "condition_success": any(row["validated_jump"] for row in candidate_rows),
        "compositional_success": any(row["compositional_jump"] for row in candidate_rows),
        "accepted_candidates": sum(bool(row["validated_jump"]) for row in candidate_rows),
        "minimum_successful_depth": min(
            (int(row["ancestry_depth"]) for row in candidate_rows if row["validated_jump"]),
            default=None,
        ),
        "llm_calls": slots * 2,
        "llm_tokens": sum(int(row["phase_one_tokens"]) + int(row["phase_two_tokens"]) for row in candidate_rows),
        "primitive_operation_capacity": search_meta["primitive_operation_capacity"],
        "primitive_operations_used": search_meta["primitive_operations_used"],
        "candidate_evaluations": search_meta["candidate_evaluations"],
    }
    return candidate_rows, world_row, search_trace


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    conditions = tuple(Condition(value) for value in config["conditions"])
    jobs = [
        {
            "config": config,
            "family": family,
            "world_seed": int(seed),
            "condition": condition,
            "base_url": base_url,
            "log_path": output_dir / "llm_calls.jsonl",
        }
        for family in config["families"]
        for seed in config["world_seeds"]
        for condition in conditions
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates: list[dict[str, Any]] = []
    worlds: list[dict[str, Any]] = []
    self_traces: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=int(config.get("concurrency", 1))) as executor:
        futures = [executor.submit(_run_world_condition, **job) for job in jobs]
        for future in as_completed(futures):
            candidate_rows, world_row, traces = future.result()
            candidates.extend(candidate_rows)
            worlds.append(world_row)
            self_traces.extend(
                {"world_id": world_row["world_id"], "family": world_row["family"], **trace}
                for trace in traces
            )
    candidates.sort(key=lambda row: (row["condition"], row["family"], row["world_seed"], row["slot"]))
    worlds.sort(key=lambda row: (row["condition"], row["family"], row["world_seed"]))
    pq.write_table(_arrow_table(candidates), output_dir / "candidate_results.parquet", compression="zstd")
    pq.write_table(_arrow_table(worlds), output_dir / "world_results.parquet", compression="zstd")
    if self_traces:
        pq.write_table(_arrow_table(self_traces), output_dir / "llm_self_plans.parquet", compression="zstd")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in worlds:
        grouped[row["condition"]].append(row)
    summary_rows = [
        {
            "condition": condition,
            "worlds": len(rows),
            "jsr": sum(bool(row["condition_success"]) for row in rows) / len(rows),
            "compositional_jsr": sum(bool(row["compositional_success"]) for row in rows) / len(rows),
            "mean_tokens": sum(int(row["llm_tokens"]) for row in rows) / len(rows),
            "llm_calls": sum(int(row["llm_calls"]) for row in rows),
        }
        for condition, rows in sorted(grouped.items())
    ]
    pq.write_table(pa.Table.from_pylist(summary_rows), output_dir / "condition_summary.parquet", compression="zstd")
    summary = {
        "config": config,
        "model_manifest": asdict(_manifest(config)),
        "world_condition_rows": len(worlds),
        "candidate_rows": len(candidates),
        "conditions": summary_rows,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output_dir, args.base_url), indent=2))


if __name__ == "__main__":
    main()
