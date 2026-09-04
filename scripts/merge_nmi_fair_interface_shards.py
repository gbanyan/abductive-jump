#!/usr/bin/env python3
"""Merge and cardinality-check the four frozen fair-interface operational shards."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]


def arrow_table(rows: list[dict[str, Any]]) -> pa.Table:
    columns = sorted({key for row in rows for key in row})
    return pa.Table.from_pylist([{key: row.get(key) for key in columns} for row in rows])


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        type=Path,
        default=ROOT / "experiments" / "nmi_fair_interface_v1",
    )
    args = parser.parse_args()
    base = args.base
    amendment_path = base / "protocol_amendment_001.json"
    amendment = json.loads(amendment_path.read_text())
    if amendment["status"] != "frozen_before_formal_sharded_inference":
        raise ValueError("operational amendment is not frozen")
    if digest(ROOT / amendment["generator"]) != amendment["generator_sha256"]:
        raise ValueError("shard generator differs from frozen amendment")
    if digest(ROOT / amendment["merge_script"]) != amendment["merge_script_sha256"]:
        raise ValueError("merge script differs from frozen amendment")
    for relative, expected in amendment["shards"].items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"shard config differs from frozen amendment: {relative}")

    candidates: list[dict[str, Any]] = []
    worlds: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for index in range(4):
        run_dir = base / "shards" / "results" / f"shard_{index}"
        candidates.extend(pq.read_table(run_dir / "candidate_results.parquet").to_pylist())
        worlds.extend(pq.read_table(run_dir / "world_results.parquet").to_pylist())
        traces.extend(pq.read_table(run_dir / "llm_self_plans.parquet").to_pylist())
        calls.extend(
            json.loads(line) for line in (run_dir / "llm_calls.jsonl").read_text().splitlines()
        )
    world_keys = [(row["family"], int(row["world_seed"]), row["world_id"]) for row in worlds]
    candidate_keys = [
        (row["family"], int(row["world_seed"]), row["world_id"], int(row["slot"]))
        for row in candidates
    ]
    call_keys = [(row["world_id"], int(row["decoding_seed"])) for row in calls]
    if len(world_keys) != 96 or len(set(world_keys)) != 96:
        raise ValueError("merged worlds are duplicate or incomplete")
    if len(candidate_keys) != 288 or len(set(candidate_keys)) != 288:
        raise ValueError("merged candidates are duplicate or incomplete")
    if (
        len(call_keys) != amendment["expected_calls_after_merge"]
        or len(set(call_keys)) != amendment["expected_calls_after_merge"]
    ):
        raise ValueError("merged calls are duplicate or incomplete")
    if len(traces) != 4608:
        raise ValueError("merged plan opportunities are incomplete")

    candidates.sort(key=lambda row: (row["family"], row["world_seed"], row["slot"]))
    worlds.sort(key=lambda row: (row["family"], row["world_seed"]))
    traces.sort(key=lambda row: (row["family"], row["world_seed"], row["slot"], row["plan_index"]))
    calls.sort(key=lambda row: (row["world_id"], row["decoding_seed"]))
    output = base / "results" / "deepseek_fair_cself"
    if output.exists() and any(output.iterdir()):
        raise ValueError("refusing to overwrite merged results")
    output.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        arrow_table(candidates), output / "candidate_results.parquet", compression="zstd"
    )
    pq.write_table(arrow_table(worlds), output / "world_results.parquet", compression="zstd")
    pq.write_table(arrow_table(traces), output / "llm_self_plans.parquet", compression="zstd")
    with (output / "llm_calls.jsonl").open("w", encoding="utf-8") as handle:
        for row in calls:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    config_path = base / "configs" / "deepseek_fair_cself.json"
    successes = sum(bool(row["condition_success"]) for row in worlds)
    summary = {
        "config_sha256": digest(config_path),
        "worlds": len(worlds),
        "candidate_slots": len(candidates),
        "plan_opportunities": len(traces),
        "llm_calls": len(calls),
        "successes": successes,
        "jsr": successes / len(worlds),
        "executable_plan_opportunities": sum(bool(row["executable"]) for row in traces),
        "executable_slots": sum(bool(row["proposal_executable"]) for row in candidates),
        "validated_candidates": sum(bool(row["validated_jump"]) for row in candidates),
        "operational_amendment_sha256": digest(amendment_path),
        "formal_shards": 4,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
