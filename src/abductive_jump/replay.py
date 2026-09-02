from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .conditions import Condition, ProposalSource
from .executable import evaluate_executable, freeze_theory, parse_theory
from .external_reasoning_calibration import _prediction_table
from .llm import extract_json_object
from .oracle import incumbent_oracle
from .primary_experiment import (
    _phase_one_representation,
    _thresholds,
)
from .proposals import apply_mutation_plan, select_external_proposals
from .realization import fit_representation
from .worlds import FAMILIES, generate_world, predict


def _calls(path: Path) -> dict[tuple[str, str, str, int], str]:
    calls: dict[tuple[str, str, str, int], str] = {}
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            key = (
                row["condition"],
                row["proposal_source"],
                row["world_id"],
                int(row["decoding_seed"]),
            )
            if key in calls:
                raise ValueError(f"duplicate replay key: {key}")
            calls[key] = row["full_output"]
    return calls


def _decoding_seed(config: dict[str, Any], condition: Condition, family: str, world_seed: int, slot: int) -> int:
    return (
        int(config["decoding_seed_base"])
        + list(Condition).index(condition) * 10_000_000
        + FAMILIES.index(family) * 100_000
        + world_seed * 100
        + slot * 2
    )


def replay_primary(
    config_path: Path, run_dir: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    config = json.loads(config_path.read_text())
    saved = pq.read_table(run_dir / "candidate_theories.parquet").to_pylist()
    calls = _calls(run_dir / "llm_calls.jsonl")
    theories: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for row in saved:
        condition = Condition(row["condition"])
        source = ProposalSource(row["proposal_source"])
        family = row["family"]
        world_seed = int(row["world_seed"])
        slot = int(row["slot"])
        world = generate_world(family, world_seed, no_jump=bool(row["no_jump"]))
        public = world.public()
        decoding_seed = _decoding_seed(config, condition, family, world_seed, slot)
        key = (condition.value, source.value, world.world_id, decoding_seed)
        external = select_external_proposals(
            public,
            world_seed ^ 0x5151,
            int(config["candidate_slots"]),
            diverse=condition is Condition.B5_FULL_SYSTEM,
        )
        candidate, ancestry, _ = _phase_one_representation(world, condition, slot, external)
        mutation_records: tuple[Any, ...] = (
            external[slot].ancestry
            if condition
            in {Condition.B4_REPRESENTATION_MUTATION, Condition.B5_FULL_SYSTEM}
            else ()
        )
        fallback = False
        try:
            phase_one = extract_json_object(calls[key])
            if condition is Condition.B0_DIRECT_LLM:
                candidate = parse_theory(
                    phase_one,
                    {public_name: internal for internal, public_name in world.variable_names},
                ).representation
            elif condition is Condition.B1_SAMPLE_MATCHED:
                proposal = apply_mutation_plan(world.incumbent, phase_one["mutation_plan"], decoding_seed)
                candidate, ancestry = proposal.representation, proposal.operators
                mutation_records = proposal.ancestry
            if candidate is None or candidate.validate():
                raise ValueError("invalid replay candidate")
        except (KeyError, TypeError, ValueError, OverflowError):
            candidate, ancestry, mutation_records, fallback = world.incumbent, (), (), True
        try:
            fitted = fit_representation(public, candidate)
        except (KeyError, TypeError, ValueError, OverflowError):
            candidate, ancestry, mutation_records, fallback = world.incumbent, (), (), True
            fitted = fit_representation(public, candidate)
        if fallback != bool(row["fallback_to_incumbent"]):
            mismatches.append(f"{condition}:{world.world_id}:{slot}:fallback")
        table = _prediction_table(world, fitted.expression)
        exact_choice = max(
            table,
            key=lambda item: (float(item["absolute_separation"]), str(item["case_id"])),
        )["case_id"]
        second_key = (condition.value, source.value, world.world_id, decoding_seed + 1)
        replayed = dict(row)
        replayed["representation_json"] = candidate.canonical_json()
        replayed["expression_json"] = fitted.expression.canonical_json
        replayed["mutation_ancestry"] = list(ancestry)
        replayed["replay_verified"] = False
        try:
            payload = extract_json_object(calls[second_key])
            payload["representation"] = candidate.canonical_dict()
            payload["expression"] = fitted.expression.tree
            payload["selected_intervention_ids"] = [exact_choice]
            theory = parse_theory(
                payload,
                {public_name: internal for internal, public_name in world.variable_names},
            )
            commitment = freeze_theory(world, theory)
            result = evaluate_executable(world, theory, commitment, _thresholds(config))
            for field in ("j0", "j1", "j2", "j3", "j4", "j5"):
                if bool(row.get(field)) != bool(getattr(result, field)):
                    mismatches.append(f"{condition}:{world.world_id}:{slot}:{field}")
            replayed["commitment_digest"] = commitment.digest
            replayed["theory_hash"] = theory.theory_hash
            replayed["replay_verified"] = True
            case = next(case for case in world.interventions if case.case_id == exact_choice)
            candidate_prediction = theory.expression.evaluate(
                dict(case.inputs), dict(case.intervention)
            )
            oracle_prediction = predict(
                incumbent_oracle(world).program,
                dict(case.inputs),
                dict(case.intervention),
            )
            predictions.append(
                {
                    "condition": condition.value,
                    "world_id": world.world_id,
                    "family": family,
                    "world_seed": world_seed,
                    "no_jump": world.no_jump,
                    "slot": slot,
                    "case_id": exact_choice,
                    "candidate_prediction": candidate_prediction,
                    "incumbent_oracle_prediction": oracle_prediction,
                    "revealed_outcome": case.outcome,
                    "absolute_separation": abs(candidate_prediction - oracle_prediction),
                    "commitment_digest": commitment.digest,
                }
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            if bool(row["phase_two_valid"]):
                mismatches.append(
                    f"{condition}:{world.world_id}:{slot}:phase_two:{type(exc).__name__}:{exc}"
                )
        theories.append(replayed)
        base_trace = {
            "condition": condition.value,
            "world_id": world.world_id,
            "world_seed": world_seed,
            "slot": slot,
            "candidate_hash": candidate.structural_hash,
            "fallback_to_incumbent": fallback,
        }
        if mutation_records:
            for record_index, record in enumerate(mutation_records):
                traces.append(
                    {
                        **base_trace,
                        "genome_level": "G_R",
                        "record_index": record_index,
                        "parent_hash": record.parent_hash,
                        "operator": record.operator.value,
                        "arguments_json": json.dumps(
                            dict(record.arguments), sort_keys=True, separators=(",", ":")
                        ),
                        "mutation_seed": record.seed,
                        "child_hash": record.child_hash,
                    }
                )
        else:
            marker = "NO_MUTATION"
            genome_level = "NONE"
            if condition is Condition.B0_DIRECT_LLM and not fallback:
                marker, genome_level = "LLM_DIRECT_GRAPH", "G_R"
            elif condition is Condition.B3_ATTRIBUTE_MUTATION:
                marker, genome_level = "WITHIN_SPACE_ATTRIBUTE_VARIANT", "G_H"
            traces.append(
                {
                    **base_trace,
                    "genome_level": genome_level,
                    "record_index": 0,
                    "parent_hash": world.incumbent.structural_hash,
                    "operator": marker,
                    "arguments_json": json.dumps(
                        {"slot": slot}, sort_keys=True, separators=(",", ":")
                    ),
                    "mutation_seed": decoding_seed,
                    "child_hash": candidate.structural_hash,
                }
            )
    if mismatches:
        raise ValueError(f"replay mismatches ({len(mismatches)}): {mismatches[:10]}")
    return theories, predictions, traces


def run(root: Path) -> dict[str, int]:
    all_theories: list[dict[str, Any]] = []
    all_predictions: list[dict[str, Any]] = []
    all_traces: list[dict[str, Any]] = []
    for config_name, run_name in (
        ("confirmatory-primary-jump.json", "primary-jump"),
        ("confirmatory-primary-control.json", "primary-control"),
    ):
        theories, predictions, traces = replay_primary(
            root / "configs" / config_name,
            root / "artifacts" / "confirmatory" / run_name,
        )
        all_theories.extend(theories)
        all_predictions.extend(predictions)
        all_traces.extend(traces)
    output = root / "artifacts"
    pq.write_table(pa.Table.from_pylist(all_theories), output / "candidate_theories.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pylist(all_predictions), output / "intervention_predictions.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pylist(all_traces), output / "mutation_trace.parquet", compression="zstd")
    summary = {
        "candidate_theories": len(all_theories),
        "intervention_predictions": len(all_predictions),
        "mutation_traces": len(all_traces),
        "verified_theories": sum(bool(row["replay_verified"]) for row in all_theories),
    }
    (output / "replay-validation.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2))


if __name__ == "__main__":
    main()
