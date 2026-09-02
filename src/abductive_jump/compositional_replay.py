from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .composition_search import SearchEvaluation, evaluate_candidate
from .compositional_experiment import (
    _condition_candidates,
    _fit_for_condition,
    _parse_self_plans,
    _world,
)
from .compositional_worlds import HELD_OUT_FAMILY
from .conditions import Condition
from .executable import evaluate_executable, freeze_theory, parse_theory
from .external_reasoning_calibration import _arrow_table, _prediction_table
from .generic_primitives import ComposedRepresentation
from .llm import extract_json_object
from .primary_experiment import _thresholds
from .proposals import select_external_proposals
from .worlds import FAMILIES

RUNS = (
    ("compositional-confirmatory-existing.json", "confirmatory-existing"),
    ("compositional-confirmatory-existing-control.json", "confirmatory-existing-control"),
    ("compositional-confirmatory-heldout.json", "confirmatory-heldout"),
    ("compositional-confirmatory-heldout-control.json", "confirmatory-heldout-control"),
)


def _calls(path: Path) -> dict[tuple[str, str, int], dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    lookup = {
        (str(row["condition"]), str(row["world_id"]), int(row["decoding_seed"])): row
        for row in rows
    }
    if len(lookup) != len(rows):
        raise ValueError(f"duplicate calls in {path}")
    return lookup


def _seed(config: dict[str, Any], condition: Condition, family: str, world_seed: int, slot: int) -> int:
    family_index = [*FAMILIES, HELD_OUT_FAMILY].index(family)
    return (
        int(config["decoding_seed_base"])
        + list(Condition).index(condition) * 10_000_000
        + family_index * 100_000
        + world_seed * 100
        + slot * 2
    )


def _reconstruct_candidates(
    config: dict[str, Any], world: Any, condition: Condition, calls: dict[Any, Any]
) -> tuple[list[SearchEvaluation], list[tuple[Any, ...]]]:
    slots = int(config["candidate_slots"])
    search_seed = (
        int(config["search_seed_base"])
        + world.seed * 101
        + list(Condition).index(condition)
    )
    if condition is Condition.C_SELF_LLM_COMPOSITION:
        candidates = []
        records = []
        for slot in range(slots):
            call = calls[(condition.value, world.world_id, _seed(config, condition, world.family, world.seed, slot))]
            evaluated, _ = _parse_self_plans(
                world,
                call["full_output"],
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
            candidates.append(selected)
            records.append(selected.candidate.ancestry)
        return candidates, records
    candidates, _ = _condition_candidates(world, condition, search_seed, slots, config)
    if condition is Condition.C1_ATOMIC_HIGH_LEVEL:
        proposals = select_external_proposals(world.public(), search_seed, slots, diverse=False)
        return candidates, [proposal.ancestry for proposal in proposals]
    return candidates, [candidate.candidate.ancestry for candidate in candidates]


def replay_run(
    config_path: Path, run_dir: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    config = json.loads(config_path.read_text())
    saved = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    calls = _calls(run_dir / "llm_calls.jsonl")
    by_cell: dict[tuple[str, str], tuple[list[SearchEvaluation], list[tuple[Any, ...]]]] = {}
    enriched = []
    ancestry_rows = []
    mismatches: list[str] = []
    for row in saved:
        condition = Condition(row["condition"])
        world = _world(config, row["family"], int(row["world_seed"]))
        key = (condition.value, world.world_id)
        if key not in by_cell:
            by_cell[key] = _reconstruct_candidates(config, world, condition, calls)
        candidates, record_sets = by_cell[key]
        slot = int(row["slot"])
        candidate = candidates[slot]
        records = record_sets[slot]
        representation = candidate.candidate.representation
        expression, observational_loss, signature = _fit_for_condition(
            world, condition, representation
        )
        table = _prediction_table(world, expression)
        exact = max(
            table,
            key=lambda item: (float(item["absolute_separation"]), str(item["case_id"])),
        )["case_id"]
        prefix = f"{condition.value}:{world.world_id}:{slot}"
        if representation.structural_hash != row["representation_hash"]:
            mismatches.append(prefix + ":representation_hash")
        if (
            list(candidate.candidate.operators) != list(row["mutation_ancestry"])
            and condition is not Condition.C1_ATOMIC_HIGH_LEVEL
        ):
            # C1 records legacy ancestry only in its separate atomic-reference trace.
            mismatches.append(prefix + ":ancestry")
        if int(row["ancestry_depth"]) != candidate.candidate.depth:
            mismatches.append(prefix + ":depth")
        if signature != row["structural_signature"]:
            mismatches.append(prefix + ":signature")
        if abs(float(row["observational_loss"]) - observational_loss) > 1e-10:
            mismatches.append(prefix + ":observational_loss")
        if str(row["exact_designer_intervention_id"]) != exact:
            mismatches.append(prefix + ":intervention")

        replayed = dict(row)
        replayed["representation_json"] = representation.canonical_json()
        replayed["expression_json"] = expression.canonical_json
        replayed["replay_verified"] = False
        phase_two_seed = _seed(config, condition, world.family, world.seed, slot) + 1
        phase_two = calls[(condition.value, world.world_id, phase_two_seed)]
        try:
            payload = extract_json_object(phase_two["full_output"])
            payload["representation"] = representation.canonical_dict()
            payload["expression"] = expression.tree
            payload["selected_intervention_ids"] = [exact]
            theory = parse_theory(
                payload,
                {public: internal for internal, public in world.variable_names},
            )
            result = evaluate_executable(
                world, theory, freeze_theory(world, theory), _thresholds(config)
            )
            for field in ("j0", "j1", "j2", "j3", "j4", "j5", "validated_jump"):
                actual = result.validated_jump if field == "validated_jump" else getattr(result, field)
                if bool(row[field]) != bool(actual):
                    mismatches.append(prefix + ":" + field)
            replayed.update(asdict(result))
            replayed["validated_jump"] = result.validated_jump
            replayed["replay_verified"] = True
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            if bool(row["phase_two_valid"]):
                mismatches.append(prefix + f":phase_two:{type(exc).__name__}:{exc}")
        enriched.append(replayed)

        if records:
            for index, record in enumerate(records):
                ancestry_rows.append(
                    {
                        "condition": condition.value,
                        "family": world.family,
                        "world_id": world.world_id,
                        "world_seed": world.seed,
                        "no_jump": world.no_jump,
                        "slot": slot,
                        "record_index": index,
                        "depth": getattr(record, "depth", index + 1),
                        "parent_hash": record.parent_hash,
                        "child_hash": record.child_hash,
                        "operator": record.operator.value,
                        "arguments_json": json.dumps(
                            dict(record.arguments), sort_keys=True, separators=(",", ":")
                        ),
                        "mutation_seed": record.seed,
                        "candidate_hash": representation.structural_hash,
                        "legacy_atomic_reference": condition is Condition.C1_ATOMIC_HIGH_LEVEL,
                    }
                )
        else:
            ancestry_rows.append(
                {
                    "condition": condition.value,
                    "family": world.family,
                    "world_id": world.world_id,
                    "world_seed": world.seed,
                    "no_jump": world.no_jump,
                    "slot": slot,
                    "record_index": 0,
                    "depth": 0,
                    "parent_hash": world.incumbent.structural_hash,
                    "child_hash": representation.structural_hash,
                    "operator": "NO_GENERIC_ANCESTRY",
                    "arguments_json": "{}",
                    "mutation_seed": 0,
                    "candidate_hash": representation.structural_hash,
                    "legacy_atomic_reference": condition is Condition.C1_ATOMIC_HIGH_LEVEL,
                }
            )
    return enriched, ancestry_rows, mismatches


def run(root: Path) -> dict[str, Any]:
    candidates = []
    ancestry = []
    mismatches = []
    for config_name, run_name in RUNS:
        run_dir = root / "artifacts" / "compositional" / run_name
        enriched, traces, errors = replay_run(
            root / "configs" / config_name, run_dir
        )
        candidates.extend(enriched)
        ancestry.extend(traces)
        mismatches.extend(errors)
    if mismatches:
        raise ValueError(f"compositional replay mismatches ({len(mismatches)}): {mismatches[:20]}")
    candidates.sort(
        key=lambda row: (row["condition"], row["family"], row["world_seed"], row["slot"])
    )
    ancestry.sort(
        key=lambda row: (
            row["condition"],
            row["family"],
            row["world_seed"],
            row["slot"],
            row["record_index"],
        )
    )
    output = root / "artifacts"
    pq.write_table(
        _arrow_table(candidates),
        output / "compositional_candidates.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(ancestry),
        output / "composition_ancestry.parquet",
        compression="zstd",
    )
    summary = {
        "candidate_rows": len(candidates),
        "verified_candidates": sum(bool(row["replay_verified"]) for row in candidates),
        "ancestry_rows": len(ancestry),
        "mismatches": len(mismatches),
    }
    (output / "compositional-replay-validation.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
