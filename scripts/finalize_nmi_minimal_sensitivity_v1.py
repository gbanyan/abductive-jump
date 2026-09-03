"""Fail-closed integrity finalizer for one minimal-sensitivity shard."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_calls(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def finalize(config_path: Path, run_dir: Path, kind: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    expected_worlds = len(config["families"]) * len(config["world_seeds"])
    expected_candidates = expected_worlds * int(config["candidate_slots"])
    required = (
        ("candidate_results.parquet", "world_results.parquet", "summary.json", "llm_calls.jsonl")
        if kind == "p2"
        else (
            "candidate_results.parquet",
            "world_results.parquet",
            "condition_summary.parquet",
            "llm_self_plans.parquet",
            "summary.json",
            "llm_calls.jsonl",
        )
    )
    for name in required:
        require((run_dir / name).is_file(), f"missing artifact: {name}")

    candidates = pq.read_table(run_dir / "candidate_results.parquet")
    worlds = pq.read_table(run_dir / "world_results.parquet")
    calls = read_calls(run_dir / "llm_calls.jsonl")
    require(candidates.num_rows == expected_candidates, "candidate row count mismatch")
    require(worlds.num_rows == expected_worlds, "world row count mismatch")
    require(set(worlds["world_seed"].to_pylist()) == set(config["world_seeds"]), "world seeds mismatch")
    require(set(worlds["family"].to_pylist()) == set(config["families"]), "families mismatch")
    require(all(row.get("model") == config["model"] for row in calls), "model alias mismatch")
    require(all(row.get("revision") == config["revision"] for row in calls), "revision mismatch")
    require(all(row.get("quantization") == config["quantization"] for row in calls), "quantization mismatch")
    require(all(int(row.get("attempt_count", 0)) >= 1 for row in calls), "invalid transport attempt count")
    keys = [
        (
            row.get("condition"),
            row.get("proposal_source"),
            row.get("world_id"),
            row.get("decoding_seed"),
            row.get("prompt_template_version"),
        )
        for row in calls
    ]
    require(len(keys) == len(set(keys)), "duplicate logical LLM call keys")

    if kind == "p2":
        require(len(calls) == expected_candidates, "P2 call count mismatch")
        require(config["calls_per_world"] == int(config["candidate_slots"]), "P2 call budget mismatch")
    else:
        plans = pq.read_table(run_dir / "llm_self_plans.parquet")
        base_calls = expected_candidates * 2
        repairs = int(config.get("validator_repair_attempts", 0))
        if repairs == 0:
            require(len(calls) == base_calls, "C_self no-repair call count mismatch")
            require(plans.num_rows == expected_candidates * int(config["self_plans_per_slot"]), "C_self plan row count mismatch")
        else:
            require(repairs == 1, "only one repair attempt is permitted")
            require(base_calls <= len(calls) <= base_calls + expected_candidates, "repair call count out of range")
            minimum_plans = expected_candidates * int(config["self_plans_per_slot"])
            require(minimum_plans <= plans.num_rows <= minimum_plans * 2, "repair trace row count out of range")

    transport_errors = sorted(run_dir.glob("*.transport-errors"))
    require(not transport_errors, "transport error sentinel present")
    artifacts = {
        path.name: digest(path)
        for path in sorted(run_dir.iterdir())
        if path.is_file()
        and path.name not in {"validation.json", "run.stdout.log", "run.stderr.log"}
    }
    return {
        "status": "complete_verified",
        "kind": kind,
        "experiment_id": config["extension_experiment_id"],
        "worlds": expected_worlds,
        "candidate_rows": expected_candidates,
        "llm_calls": len(calls),
        "transport_error_sentinels": 0,
        "artifact_sha256": artifacts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--kind", choices=("cself", "p2"), required=True)
    args = parser.parse_args()
    print(json.dumps(finalize(args.config, args.run_dir, args.kind), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
