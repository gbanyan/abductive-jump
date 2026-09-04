#!/usr/bin/env python3
"""Verify realizer-audit cardinality, hashes and derived summary tables."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "nmi_realizer_audit_v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    protocol = json.loads((BASE / "protocol.json").read_text())
    validation = json.loads((BASE / "results" / "validation.json").read_text())
    manifest = json.loads((BASE / "analysis" / "manifest.json").read_text())
    if validation["status"] != "complete_verified":
        raise ValueError("formal replay is not complete_verified")
    if not validation["zero_model_calls"]:
        raise ValueError("formal replay was not inference-free")
    if validation["aligned_replay_mismatch_count"] != 0:
        raise ValueError("aligned replay has mismatches")
    for name in ("candidate_results.parquet", "world_results.parquet", "summary.json"):
        key = name.removesuffix(".parquet").removesuffix(".json") + "_sha256"
        if digest(BASE / "results" / name) != validation[key]:
            raise ValueError(f"result digest mismatch: {name}")
    if digest(BASE / "results" / "validation.json") != manifest["source_validation_sha256"]:
        raise ValueError("analysis references a different validation artifact")
    for name, expected in manifest["outputs"].items():
        if digest(BASE / "analysis" / name) != expected:
            raise ValueError(f"analysis digest mismatch: {name}")

    candidates = pq.read_table(BASE / "results" / "candidate_results.parquet").to_pylist()
    worlds = pq.read_table(BASE / "results" / "world_results.parquet").to_pylist()
    if len(candidates) != protocol["candidate_policy_rows_expected"]:
        raise ValueError("candidate-policy cardinality mismatch")
    if len(worlds) != protocol["world_policy_rows_expected"]:
        raise ValueError("world-policy cardinality mismatch")
    if sorted({row["policy"] for row in worlds}) != sorted(protocol["policies"]):
        raise ValueError("policy set mismatch")

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in worlds:
        pop = (
            "fixed_known_panel"
            if row["source"] == "DeepSeek_grammar"
            else "heldout"
            if row["family"] == "triadic_relation_reification"
            else "known"
        )
        grouped[(str(row["source"]), pop, str(row["policy"]))].append(row)
    with (BASE / "analysis" / "condition_summary.csv").open(newline="") as handle:
        summaries = list(csv.DictReader(handle))
    for row in summaries:
        key = (row["source"], row["population"], row["policy"])
        selected = grouped[key]
        successes = sum(bool(item["successful"]) for item in selected)
        if int(row["worlds"]) != len(selected) or int(row["successes"]) != successes:
            raise ValueError(f"summary mismatch: {key}")

    required = {
        ("C3", "known", "aligned"): (400, 400),
        ("C3", "heldout", "aligned"): (100, 100),
        ("C3", "known", "motif_disabled"): (0, 400),
        ("C3", "heldout", "motif_disabled"): (0, 100),
        ("C_rand", "known", "aligned"): (52, 400),
        ("C_rand", "heldout", "aligned"): (13, 100),
        ("DeepSeek_grammar", "fixed_known_panel", "aligned"): (15, 96),
        ("DeepSeek_grammar", "fixed_known_panel", "motif_disabled"): (0, 96),
    }
    observed = {
        (row["source"], row["population"], row["policy"]): (
            int(row["successes"]),
            int(row["worlds"]),
        )
        for row in summaries
    }
    for key, value in required.items():
        if observed.get(key) != value:
            raise ValueError(f"required result mismatch: {key}")
    print(
        json.dumps(
            {
                "status": "complete_verified",
                "zero_model_calls": True,
                "aligned_replay_mismatches": 0,
                "candidate_policy_rows": len(candidates),
                "world_policy_rows": len(worlds),
                "required_headline_counts_verified": len(required),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
