"""Analysis for the frozen minimal NMI sensitivity extension."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

CSSELF_RUNS = (
    "phi8_cself",
    "deepseek_matched_cself",
    "deepseek_native_cself",
    "phi8_cself_repair",
)
ALL_RUNS = (*CSSELF_RUNS, "deepseek_p2")


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("Wilson interval requires a positive denominator")
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    radius = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total))
        / denominator
    )
    return centre - radius, centre + radius


def paired_difference(
    reference: Iterable[dict[str, Any]], comparison: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    key = lambda row: (str(row["family"]), int(row["world_seed"]))
    left = {key(row): bool(row["condition_success"]) for row in reference}
    right = {key(row): bool(row["condition_success"]) for row in comparison}
    if left.keys() != right.keys():
        raise ValueError("paired conditions do not contain identical worlds")
    both_fail = both_succeed = gained = lost = 0
    for world, old in left.items():
        new = right[world]
        both_fail += not old and not new
        both_succeed += old and new
        gained += not old and new
        lost += old and not new
    total = len(left)
    return {
        "worlds": total,
        "both_fail": both_fail,
        "both_succeed": both_succeed,
        "comparison_only_success": gained,
        "reference_only_success": lost,
        "paired_jsr_difference": (gained - lost) / total,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path.name}")
    fields: list[str] = []
    for row in rows:
        fields.extend(key for key in row if key not in fields)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parquet_rows(path: Path) -> list[dict[str, Any]]:
    return pq.read_table(path).to_pylist()


def require_finalized(results_root: Path) -> dict[str, dict[str, Any]]:
    validations = {}
    for name in ALL_RUNS:
        path = results_root / name / "validation.json"
        if not path.is_file():
            raise ValueError(f"analysis locked: missing {path}")
        validation = json.loads(path.read_text())
        if validation.get("status") != "complete_verified":
            raise ValueError(f"analysis locked: {name} is not complete_verified")
        validations[name] = validation
    return validations


def condition_summary(label: str, rows: list[dict[str, Any]], population: str) -> dict[str, Any]:
    successes = sum(bool(row["condition_success"]) for row in rows)
    low, high = wilson_interval(successes, len(rows))
    return {
        "condition": label,
        "population": population,
        "successes": successes,
        "worlds": len(rows),
        "jsr": successes / len(rows),
        "wilson_95_low": low,
        "wilson_95_high": high,
    }


def effective_plan_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["world_id"]), int(row["slot"]))].append(row)
    effective = []
    for group in grouped.values():
        repair = [row for row in group if row.get("repair_stage") == "repair"]
        effective.extend(repair or [row for row in group if row.get("repair_stage", "initial") == "initial"])
    return effective


def cself_attrition(label: str, run_dir: Path) -> list[dict[str, Any]]:
    plan_rows = effective_plan_rows(parquet_rows(run_dir / "llm_self_plans.parquet"))
    candidate_rows = parquet_rows(run_dir / "candidate_results.parquet")
    stages = (
        "request_returned",
        "non_empty_answer",
        "json_parse_valid",
        "plan_schema_valid",
        "operation_names_valid",
        "argument_types_valid",
        "executable",
        "representation_constructed",
    )
    result = [
        {
            "condition": label,
            "unit": "effective_plan_opportunity",
            "stage": stage,
            "passed": sum(bool(row.get(stage)) for row in plan_rows),
            "denominator": len(plan_rows),
            "rate": sum(bool(row.get(stage)) for row in plan_rows) / len(plan_rows),
        }
        for stage in stages
    ]
    executable_slots = {
        (str(row["world_id"]), int(row["slot"]))
        for row in plan_rows
        if bool(row.get("executable"))
    }
    proposed_candidates = [
        row
        for row in candidate_rows
        if (str(row["world_id"]), int(row["slot"])) in executable_slots
    ]
    for stage in ("j1", "j2", "j3", "j4", "j5"):
        passed = sum(bool(row.get(stage)) for row in proposed_candidates)
        result.append(
            {
                "condition": label,
                "unit": "executable_self_proposed_candidate",
                "stage": stage.upper(),
                "passed": passed,
                "denominator": len(proposed_candidates),
                "rate": passed / len(proposed_candidates) if proposed_candidates else 0.0,
            }
        )
    return result


def call_ledger(label: str, path: Path) -> dict[str, Any]:
    calls = []
    with path.open(encoding="utf-8") as handle:
        calls = [json.loads(line) for line in handle]
    reasoning_counts = [row.get("reasoning_tokens") for row in calls]
    return {
        "condition": label,
        "llm_calls": len(calls),
        "transport_attempts": sum(int(row.get("attempt_count", 1)) for row in calls),
        "prompt_tokens": sum(int(row.get("prompt_tokens", 0)) for row in calls),
        "completion_tokens": sum(int(row.get("completion_tokens", 0)) for row in calls),
        "answer_tokens": sum(int(row.get("answer_tokens") or 0) for row in calls),
        "reasoning_tokens_reported": sum(int(value or 0) for value in reasoning_counts),
        "reasoning_token_count_available_calls": sum(value is not None for value in reasoning_counts),
        "reasoning_text_available_calls": sum(bool(row.get("reasoning_output")) for row in calls),
        "latency_seconds_sum": sum(float(row.get("latency_seconds", 0.0)) for row in calls),
        "finish_reasons": json.dumps(Counter(str(row.get("finish_reason", "")) for row in calls), sort_keys=True),
    }


def run(root: Path) -> dict[str, Any]:
    base = root / "experiments" / "nmi_minimal_sensitivity_v1"
    results_root = base / "results"
    validations = require_finalized(results_root)
    panel = json.loads((base / "panel_manifest.json").read_text())
    pairs = {(row["family"], int(row["world_seed"])) for row in panel["selected_worlds"]}

    historical = [
        row
        for row in parquet_rows(root / "artifacts/compositional/confirmatory-existing/world_results.parquet")
        if row["condition"] == "C_SELF_LLM_COMPOSITION"
        and (row["family"], int(row["world_seed"])) in pairs
    ]
    if len(historical) != 96:
        raise ValueError("historical paired panel must contain 96 worlds")
    conditions: dict[str, list[dict[str, Any]]] = {"historical_phi4_4bit_cself": historical}
    for name in CSSELF_RUNS:
        rows = parquet_rows(results_root / name / "world_results.parquet")
        if len(rows) != 96:
            raise ValueError(f"{name} must contain 96 worlds")
        conditions[name] = rows
    p2_rows = parquet_rows(results_root / "deepseek_p2" / "world_results.parquet")
    if len(p2_rows) != 40:
        raise ValueError("DeepSeek P2 must contain 40 worlds")
    conditions["deepseek_p2"] = p2_rows

    summaries = [
        condition_summary(
            name,
            rows,
            "original confirmatory n=400, fixed paired subset shown" if name.startswith("historical") else (
                "new balanced n=40 positive-control subset" if name == "deepseek_p2" else "new fixed n=96 sensitivity panel"
            ),
        )
        for name, rows in conditions.items()
    ]
    per_family = []
    for name, rows in conditions.items():
        families = sorted({str(row["family"]) for row in rows})
        for family in families:
            subset = [row for row in rows if row["family"] == family]
            summary = condition_summary(name, subset, "family-descriptive")
            summary["family"] = family
            per_family.append(summary)

    contrasts = (
        ("historical_phi4_4bit_cself", "phi8_cself"),
        ("historical_phi4_4bit_cself", "deepseek_matched_cself"),
        ("deepseek_matched_cself", "deepseek_native_cself"),
        ("phi8_cself", "phi8_cself_repair"),
    )
    paired = []
    for reference, comparison in contrasts:
        row = paired_difference(conditions[reference], conditions[comparison])
        row.update({"reference": reference, "comparison": comparison})
        paired.append(row)

    attrition = []
    offline = json.loads((base / "offline" / "historical_cself_attrition.json").read_text())
    attrition.extend(
        {"condition": "historical_phi4_4bit_cself", **row}
        for row in offline["response_cascade"]
    )
    for name in CSSELF_RUNS:
        attrition.extend(cself_attrition(name, results_root / name))
    ledgers = [call_ledger(name, results_root / name / "llm_calls.jsonl") for name in ALL_RUNS]

    analysis_dir = base / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    write_csv(analysis_dir / "world_summary.csv", summaries)
    write_csv(analysis_dir / "per_family.csv", per_family)
    write_csv(analysis_dir / "paired_world_differences.csv", paired)
    write_csv(analysis_dir / "gate_attrition.csv", attrition)
    write_csv(analysis_dir / "compute_ledger.csv", ledgers)
    report = {
        "analysis_scope": "minimal targeted sensitivity; world is the replicate",
        "candidate_level_significance_tests": False,
        "validations": validations,
        "world_summary": summaries,
        "paired_world_differences": paired,
        "gate_attrition": attrition,
        "compute_ledger": ledgers,
    }
    (analysis_dir / "analysis.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = run(args.root)
    print(json.dumps({"conditions": len(report["world_summary"])}, sort_keys=True))


if __name__ == "__main__":
    main()
