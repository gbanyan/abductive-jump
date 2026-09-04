#!/usr/bin/env python3
"""Analyze the verified NMI realizer-dependence counterfactual replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    spread = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, centre - spread), min(1.0, centre + spread)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def population(row: dict[str, Any]) -> str:
    if row["source"] == "DeepSeek_grammar":
        return "fixed_known_panel"
    return "heldout" if row["family"] == "triadic_relation_reification" else "known"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        default=ROOT / "experiments" / "nmi_realizer_audit_v1",
    )
    args = parser.parse_args()
    base = args.experiment_dir
    results = base / "results"
    analysis = base / "analysis"
    if analysis.exists() and any(analysis.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty analysis directory: {analysis}")
    validation = json.loads((results / "validation.json").read_text())
    if validation["status"] != "complete_verified" or not validation["zero_model_calls"]:
        raise ValueError("realizer replay is not complete_verified and inference-free")
    for name in ("candidate_results.parquet", "world_results.parquet", "summary.json"):
        key = name.removesuffix(".parquet").removesuffix(".json") + "_sha256"
        if digest(results / name) != validation[key]:
            raise ValueError(f"result hash mismatch: {name}")

    candidates = pq.read_table(results / "candidate_results.parquet").to_pylist()
    worlds = pq.read_table(results / "world_results.parquet").to_pylist()
    for row in candidates:
        row["population"] = population(row)
    for row in worlds:
        row["population"] = population(row)

    summary_rows = []
    summary_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in worlds:
        summary_groups[(row["source"], row["population"], row["policy"])].append(row)
    for (source, pop, policy), rows in sorted(summary_groups.items()):
        successes = sum(bool(row["successful"]) for row in rows)
        low, high = wilson(successes, len(rows))
        summary_rows.append(
            {
                "source": source,
                "population": pop,
                "policy": policy,
                "worlds": len(rows),
                "successes": successes,
                "jsr": successes / len(rows),
                "wilson_95_low": low,
                "wilson_95_high": high,
            }
        )
    write_csv(analysis / "condition_summary.csv", summary_rows)

    family_rows = []
    family_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in worlds:
        family_groups[(row["source"], row["policy"], row["family"])].append(row)
    for (source, policy, family), rows in sorted(family_groups.items()):
        successes = sum(bool(row["successful"]) for row in rows)
        low, high = wilson(successes, len(rows))
        family_rows.append(
            {
                "source": source,
                "policy": policy,
                "family": family,
                "worlds": len(rows),
                "successes": successes,
                "jsr": successes / len(rows),
                "wilson_95_low": low,
                "wilson_95_high": high,
            }
        )
    write_csv(analysis / "per_family.csv", family_rows)

    by_world = {
        (row["source"], row["policy"], row["family"], int(row["world_seed"])): bool(
            row["successful"]
        )
        for row in worlds
    }
    policies = sorted({str(row["policy"]) for row in worlds if row["policy"] != "aligned"})
    transition_rows = []
    for source in sorted({str(row["source"]) for row in worlds}):
        keys = sorted(
            {
                (str(row["family"]), int(row["world_seed"]))
                for row in worlds
                if row["source"] == source and row["policy"] == "aligned"
            }
        )
        for policy in policies:
            cells = [
                (by_world[(source, "aligned", *key)], by_world[(source, policy, *key)])
                for key in keys
            ]
            transition_rows.append(
                {
                    "source": source,
                    "comparison": f"aligned_vs_{policy}",
                    "worlds": len(cells),
                    "both_fail": sum(not a and not b for a, b in cells),
                    "aligned_only": sum(a and not b for a, b in cells),
                    "counterfactual_only": sum(not a and b for a, b in cells),
                    "both_pass": sum(a and b for a, b in cells),
                    "paired_jsr_difference": sum(int(b) - int(a) for a, b in cells) / len(cells),
                }
            )
    write_csv(analysis / "paired_transitions.csv", transition_rows)

    gate_rows = []
    gates = ("j0", "j1", "j2", "j3", "j4", "j5")
    candidate_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        candidate_groups[(row["source"], row["policy"])].append(row)
    for (source, policy), rows in sorted(candidate_groups.items()):
        cumulative = [True] * len(rows)
        for gate in gates:
            cumulative = [
                prior and bool(row[gate]) for prior, row in zip(cumulative, rows, strict=True)
            ]
            passed = sum(cumulative)
            gate_rows.append(
                {
                    "source": source,
                    "policy": policy,
                    "unit": "archived_candidate_slot",
                    "stage": gate.upper(),
                    "passed": passed,
                    "denominator": len(rows),
                    "rate": passed / len(rows),
                }
            )
    write_csv(analysis / "gate_attrition.csv", gate_rows)

    signature_rows = []
    aligned_candidates = [row for row in candidates if row["policy"] == "aligned"]
    for source in sorted({str(row["source"]) for row in aligned_candidates}):
        source_rows = [row for row in aligned_candidates if row["source"] == source]
        for signature in sorted({str(row["detected_signature"]) for row in source_rows}):
            rows = [row for row in source_rows if row["detected_signature"] == signature]
            validated = sum(bool(row["counterfactual_validated_jump"]) for row in rows)
            signature_rows.append(
                {
                    "source": source,
                    "detected_signature": signature,
                    "candidate_slots": len(rows),
                    "aligned_validated_candidates": validated,
                    "aligned_validated_worlds": len(
                        {
                            (row["family"], int(row["world_seed"]))
                            for row in rows
                            if row["counterfactual_validated_jump"]
                        }
                    ),
                }
            )
    write_csv(analysis / "signature_distribution.csv", signature_rows)

    def find(source: str, pop: str, policy: str) -> dict[str, Any]:
        return next(
            row
            for row in summary_rows
            if row["source"] == source and row["population"] == pop and row["policy"] == policy
        )

    c3_known = find("C3", "known", "aligned")
    c3_held = find("C3", "heldout", "aligned")
    c3_disabled_known = find("C3", "known", "motif_disabled")
    c3_disabled_held = find("C3", "heldout", "motif_disabled")
    c3_blind_known = find("C3", "known", "role_action_blind_binding")
    c3_blind_held = find("C3", "heldout", "role_action_blind_binding")
    ds_aligned = find("DeepSeek_grammar", "fixed_known_panel", "aligned")
    ds_disabled = find("DeepSeek_grammar", "fixed_known_panel", "motif_disabled")
    ds_blind = find("DeepSeek_grammar", "fixed_known_panel", "role_action_blind_binding")
    crand_known = find("C_rand", "known", "aligned")
    crand_held = find("C_rand", "heldout", "aligned")
    crand_disabled_known = find("C_rand", "known", "motif_disabled")
    crand_disabled_held = find("C_rand", "heldout", "motif_disabled")
    crand_blind_known = find("C_rand", "known", "role_action_blind_binding")
    crand_blind_held = find("C_rand", "heldout", "role_action_blind_binding")

    report = f"""# NMI realizer-dependence audit v1

