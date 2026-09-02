from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .compositional_experiment import _parse_self_plans, _world
from .conditions import Condition


def run(config_path: Path, run_dir: Path) -> dict[str, object]:
    config = json.loads(config_path.read_text())
    candidates = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    worlds = pq.read_table(run_dir / "world_results.parquet").to_pylist()
    calls = [json.loads(line) for line in (run_dir / "llm_calls.jsonl").read_text().splitlines()]
    expected_worlds = len(config["families"]) * len(config["world_seeds"]) * len(config["conditions"])
    expected_candidates = expected_worlds * int(config["candidate_slots"])
    expected_calls = expected_candidates * 2
    if len(worlds) != expected_worlds or len(candidates) != expected_candidates or len(calls) != expected_calls:
        raise ValueError(
            f"row invariant failed: worlds={len(worlds)}/{expected_worlds}, "
            f"candidates={len(candidates)}/{expected_candidates}, calls={len(calls)}/{expected_calls}"
        )
    call_keys = {
        (row["condition"], row["world_id"], int(row["decoding_seed"])) for row in calls
    }
    if len(call_keys) != len(calls):
        raise ValueError("duplicate call key")

    family_by_world = {row["world_id"]: row["family"] for row in worlds}
    self_calls = [
        row
        for row in calls
        if row["prompt_template_version"] == "generic-self-composition-v1"
    ]
    self_calls.sort(key=lambda row: (row["world_id"], int(row["decoding_seed"])))
    traces = []
    for call in self_calls:
        family = family_by_world[call["world_id"]]
        world = _world(config, family, int(call["world_seed"]))
        slot = sum(
            1
            for previous in self_calls
            if previous["world_id"] == call["world_id"]
            and int(previous["decoding_seed"]) < int(call["decoding_seed"])
        )
        _, rows = _parse_self_plans(
            world,
            call["full_output"],
            int(config["search_seed_base"])
            + int(call["world_seed"]) * 101
            + list(Condition).index(Condition.C_SELF_LLM_COMPOSITION)
            + slot * 1000,
            required_plans=int(config["self_plans_per_slot"]),
        )
        traces.extend(
            {
                "world_id": world.world_id,
                "family": family,
                "world_seed": world.seed,
                "slot": slot,
                **row,
            }
            for row in rows
        )
    expected_self_traces = (
        len(config["families"])
        * len(config["world_seeds"])
        * int(config["candidate_slots"])
        * int(config["self_plans_per_slot"])
    )
    if len(traces) != expected_self_traces:
        raise ValueError(f"self trace invariant failed: {len(traces)}/{expected_self_traces}")
    pq.write_table(
        pa.Table.from_pylist(traces),
        run_dir / "llm_self_plans.parquet",
        compression="zstd",
    )

    primary = {
        "C0_FIXED_SPACE",
        "C2_GENERIC_DEPTH_1",
        "C3_GENERIC_COMPOSITION",
        "C_SELF_LLM_COMPOSITION",
        "C_RAND_RANDOM_PRIMITIVES",
    }
    budget_mismatches = [
        row
        for row in worlds
        if row["condition"] in primary
        and (
            int(row["primitive_operation_capacity"]) != int(config["primitive_operation_budget"])
            or int(row["candidate_evaluations"]) != int(config["primitive_operation_budget"])
            or int(row["llm_calls"]) != int(config["candidate_slots"]) * 2
        )
    ]
    if budget_mismatches:
        raise ValueError(f"primary budget mismatches: {len(budget_mismatches)}")
    c2_jumps = sum(
        bool(row["condition_success"])
        for row in worlds
        if row["condition"] == "C2_GENERIC_DEPTH_1"
    )
    summary: dict[str, object] = {
        "world_condition_rows": len(worlds),
        "candidate_rows": len(candidates),
        "llm_calls": len(calls),
        "unique_call_keys": len(call_keys),
        "self_plan_opportunities": len(traces),
        "self_valid_plans": sum(bool(row["valid"]) for row in traces),
        "primary_budget_mismatches": len(budget_mismatches),
        "c2_depth_one_successes": c2_jumps,
        "audit_passed": not budget_mismatches and c2_jumps == 0,
    }
    (run_dir / "run_audit.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.run_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
