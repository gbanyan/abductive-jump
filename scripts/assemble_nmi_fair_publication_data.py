#!/usr/bin/env python3
"""Assemble paired and operational publication data after verified fair-interface replay."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from abductive_jump.fair_interface_publication import paired_row

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outcomes(path: Path, *, condition: str | None = None) -> dict[tuple[str, int], bool]:
    rows = pq.read_table(path).to_pylist()
    selected = [row for row in rows if condition is None or row["condition"] == condition]
    result = {
        (str(row["family"]), int(row["world_seed"])): bool(row["condition_success"])
        for row in selected
    }
    if len(result) != len(selected):
        raise ValueError(f"duplicate world keys in {path}")
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    fair_base = ROOT / "experiments" / "nmi_fair_interface_v1"
    fair_results = fair_base / "results" / "deepseek_fair_cself"
    fair_analysis = fair_base / "analysis"
    validation_path = fair_results / "validation.json"
    validation = json.loads(validation_path.read_text())
    if validation.get("status") != "complete_verified" or validation.get("replay_mismatches") != 0:
        raise ValueError("fair-interface publication assembly requires verified replay")

    panel = json.loads(
        (ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "panel_manifest.json").read_text()
    )
    amendment_001_path = fair_base / "protocol_amendment_001.json"
    amendment_002_path = fair_base / "protocol_amendment_002.json"
    amendment_001 = json.loads(amendment_001_path.read_text())
    amendment_002 = json.loads(amendment_002_path.read_text())
    panel_keys = {
        (str(row["family"]), int(row["world_seed"])) for row in panel["selected_worlds"]
    }
    source_paths = {
        "historical_phi4_4bit_cself": ROOT
        / "artifacts"
        / "compositional"
        / "confirmatory-existing"
        / "world_results.parquet",
        "deepseek_matched_cself": ROOT
        / "experiments"
        / "nmi_minimal_sensitivity_v1"
        / "results"
        / "deepseek_matched_cself"
        / "world_results.parquet",
        "deepseek_native_cself": ROOT
        / "experiments"
        / "nmi_minimal_sensitivity_v1"
        / "results"
        / "deepseek_native_cself"
        / "world_results.parquet",
        "deepseek_fair_interface_cself": fair_results / "world_results.parquet",
    }
    values = {
        "historical_phi4_4bit_cself": {
            key: value
            for key, value in outcomes(
                source_paths["historical_phi4_4bit_cself"],
                condition="C_SELF_LLM_COMPOSITION",
            ).items()
            if key in panel_keys
        },
        "deepseek_matched_cself": outcomes(source_paths["deepseek_matched_cself"]),
        "deepseek_native_cself": outcomes(source_paths["deepseek_native_cself"]),
        "deepseek_fair_interface_cself": outcomes(
            source_paths["deepseek_fair_interface_cself"]
        ),
    }
    if any(set(rows) != panel_keys for rows in values.values()):
        raise ValueError("one or more paired sources do not equal the frozen 96-world panel")
    paired = [
        paired_row(
            reference,
            values[reference],
            "deepseek_fair_interface_cself",
            values["deepseek_fair_interface_cself"],
        )
        for reference in (
            "historical_phi4_4bit_cself",
            "deepseek_matched_cself",
            "deepseek_native_cself",
        )
    ]
    write_csv(fair_analysis / "paired_world_differences.csv", paired)

    formal_transport_errors = {}
    for index in range(4):
        path = fair_base / "shards" / "results" / f"shard_{index}" / "llm_calls.jsonl.transport-errors"
        if path.is_file():
            formal_transport_errors[str(path.relative_to(ROOT))] = {
                "records": len(path.read_text().splitlines()),
                "sha256": digest(path),
            }
    report = {
        "schema_version": "nmi-fair-interface-publication-data-v1",
        "paired_world_differences": paired,
        "formal_transport_retry_logs": formal_transport_errors,
        "excluded_timeout_attempts": sum(
            int(row["records"]) for row in amendment_002["excluded_attempts"]["files"].values()
        ),
        "excluded_throughput_pilot_calls": int(
            amendment_001["pilot_exclusion"]["calls"]
        ),
        "model_calls_made": 0,
        "source_sha256": {
            str(path.relative_to(ROOT)): digest(path)
            for path in [
                *source_paths.values(),
                validation_path,
                amendment_001_path,
                amendment_002_path,
            ]
        },
    }
    (fair_analysis / "publication_manifest.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