## Status

Complete and validation-verified. The aligned policy reproduced every archived candidate gate and world verdict with zero mismatches. This analysis replayed fixed archived candidates and made zero model calls.

## Primary causal result

Disabling motif realization reduced C3 from {c3_known["successes"]}/{c3_known["worlds"]} known-family and {c3_held["successes"]}/{c3_held["worlds"]} held-out worlds to {c3_disabled_known["successes"]}/{c3_disabled_known["worlds"]} and {c3_disabled_held["successes"]}/{c3_disabled_held["worlds"]}. C_rand fell from {crand_known["successes"]}/{crand_known["worlds"]} and {crand_held["successes"]}/{crand_held["worlds"]} to {crand_disabled_known["successes"]}/{crand_disabled_known["worlds"]} and {crand_disabled_held["successes"]}/{crand_disabled_held["worlds"]}. Grammar-constrained DeepSeek fell from {ds_aligned["successes"]}/{ds_aligned["worlds"]} to {ds_disabled["successes"]}/{ds_disabled["worlds"]}.

The fixed motif-to-basis semantic library is therefore necessary for every archived validated escape under this counterfactual. This identifies a scaffold dependency; it does not show whether a model internally conceptualized a useful representation.

## Role/action-blind binding

Retaining each motif's algebraic term shape but replacing role- and intervention-aware field selection with type-compatible lexical binding retained {c3_blind_known["successes"]}/{c3_blind_known["worlds"]} known-family and {c3_blind_held["successes"]}/{c3_blind_held["worlds"]} held-out C3 successes. It retained {ds_blind["successes"]}/{ds_blind["worlds"]} grammar-constrained DeepSeek successes. C_rand changed from {crand_known["successes"]}/{crand_known["worlds"]} and {crand_held["successes"]}/{crand_held["worlds"]} to {crand_blind_known["successes"]}/{crand_blind_known["worlds"]} and {crand_blind_held["successes"]}/{crand_blind_held["worlds"]}.

Thus the algebraic motif library, rather than role-aware binding alone, accounts for the universal dependency. Role/action information contributes to a subset of worlds, especially the model-proposed panel, but the blind policy is not a no-information realizer: it preserves the motif's algebraic form and refits coefficients on public observations.

## Interpretation boundary

This is a post-confirmatory causal sensitivity, not a replacement confirmation. It fixes candidate representations selected under the aligned historical pipeline; it does not rerun search or model generation under each counterfactual. Exact counts, Wilson intervals, paired transitions, gate attrition and per-family results are in the accompanying CSV files. Candidate rows are attrition units, not independent replicates.
"""
    analysis.mkdir(parents=True, exist_ok=True)
    (analysis / "report.md").write_text(report)
    manifest = {
        "schema_version": "nmi-realizer-audit-analysis-v1",
        "source_validation_sha256": digest(results / "validation.json"),
        "outputs": {
            path.name: digest(path) for path in sorted(analysis.iterdir()) if path.is_file()
        },
    }
    (analysis / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(report)


if __name__ == "__main__":
    main()
