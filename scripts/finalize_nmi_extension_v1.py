#!/usr/bin/env python3
"""Verify completeness and hash every NMI extension v1 raw result shard."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "experiments" / "nmi_extension_v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def verify_shard(config_path: Path, run_dir: Path) -> dict[str, Any]:
    config = load(config_path)
    factorial = run_dir.name.startswith("factorial_")
    families = len(config["families"])
    seeds = (
        int(config["world_seed_range"]["stop_exclusive"])
        - int(config["world_seed_range"]["start"])
        if factorial
        else len(config["world_seeds"])
    )
    sources = len(config["proposal_sources"]) if factorial else 1
    expected_world_rows = families * seeds * sources
    expected_candidate_rows = expected_world_rows * int(config["candidate_slots"])
    worlds = pq.read_table(run_dir / "world_results.parquet").to_pylist()
    candidates = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    calls = _lines(run_dir / "llm_calls.jsonl")
    assert len(worlds) == expected_world_rows, (run_dir, "world rows")
    assert len(candidates) == expected_candidate_rows, (run_dir, "candidate rows")
    if factorial:
        assert len(calls) == expected_candidate_rows * 2, (run_dir, "calls")
    else:
        phase_one = [
            row
            for row in calls
            if row["proposal_source"] == "LLM_COMPOSITION"
        ]
        phase_two = [
            row
            for row in calls
            if row["proposal_source"] == "COMPOSITION_SEARCH"
        ]
        assert len(phase_two) == expected_candidate_rows, (run_dir, "phase-two calls")
        repairs = len(phase_one) - expected_candidate_rows
        assert 0 <= repairs <= expected_candidate_rows, (run_dir, "repair calls")
        if int(config.get("validator_repair_attempts", 0)) == 0:
            assert repairs == 0, (run_dir, "unexpected repair")
        traces = pq.read_table(run_dir / "llm_self_plans.parquet").to_pylist()
        assert len(traces) == len(phase_one) * int(config["self_plans_per_slot"]), (
            run_dir,
            "plan traces",
        )
    call_keys = {
        (
            row["condition"],
            row["proposal_source"],
            row["world_id"],
            int(row["decoding_seed"]),
        )
        for row in calls
    }
    assert len(call_keys) == len(calls), (run_dir, "duplicate calls")
    expected_seeds = (
        set(range(int(config["world_seed_range"]["start"]), int(config["world_seed_range"]["stop_exclusive"])))
        if factorial
        else {int(seed) for seed in config["world_seeds"]}
    )
    assert {int(row["world_seed"]) for row in worlds} == expected_seeds
    error_path = run_dir / "llm_calls.jsonl.transport-errors"
    artifacts = {
        str(path.relative_to(ROOT)): sha(path)
        for path in sorted(run_dir.iterdir())
        if path.is_file()
    }
    return {
        "experiment_id": config["extension_experiment_id"],
        "treatment_id": config["treatment_id"],
        "config": str(config_path.relative_to(ROOT)),
        "config_sha256": sha(config_path),
        "run_dir": str(run_dir.relative_to(ROOT)),
        "world_rows": len(worlds),
        "candidate_rows": len(candidates),
        "llm_calls": len(calls),
        "transport_error_records": len(error_path.read_text().splitlines()) if error_path.is_file() else 0,
        "artifacts": artifacts,
        "status": "complete_verified",
    }


def main() -> None:
    config_manifest = load(EXT / "configs" / "config_manifest.json")
    shards = []
    missing = []
    for relative, expected_hash in sorted(config_manifest["configs"].items()):
        config_path = ROOT / relative
        assert sha(config_path) == expected_hash, config_path
        config = load(config_path)
        run_dir = EXT / "results" / config["treatment_id"] / config_path.stem
        if not (run_dir / "summary.json").is_file():
            missing.append(str(run_dir.relative_to(ROOT)))
            continue
        shards.append(verify_shard(config_path, run_dir))
    if missing:
        raise RuntimeError(f"missing {len(missing)} result shards: {missing}")
    manifest = {
        "schema_version": "nmi-extension-result-manifest-v1",
        "protocol_freeze_commit": "4606413539c908171293f2a47f834fd4d7f8fe30",
        "protocol_amendment_commit": "4ebc679b6dfdec053dc77fe6dd68caa78a2cb4da",
        "shards": shards,
        "shard_count": len(shards),
        "status": "all_raw_shards_complete_and_verified",
    }
    destination = EXT / "result_manifest.json"
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": manifest["status"], "shards": len(shards)}, sort_keys=True))


if __name__ == "__main__":
    main()
