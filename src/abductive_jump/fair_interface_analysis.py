"""Descriptive analysis for the single fixed-panel fair-interface sensitivity."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / total
    d = 1 + z * z / total
    c = (p + z * z / (2 * total)) / d
    r = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return c - r, c + r


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def cumulative(rows: list[dict[str, Any]], stages: tuple[str, ...], index: int) -> int:
    return sum(all(bool(row.get(stage)) for stage in stages[: index + 1]) for row in rows)


def run(root: Path) -> dict[str, Any]:
    base = root / "experiments" / "nmi_fair_interface_v1"
    run_dir = base / "results" / "deepseek_fair_cself"
    analysis_dir = base / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    validation = json.loads((run_dir / "validation.json").read_text())
    if validation["status"] != "complete_verified":
        raise ValueError("analysis locked until replay is complete_verified")
    worlds = pq.read_table(run_dir / "world_results.parquet").to_pylist()
    candidates = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    traces = pq.read_table(run_dir / "llm_self_plans.parquet").to_pylist()
    calls = [json.loads(line) for line in (run_dir / "llm_calls.jsonl").read_text().splitlines()]
    successes = sum(bool(row["condition_success"]) for row in worlds)
    low, high = wilson(successes, len(worlds))
    summary = {
        "condition": "deepseek_fair_interface_cself",
        "population": "fixed n=96 sensitivity panel",
        "successes": successes,
        "worlds": len(worlds),
        "jsr": successes / len(worlds),
        "wilson_95_low": low,
        "wilson_95_high": high,
    }
    per_family = []
    for family in sorted({str(row["family"]) for row in worlds}):
        subset = [row for row in worlds if row["family"] == family]
        count = sum(bool(row["condition_success"]) for row in subset)
        family_low, family_high = wilson(count, len(subset))
        per_family.append(
            {
                "family": family,
                "successes": count,
                "worlds": len(subset),
                "jsr": count / len(subset),
                "wilson_95_low": family_low,
                "wilson_95_high": family_high,
            }
        )
    trace_stages = (
        "deliberation_returned",
        "serialization_returned",
        "strict_whole_response_json",
        "json_parse_valid",
        "plan_schema_valid",
        "operation_names_valid",
        "argument_types_valid",
        "executable",
        "representation_constructed",
    )
    attrition = [
        {
            "unit": "plan_opportunity",
            "stage": stage,
            "passed": cumulative(traces, trace_stages, index),
            "denominator": len(traces),
            "rate": cumulative(traces, trace_stages, index) / len(traces),
        }
        for index, stage in enumerate(trace_stages)
    ]
    executable = [row for row in candidates if bool(row["proposal_executable"])]
    gates = ("j1", "j2", "j3", "j4", "j5")
    attrition.extend(
        {
            "unit": "executable_selected_candidate",
            "stage": stage.upper(),
            "passed": cumulative(executable, gates, index),
            "denominator": len(executable),
            "rate": cumulative(executable, gates, index) / len(executable) if executable else 0.0,
        }
        for index, stage in enumerate(gates)
    )
    stages = {
        "deliberation": [
            row for row in calls if row["prompt_template_version"].endswith("deliberation-v1")
        ],
        "serialization": [
            row for row in calls if row["prompt_template_version"].endswith("serialization-v1")
        ],
    }
    compute = []
    for stage, rows in stages.items():
        cap = 4096
        compute.append(
            {
                "stage": stage,
                "calls": len(rows),
                "prompt_tokens": sum(int(row["prompt_tokens"]) for row in rows),
                "completion_tokens": sum(int(row["completion_tokens"]) for row in rows),
                "answer_tokens": sum(int(row.get("answer_tokens") or 0) for row in rows),
                "reasoning_tokens_reported": sum(
                    int(row.get("reasoning_tokens") or 0) for row in rows
                ),
                "reasoning_text_calls": sum(bool(row.get("reasoning_output")) for row in rows),
                "cap_hits": sum(int(row["completion_tokens"]) == cap for row in rows),
                "latency_seconds": sum(float(row["latency_seconds"]) for row in rows),
                "finish_reasons": json.dumps(
                    Counter(str(row["finish_reason"]) for row in rows), sort_keys=True
                ),
            }
        )
    write_csv(analysis_dir / "world_summary.csv", [summary])
    write_csv(analysis_dir / "per_family.csv", per_family)
    write_csv(analysis_dir / "gate_attrition.csv", attrition)
    write_csv(analysis_dir / "compute_ledger.csv", compute)
    report = {
        "schema_version": "nmi-fair-interface-analysis-v1",
        "world_summary": summary,
        "per_family": per_family,
        "gate_attrition": attrition,
        "compute_ledger": compute,
        "model_calls_made": 0,
        "replay_mismatches": validation["replay_mismatches"],
    }
    (analysis_dir / "analysis.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    executable_count = sum(bool(row["executable"]) for row in traces)
    (analysis_dir / "report.md").write_text(
        "\n".join(
            [
                "# Fair-interface DeepSeek sensitivity",
                "",
                (
                    f"World-level JSR: {successes}/{len(worlds)} ({100 * summary['jsr']:.1f}%; "
                    f"Wilson 95% CI {100 * low:.1f}-{100 * high:.1f}%)."
                ),
                f"Executable plan opportunities: {executable_count}/{len(traces)}.",
                f"Executable selected candidates: {len(executable)}/{len(candidates)}.",
                f"Validated selected candidates: {sum(bool(row['validated_jump']) for row in candidates)}/{len(candidates)}.",
                "",
                (
                    "This condition guarantees grammar-level serialization and exact argument syntax only. "
                    "It supplies no semantic, fitted, intervention-outcome or gate feedback and does not support "
                    "a universal claim about language-model capability."
                ),
                "",
            ]
        )
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
