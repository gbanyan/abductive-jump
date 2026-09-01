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

from .budget import EqualBudgetContract
from .conditions import Condition, ProposalSource, build_prompt
from .executable import evaluate_executable, freeze_theory, parse_theory
from .external_reasoning_calibration import _manifest, _prediction_table
from .gates import GateThresholds
from .llm import OpenAICompatibleClient, extract_json_object
from .proposals import apply_mutation_plan, select_external_proposals
from .realization import fit_representation
from .representation import Node, NodeKind, Representation, structural_descriptor
from .worlds import FAMILIES, World, generate_world


def _arrow_table(rows: list[dict[str, Any]]) -> pa.Table:
    columns = sorted({key for row in rows for key in row})
    return pa.Table.from_pylist([{key: row.get(key) for key in columns} for row in rows])


def _attribute_variant(incumbent: Representation, slot: int) -> Representation:
    equations = [node for node in incumbent.nodes if node.kind is NodeKind.EQUATION]
    if not equations:
        return incumbent
    target = equations[slot % len(equations)]
    replacement = Node(
        target.id,
        target.kind,
        {**target.attributes, "hypothesis_value_variant": str(slot - 1)},
    )
    return incumbent.replace_node(target.id, attributes=replacement.attributes)


def _thresholds(config: dict[str, Any]) -> GateThresholds:
    values = config["gate_thresholds"]
    return GateThresholds(
        epsilon_obs=float(values["epsilon_obs"]),
        epsilon_candidate_obs=float(values["epsilon_candidate_obs"]),
        min_prediction_separation=float(values["min_prediction_separation"]),
        delta_cf=float(values["delta_cf"]),
        epsilon_falsification=float(values["epsilon_falsification"]),
        delta_falsification=float(values["delta_falsification"]),
    )


def _world_seeds(config: dict[str, Any]) -> tuple[int, ...]:
    if "world_seeds" in config:
        return tuple(int(seed) for seed in config["world_seeds"])
    values = config["world_seed_range"]
    seeds = tuple(range(int(values["start"]), int(values["stop_exclusive"])))
    if not seeds:
        raise ValueError("world seed range must be non-empty")
    return seeds


def _phase_one_representation(
    world: World,
    condition: Condition,
    slot: int,
    external: tuple[Any, ...],
) -> tuple[Representation | None, tuple[str, ...], ProposalSource]:
    if condition in {Condition.B2_FIXED_SPACE_AGENT, Condition.B3_ATTRIBUTE_MUTATION}:
        representation = (
            world.incumbent
            if condition is Condition.B2_FIXED_SPACE_AGENT
            else _attribute_variant(world.incumbent, slot)
        )
        return representation, (), ProposalSource.P0_LLM
    if condition in {Condition.B4_REPRESENTATION_MUTATION, Condition.B5_FULL_SYSTEM}:
        proposal = external[slot]
        return proposal.representation, proposal.operators, ProposalSource.P1_EXTERNAL
    return None, (), ProposalSource.P0_LLM


