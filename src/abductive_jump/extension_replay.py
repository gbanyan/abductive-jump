from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .composition_search import SearchEvaluation, evaluate_candidate
from .compositional_experiment import _fit_for_condition, _parse_self_plans, _world
from .compositional_worlds import HELD_OUT_FAMILY
from .conditions import Condition, ProposalSource
from .executable import evaluate_executable, freeze_theory, parse_theory
from .external_reasoning_calibration import _prediction_table
from .generic_primitives import ComposedRepresentation
from .llm import extract_json_object
from .primary_experiment import _thresholds
from .proposals import apply_mutation_plan, select_external_proposals
from .realization import fit_representation
from .worlds import FAMILIES, generate_world


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _calls(path: Path) -> dict[tuple[str, str, str, int], dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    result: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row["condition"]),
            str(row["proposal_source"]),
            str(row["world_id"]),
            int(row["decoding_seed"]),
        )
        if key in result:
            raise ValueError(f"duplicate call key in {path}: {key}")
        result[key] = row
    return result


def _seed(config: dict[str, Any], condition: Condition, family: str, world_seed: int, slot: int) -> int:
    family_index = [*FAMILIES, HELD_OUT_FAMILY].index(family)
    return (
        int(config["decoding_seed_base"])
        + list(Condition).index(condition) * 10_000_000
        + family_index * 100_000
        + world_seed * 100
        + slot * 2
    )


