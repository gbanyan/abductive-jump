#!/usr/bin/env python3
"""Freeze four disjoint operational shards without changing scientific settings."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "nmi_fair_interface_v1"
CONFIG = BASE / "configs" / "deepseek_fair_cself.json"
PILOT = BASE / "operational_pilots" / "serial_runner_excluded" / "llm_calls.jsonl"
AMENDMENT = BASE / "protocol_amendment_001.json"


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    formal_results = BASE / "results"
    if formal_results.exists() and any(formal_results.iterdir()):
        raise ValueError("refusing to materialize shards after formal results exist")
    config = json.loads(CONFIG.read_text())
    families = list(config["families"])
    if len(families) != 8:
        raise ValueError("expected eight frozen families")
    shard_paths = []
    for index in range(4):
        shard = dict(config)
        shard["experiment_id"] = f"{config['experiment_id']}::operational-shard-{index}"
        shard["families"] = families[index * 2 : index * 2 + 2]
        path = BASE / "shards" / "configs" / f"shard_{index}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(canonical(shard))
        shard_paths.append(path)
    pilot_lines = PILOT.read_text().splitlines()
    amendment = {
        "schema_version": "nmi-fair-interface-operational-amendment-v1",
        "status": "frozen_before_formal_sharded_inference",
        "scientific_change": False,
        "reason": (
            "The serial operational pilot demonstrated severe client-side underutilization: four "
            "active requests used approximately 1.2% of available KV cache. Four disjoint family "
            "shards preserve per-run concurrency=4 while reducing idle wall time."
        ),
        "unchanged": [
            "96-world panel",
            "world seeds and decoding seeds",
            "model identity and revision",
            "reasoning and serialization budgets",
            "prompts and response schema",
            "primitive vocabulary and 48 opportunities per world",
            "candidate slots and J0-J5",
            "hidden-information boundaries",
        ],
        "pilot_exclusion": {
            "path": str(PILOT.parent.relative_to(ROOT)),
            "calls": len(pilot_lines),
            "call_log_sha256": digest(PILOT),
            "reason": "interrupted operational throughput probe; no result parquet or world summary was produced",
            "excluded_from_all_analysis": True,
        },
        "full_config": str(CONFIG.relative_to(ROOT)),
        "full_config_sha256": digest(CONFIG),
        "shards": {str(path.relative_to(ROOT)): digest(path) for path in shard_paths},
        "family_partition": [json.loads(path.read_text())["families"] for path in shard_paths],
        "expected_calls_after_merge": 576,
        "expected_unique_worlds_after_merge": 96,
        "generator": str(Path(__file__).relative_to(ROOT)),
        "generator_sha256": digest(Path(__file__)),
        "merge_script": "scripts/merge_nmi_fair_interface_shards.py",
        "merge_script_sha256": digest(ROOT / "scripts" / "merge_nmi_fair_interface_shards.py"),
    }
    AMENDMENT.write_text(canonical(amendment))
    print(canonical(amendment), end="")


if __name__ == "__main__":
    main()