def _run_slot(
    *,
    config: dict[str, Any],
    condition: Condition,
    family: str,
    world_seed: int,
    slot: int,
    base_url: str,
    log_path: Path,
    source_override: ProposalSource | None = None,
) -> dict[str, Any]:
    world = generate_world(family, world_seed, no_jump=bool(config.get("no_jump", False)))
    public = world.public()
    slots = int(config["candidate_slots"])
    external = select_external_proposals(
        public,
        world_seed ^ 0x5151,
        slots,
        diverse=condition is Condition.B5_FULL_SYSTEM,
    )
    if source_override is ProposalSource.P2_ORACLE:
        supplied, ancestry, source = world.truth.representation, (), source_override
    else:
        supplied, ancestry, source = _phase_one_representation(
            world, condition, slot, external
        )
        source = source_override or source
    manifest_config = dict(config)
    generation = dict(config["generation"])
    if condition is Condition.B1_SAMPLE_MATCHED:
        generation["temperature"] = float(config["sample_temperature"])
    manifest_config["generation"] = generation
    client = OpenAICompatibleClient(base_url, _manifest(manifest_config), log_path)
    condition_index = list(Condition).index(condition)
    decoding_seed = (
        int(config["decoding_seed_base"])
        + condition_index * 10_000_000
        + FAMILIES.index(family) * 100_000
        + world_seed * 100
        + slot * 2
    )
    row: dict[str, Any] = {
        "condition": condition.value,
        "proposal_source": source.value,
        "family": family,
        "world_id": world.world_id,
        "world_seed": world_seed,
        "no_jump": world.no_jump,
        "slot": slot,
        "phase_one_valid": False,
        "phase_two_valid": False,
        "fallback_to_incumbent": False,
        "validated_jump": False,
    }
    phase_one_prompt = build_prompt(public, condition, source, supplied)
    phase_one_output, phase_one_call = client.generate(
        phase_one_prompt,
        world_id=world.world_id,
        world_seed=world_seed,
        decoding_seed=decoding_seed,
        candidate_parent=world.incumbent.structural_hash,
        mutation_ancestry=ancestry,
        representation_hash=supplied.structural_hash if supplied else "",
    )
    row["phase_one_tokens"] = phase_one_call.completion_tokens
    row["phase_one_latency_seconds"] = phase_one_call.latency_seconds
    row["phase_one_prompt_hash"] = phase_one_call.prompt_hash
    candidate_representation = supplied
    try:
        phase_one_payload = extract_json_object(phase_one_output)
        if condition is Condition.B0_DIRECT_LLM:
            candidate_representation = parse_theory(
                phase_one_payload,
                {public_name: internal for internal, public_name in world.variable_names},
            ).representation
        elif condition is Condition.B1_SAMPLE_MATCHED:
            proposal = apply_mutation_plan(
                world.incumbent, phase_one_payload["mutation_plan"], decoding_seed
            )
            candidate_representation = proposal.representation
            ancestry = proposal.operators
        if candidate_representation is None:
            raise ValueError("phase one did not produce a representation")
        representation_errors = candidate_representation.validate()
        if representation_errors:
            raise ValueError("invalid phase-one graph: " + "; ".join(representation_errors))
        row["phase_one_valid"] = True
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        row["phase_one_error_type"] = type(exc).__name__
        row["phase_one_error"] = str(exc)
        candidate_representation = world.incumbent
        ancestry = ()
        row["fallback_to_incumbent"] = True

    assert candidate_representation is not None
    try:
        fitted = fit_representation(public, candidate_representation)
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        row["realization_error_type"] = type(exc).__name__
        row["realization_error"] = str(exc)
        candidate_representation = world.incumbent
        fitted = fit_representation(public, candidate_representation)
        ancestry = ()
        row["fallback_to_incumbent"] = True
    table = _prediction_table(world, fitted.expression)
    exact_choice = max(
        table,
        key=lambda item: (float(item["absolute_separation"]), str(item["case_id"])),
    )["case_id"]
    phase_two_prompt = build_prompt(
        public,
        condition,
        source,
        candidate_representation,
        fitted.expression,
        fitted.observational_loss,
        table,
    )
    phase_two_output, phase_two_call = client.generate(
        phase_two_prompt,
        world_id=world.world_id,
        world_seed=world_seed,
        decoding_seed=decoding_seed + 1,
        candidate_parent=world.incumbent.structural_hash,
        mutation_ancestry=ancestry,
        representation_hash=candidate_representation.structural_hash,
    )
    row["phase_two_tokens"] = phase_two_call.completion_tokens
    row["phase_two_latency_seconds"] = phase_two_call.latency_seconds
    row["phase_two_prompt_hash"] = phase_two_call.prompt_hash
    row["representation_hash"] = candidate_representation.structural_hash
    row["mutation_ancestry"] = list(ancestry)
    row["structural_descriptor"] = json.dumps(
        structural_descriptor(candidate_representation), separators=(",", ":")
    )
    row["observational_loss"] = fitted.observational_loss
    row["exact_designer_intervention_id"] = exact_choice
    try:
        payload = extract_json_object(phase_two_output)
        row["model_selected_intervention_ids"] = json.dumps(
            payload.get("selected_intervention_ids", []), separators=(",", ":")
        )
        payload["representation"] = candidate_representation.canonical_dict()
        payload["expression"] = fitted.expression.tree
        payload["selected_intervention_ids"] = [exact_choice]
        theory = parse_theory(
            payload,
            {public_name: internal for internal, public_name in world.variable_names},
        )
        row["phase_two_valid"] = True
        result = evaluate_executable(
            world, theory, freeze_theory(world, theory), _thresholds(config)
        )
        row.update(asdict(result))
        row["validated_jump"] = result.validated_jump
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        row["phase_two_error_type"] = type(exc).__name__
        row["phase_two_error"] = str(exc)
    return row


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    conditions = tuple(Condition(value) for value in config["conditions"])
    slots = int(config["candidate_slots"])
    contract = EqualBudgetContract(
        slots, 2, int(config["generation"]["max_tokens"])
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        {
            "config": config,
            "condition": condition,
            "family": family,
            "world_seed": seed,
            "slot": slot,
            "base_url": base_url,
            "log_path": output_dir / "llm_calls.jsonl",
        }
        for condition in conditions
        for family in config["families"]
        for seed in _world_seeds(config)
        for slot in range(slots)
    ]
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=int(config.get("concurrency", 1))) as executor:
        futures = [executor.submit(_run_slot, **job) for job in jobs]
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: (row["condition"], row["family"], row["world_seed"], row["slot"]))
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["condition"], row["world_id"])].append(row)
    world_rows: list[dict[str, Any]] = []
    for (condition, world_id), candidates in sorted(grouped.items()):
        used_tokens = sum(
            int(row.get("phase_one_tokens", 0)) + int(row.get("phase_two_tokens", 0))
            for row in candidates
        )
        world_rows.append(
            {
                "condition": condition,
                "world_id": world_id,
                "family": candidates[0]["family"],
                "world_seed": candidates[0]["world_seed"],
                "no_jump": candidates[0]["no_jump"],
                "condition_success": any(row["validated_jump"] for row in candidates),
                "accepted_candidates": sum(row["validated_jump"] for row in candidates),
                "proposal_valid_candidates": sum(row["phase_one_valid"] for row in candidates),
                "reasoning_valid_candidates": sum(row["phase_two_valid"] for row in candidates),
                "archive_occupancy": len({row["structural_descriptor"] for row in candidates}),
                "llm_tokens_used": used_tokens,
                "llm_calls_used": len(candidates) * 2,
                "candidate_evaluations_used": len(candidates),
                "interventions_used": len(candidates),
                "budget_limit": json.dumps(contract.canonical_dict(), sort_keys=True),
            }
        )
    pq.write_table(_arrow_table(rows), output_dir / "candidate_theories.parquet", compression="zstd")
    pq.write_table(_arrow_table(world_rows), output_dir / "world_condition_results.parquet", compression="zstd")
    summaries = []
    for condition in conditions:
        selected = [row for row in world_rows if row["condition"] == condition.value]
        jumps = [row for row in selected if not row["no_jump"]]
        controls = [row for row in selected if row["no_jump"]]
        summaries.append(
            {
                "condition": condition.value,
                "worlds": len(selected),
                "jsr": sum(row["condition_success"] for row in jumps) / len(jumps) if jumps else None,
                "fjr": sum(row["condition_success"] for row in controls) / len(controls) if controls else None,
                "mean_tokens": sum(row["llm_tokens_used"] for row in selected) / len(selected),
                "mean_archive_occupancy": sum(row["archive_occupancy"] for row in selected) / len(selected),
            }
        )
    pq.write_table(pa.Table.from_pylist(summaries), output_dir / "condition_summary.parquet", compression="zstd")
    summary = {
        "model_manifest": asdict(_manifest(config)),
        "budget_contract": contract.canonical_dict(),
        "conditions": summaries,
        "candidate_rows": len(rows),
        "world_condition_rows": len(world_rows),
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