def _compare(prefix: str, saved: dict[str, Any], actual: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    mismatches = []
    for field in fields:
        if field not in saved:
            mismatches.append(f"{prefix}:missing_saved_field:{field}")
        elif saved[field] != actual[field]:
            mismatches.append(f"{prefix}:{field}:{saved[field]!r}!={actual[field]!r}")
    return mismatches


def replay_compositional(config_path: Path, run_dir: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    saved_rows = [
        row
        for row in pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
        if row["condition"] == Condition.C_SELF_LLM_COMPOSITION.value
    ]
    calls = _calls(run_dir / "llm_calls.jsonl")
    condition = Condition.C_SELF_LLM_COMPOSITION
    reconstructed: dict[tuple[str, int], tuple[SearchEvaluation, list[dict[str, Any]]]] = {}
    output_rows: list[dict[str, Any]] = []
    mismatches: list[str] = []
    treatment_id = str(config.get("treatment_id", "historical_test"))
    for saved in saved_rows:
        world = _world(config, str(saved["family"]), int(saved["world_seed"]))
        slot = int(saved["slot"])
        key = (world.world_id, slot)
        initial_seed = _seed(config, condition, world.family, world.seed, slot)
        if key not in reconstructed:
            initial = calls[
                (
                    condition.value,
                    ProposalSource.LLM_COMPOSITION.value,
                    world.world_id,
                    initial_seed,
                )
            ]
            search_seed = int(config["search_seed_base"]) + world.seed * 101 + list(Condition).index(condition)
            evaluated, trace = _parse_self_plans(
                world,
                str(initial["full_output"]),
                search_seed + slot * 1000,
                required_plans=int(config["self_plans_per_slot"]),
            )
            if int(config.get("validator_repair_attempts", 0)) == 1 and len(evaluated) < int(
                config["self_plans_per_slot"]
            ):
                repaired = calls[
                    (
                        condition.value,
                        ProposalSource.LLM_COMPOSITION.value,
                        world.world_id,
                        initial_seed + 50_000_000,
                    )
                ]
                evaluated, trace = _parse_self_plans(
                    world,
                    str(repaired["full_output"]),
                    search_seed + slot * 1000,
                    required_plans=int(config["self_plans_per_slot"]),
                )
            selected = max(
                evaluated,
                key=lambda item: (item.score, item.candidate.representation.structural_hash),
                default=evaluate_candidate(
                    world.public(), ComposedRepresentation(world.incumbent, ())
                ),
            )
            reconstructed[key] = selected, trace
        selected, trace = reconstructed[key]
        representation = selected.candidate.representation
        expression, obs_loss, signature = _fit_for_condition(world, condition, representation)
        table = _prediction_table(world, expression)
        exact = max(
            table, key=lambda row: (float(row["absolute_separation"]), str(row["case_id"]))
        )["case_id"]
        prefix = f"{treatment_id}:{world.world_id}:{slot}"
        actual_structure = {
            "representation_hash": representation.structural_hash,
            "ancestry_depth": selected.candidate.depth,
            "mutation_ancestry": list(selected.candidate.operators),
            "structural_signature": signature,
            "exact_designer_intervention_id": exact,
        }
        mismatches.extend(
            _compare(
                prefix,
                saved,
                actual_structure,
                (
                    "representation_hash",
                    "ancestry_depth",
                    "mutation_ancestry",
                    "structural_signature",
                    "exact_designer_intervention_id",
                ),
            )
        )
        if abs(float(saved["observational_loss"]) - obs_loss) > 1e-10:
            mismatches.append(prefix + ":observational_loss")
        phase_two = calls[
            (
                condition.value,
                ProposalSource.COMPOSITION_SEARCH.value,
                world.world_id,
                initial_seed + 1,
            )
        ]
        replay_verified = False
        result_fields: dict[str, Any] = {}
        try:
            payload = extract_json_object(str(phase_two["full_output"]))
            payload["representation"] = representation.canonical_dict()
            payload["expression"] = expression.tree
            payload["selected_intervention_ids"] = [exact]
            theory = parse_theory(
                payload,
                {public: internal for internal, public in world.variable_names},
            )
            commitment = freeze_theory(world, theory)
            result = evaluate_executable(world, theory, commitment, _thresholds(config))
            result_fields = asdict(result)
            result_fields["validated_jump"] = result.validated_jump
            mismatches.extend(
                _compare(
                    prefix,
                    saved,
                    result_fields,
                    ("j0", "j1", "j2", "j3", "j4", "j5", "validated_jump"),
                )
            )
            replay_verified = True
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            if bool(saved["phase_two_valid"]):
                mismatches.append(prefix + f":phase_two:{type(exc).__name__}:{exc}")
        output_rows.append(
            {
                **saved,
                **result_fields,
                "treatment_id": treatment_id,
                "representation_json": representation.canonical_json(),
                "expression_json": expression.canonical_json,
                "replayed_final_plan_valid_count": sum(bool(row.get("valid")) for row in trace),
                "replay_verified": replay_verified,
            }
        )
    if mismatches:
        raise ValueError(f"compositional replay mismatches ({len(mismatches)}): {mismatches[:20]}")
    destination = run_dir / "replayed_candidates.parquet"
    pq.write_table(pa.Table.from_pylist(output_rows), destination, compression="zstd")
    return {
        "kind": "compositional",
        "treatment_id": str(config.get("treatment_id", "historical_test")),
        "config_sha256": _sha(config_path),
        "raw_calls_sha256": _sha(run_dir / "llm_calls.jsonl"),
        "candidate_rows": len(output_rows),
        "verified_rows": sum(bool(row["replay_verified"]) for row in output_rows),
        "mismatches": 0,
        "replayed_candidates_sha256": _sha(destination),
    }


def replay_factorial(config_path: Path, run_dir: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    saved_rows = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    calls = _calls(run_dir / "llm_calls.jsonl")
    output_rows: list[dict[str, Any]] = []
    mismatches: list[str] = []
    treatment_id = str(config.get("treatment_id", "historical_test"))
    for saved in saved_rows:
        condition = Condition(str(saved["condition"]))
        source = ProposalSource(str(saved["proposal_source"]))
        family = str(saved["family"])
        world_seed = int(saved["world_seed"])
        slot = int(saved["slot"])
        world = generate_world(family, world_seed, no_jump=bool(saved["no_jump"]))
        public = world.public()
        decoding_seed = _seed(config, condition, family, world_seed, slot)
        phase_one = calls[(condition.value, source.value, world.world_id, decoding_seed)]
        external = select_external_proposals(
            public,
            world_seed ^ 0x5151,
            int(config["candidate_slots"]),
            diverse=False,
        )
        if source is ProposalSource.P2_ORACLE:
            candidate = world.truth.representation
            ancestry: tuple[str, ...] = ()
        elif source is ProposalSource.P1_EXTERNAL:
            candidate = external[slot].representation
            ancestry = external[slot].operators
        else:
            candidate = None
            ancestry = ()
        fallback = False
        try:
            payload = extract_json_object(str(phase_one["full_output"]))
            if source is ProposalSource.P0_LLM:
                proposal = apply_mutation_plan(world.incumbent, payload["mutation_plan"], decoding_seed)
                candidate, ancestry = proposal.representation, proposal.operators
            if candidate is None or candidate.validate():
                raise ValueError("invalid replay candidate")
        except (KeyError, TypeError, ValueError, OverflowError):
            candidate, ancestry, fallback = world.incumbent, (), True
        try:
            fitted = fit_representation(public, candidate)
        except (KeyError, TypeError, ValueError, OverflowError):
            candidate, ancestry, fallback = world.incumbent, (), True
            fitted = fit_representation(public, candidate)
        table = _prediction_table(world, fitted.expression)
        exact = max(
            table, key=lambda row: (float(row["absolute_separation"]), str(row["case_id"]))
        )["case_id"]
        prefix = f"{treatment_id}:{source.value}:{world.world_id}:{slot}"
        actual_structure = {
            "fallback_to_incumbent": fallback,
            "representation_hash": candidate.structural_hash,
            "mutation_ancestry": list(ancestry),
            "exact_designer_intervention_id": exact,
        }
        mismatches.extend(
            _compare(
                prefix,
                saved,
                actual_structure,
                (
                    "fallback_to_incumbent",
                    "representation_hash",
                    "mutation_ancestry",
                    "exact_designer_intervention_id",
                ),
            )
        )
        if abs(float(saved["observational_loss"]) - fitted.observational_loss) > 1e-10:
            mismatches.append(prefix + ":observational_loss")
        phase_two = calls[(condition.value, source.value, world.world_id, decoding_seed + 1)]
        replay_verified = False
        result_fields: dict[str, Any] = {}
        try:
            payload = extract_json_object(str(phase_two["full_output"]))
            payload["representation"] = candidate.canonical_dict()
            payload["expression"] = fitted.expression.tree
            payload["selected_intervention_ids"] = [exact]
            theory = parse_theory(
                payload,
                {public_name: internal for internal, public_name in world.variable_names},
            )
            result = evaluate_executable(
                world, theory, freeze_theory(world, theory), _thresholds(config)
            )
            result_fields = asdict(result)
            result_fields["validated_jump"] = result.validated_jump
            mismatches.extend(
                _compare(
                    prefix,
                    saved,
                    result_fields,
                    ("j0", "j1", "j2", "j3", "j4", "j5", "validated_jump"),
                )
            )
            replay_verified = True
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            if bool(saved["phase_two_valid"]):
                mismatches.append(prefix + f":phase_two:{type(exc).__name__}:{exc}")
        output_rows.append(
            {
                **saved,
                **result_fields,
                "treatment_id": treatment_id,
                "representation_json": candidate.canonical_json(),
                "expression_json": fitted.expression.canonical_json,
                "replay_verified": replay_verified,
            }
        )
    if mismatches:
        raise ValueError(f"factorial replay mismatches ({len(mismatches)}): {mismatches[:20]}")
    destination = run_dir / "replayed_candidates.parquet"
    pq.write_table(pa.Table.from_pylist(output_rows), destination, compression="zstd")
    return {
        "kind": "factorial",
        "treatment_id": treatment_id,
        "config_sha256": _sha(config_path),
        "raw_calls_sha256": _sha(run_dir / "llm_calls.jsonl"),
        "candidate_rows": len(output_rows),
        "verified_rows": sum(bool(row["replay_verified"]) for row in output_rows),
        "mismatches": 0,
        "replayed_candidates_sha256": _sha(destination),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--kind", choices=("compositional", "factorial"), required=True)
    args = parser.parse_args()
    function = replay_compositional if args.kind == "compositional" else replay_factorial
    report = function(args.config, args.run_dir)
    path = args.run_dir / "replay_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
