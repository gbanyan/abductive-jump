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

from .phi_budget_integration import budget_run_dir, require_phi_budget_finalized

CSSELF_RUNS = (
    "phi8_cself",
    "deepseek_matched_cself",
    "deepseek_native_cself",
    "phi8_cself_repair",
)
ALL_RUNS = (*CSSELF_RUNS, "deepseek_p2")


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
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


def cumulative_pass_count(
    rows: Iterable[dict[str, Any]], stages: tuple[str, ...], stage_index: int
) -> int:
    required = stages[: stage_index + 1]
    return sum(all(bool(row.get(stage)) for stage in required) for row in rows)


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
        effective.extend(
            repair or [row for row in group if row.get("repair_stage", "initial") == "initial"]
        )
    return effective


def cself_attrition(
    label: str,
    run_dir: Path,
    pairs: set[tuple[str, int]] | None = None,
) -> list[dict[str, Any]]:
    plan_rows = effective_plan_rows(parquet_rows(run_dir / "llm_self_plans.parquet"))
    candidate_rows = parquet_rows(run_dir / "candidate_results.parquet")
    if pairs is not None:
        candidate_rows = [
            row for row in candidate_rows if (str(row["family"]), int(row["world_seed"])) in pairs
        ]
        # Historical Phi-budget plan ledgers predate the sensitivity schema and
        # identify worlds by world_id, not world_seed.  Candidate rows retain
        # both identifiers, so use their selected world IDs as the join key.
        selected_world_ids = {str(row["world_id"]) for row in candidate_rows}
        plan_rows = [row for row in plan_rows if str(row["world_id"]) in selected_world_ids]
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
    result = []
    for index, stage in enumerate(stages):
        passed = cumulative_pass_count(plan_rows, stages, index)
        result.append(
            {
                "condition": label,
                "unit": "effective_plan_opportunity",
                "stage": stage,
                "passed": passed,
                "denominator": len(plan_rows),
                "rate": passed / len(plan_rows),
            }
        )
    executable_slots = {
        (str(row["world_id"]), int(row["slot"])) for row in plan_rows if bool(row.get("executable"))
    }
    proposed_candidates = [
        row
        for row in candidate_rows
        if (str(row["world_id"]), int(row["slot"])) in executable_slots
    ]
    gates = ("j1", "j2", "j3", "j4", "j5")
    for index, stage in enumerate(gates):
        passed = cumulative_pass_count(proposed_candidates, gates, index)
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


def p2_attrition(run_dir: Path) -> list[dict[str, Any]]:
    rows = parquet_rows(run_dir / "candidate_results.parquet")
    stages = ("parse_valid", "executable", "j1", "j2", "j3", "j4", "j5")
    result = []
    for index, stage in enumerate(stages):
        passed = cumulative_pass_count(rows, stages, index)
        result.append(
            {
                "condition": "deepseek_p2",
                "unit": "model_authored_expression_and_intervention_candidate",
                "stage": stage.upper() if stage.startswith("j") else stage,
                "passed": passed,
                "denominator": len(rows),
                "rate": passed / len(rows),
            }
        )
    return result


def call_ledger(label: str, path: Path, world_ids: set[str] | None = None) -> dict[str, Any]:
    calls = []
    with path.open(encoding="utf-8") as handle:
        calls = [json.loads(line) for line in handle]
    if world_ids is not None:
        calls = [row for row in calls if str(row["world_id"]) in world_ids]
    reasoning_counts = [row.get("reasoning_tokens") for row in calls]
    return {
        "condition": label,
        "llm_calls": len(calls),
        "transport_attempts": sum(int(row.get("attempt_count", 1)) for row in calls),
        "prompt_tokens": sum(int(row.get("prompt_tokens", 0)) for row in calls),
        "completion_tokens": sum(int(row.get("completion_tokens", 0)) for row in calls),
        "answer_tokens": sum(int(row.get("answer_tokens") or 0) for row in calls),
        "reasoning_tokens_reported": sum(int(value or 0) for value in reasoning_counts),
        "reasoning_token_count_available_calls": sum(
            value is not None for value in reasoning_counts
        ),
        "reasoning_text_available_calls": sum(bool(row.get("reasoning_output")) for row in calls),
        "latency_seconds_sum": sum(float(row.get("latency_seconds", 0.0)) for row in calls),
        "finish_reasons": json.dumps(
            Counter(str(row.get("finish_reason", "")) for row in calls), sort_keys=True
        ),
    }


def run(root: Path) -> dict[str, Any]:
    base = root / "experiments" / "nmi_minimal_sensitivity_v1"
    results_root = base / "results"
    validations = require_finalized(results_root)
    budget_validations = require_phi_budget_finalized(root)
    panel = json.loads((base / "panel_manifest.json").read_text())
    pairs = {(row["family"], int(row["world_seed"])) for row in panel["selected_worlds"]}

    historical_full = [
        row
        for row in parquet_rows(
            root / "artifacts/compositional/confirmatory-existing/world_results.parquet"
        )
        if row["condition"] == "C_SELF_LLM_COMPOSITION"
    ]
    historical = [
        row for row in historical_full if (row["family"], int(row["world_seed"])) in pairs
    ]
    if len(historical) != 96:
        raise ValueError("historical paired panel must contain 96 worlds")
    budget_known_full = parquet_rows(budget_run_dir(root, "known_jump") / "world_results.parquet")
    budget_panel = [
        row for row in budget_known_full if (str(row["family"]), int(row["world_seed"])) in pairs
    ]
    if len(budget_known_full) != 400 or len(budget_panel) != 96:
        raise ValueError(
            "Phi budget known-family result must contain 400 worlds and the exact 96-world panel"
        )
    conditions: dict[str, list[dict[str, Any]]] = {
        "historical_phi4_4bit_cself": historical,
        "phi4_4bit_budget_cself": budget_panel,
    }
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
            "original confirmatory n=400, fixed paired subset shown"
            if name.startswith("historical")
            else (
                "previously frozen n=400 budget sensitivity, fixed paired subset shown"
                if name == "phi4_4bit_budget_cself"
                else "new balanced n=40 positive-control subset"
                if name == "deepseek_p2"
                else "new fixed n=96 sensitivity panel"
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
        ("historical_phi4_4bit_cself", "phi4_4bit_budget_cself"),
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
        {"condition": "historical_phi4_4bit_cself", **row} for row in offline["response_cascade"]
    )
    for name in CSSELF_RUNS:
        attrition.extend(cself_attrition(name, results_root / name))
    attrition.extend(
        cself_attrition(
            "phi4_4bit_budget_cself",
            budget_run_dir(root, "known_jump"),
            pairs,
        )
    )
    attrition.extend(p2_attrition(results_root / "deepseek_p2"))
    ledgers = [call_ledger(name, results_root / name / "llm_calls.jsonl") for name in ALL_RUNS]
    budget_panel_world_ids = {str(row["world_id"]) for row in budget_panel}
    ledgers.append(
        call_ledger(
            "phi4_4bit_budget_cself",
            budget_run_dir(root, "known_jump") / "llm_calls.jsonl",
            budget_panel_world_ids,
        )
    )

    historical_heldout = [
        row
        for row in parquet_rows(
            root / "artifacts/compositional/confirmatory-heldout/world_results.parquet"
        )
        if row["condition"] == "C_SELF_LLM_COMPOSITION"
    ]
    budget_heldout = parquet_rows(budget_run_dir(root, "heldout_jump") / "world_results.parquet")
    if len(historical_full) != 400 or len(historical_heldout) != 100 or len(budget_heldout) != 100:
        raise ValueError("full Phi budget comparison populations have unexpected cardinality")
    budget_summaries = [
        condition_summary(
            "historical_phi4_4bit_cself_full", historical_full, "original confirmatory n=400"
        ),
        condition_summary(
            "phi4_4bit_budget_cself_full", budget_known_full, "budget sensitivity n=400"
        ),
        condition_summary(
            "historical_phi4_4bit_cself_heldout", historical_heldout, "original held-out n=100"
        ),
        condition_summary(
            "phi4_4bit_budget_cself_heldout", budget_heldout, "budget sensitivity held-out n=100"
        ),
    ]
    budget_paired = []
    for reference_name, comparison_name, reference_rows, comparison_rows in (
        (
            "historical_phi4_4bit_cself_full",
            "phi4_4bit_budget_cself_full",
            historical_full,
            budget_known_full,
        ),
        (
            "historical_phi4_4bit_cself_heldout",
            "phi4_4bit_budget_cself_heldout",
            historical_heldout,
            budget_heldout,
        ),
    ):
        row = paired_difference(reference_rows, comparison_rows)
        row.update({"reference": reference_name, "comparison": comparison_name})
        budget_paired.append(row)
    budget_attrition = cself_attrition(
        "phi4_4bit_budget_cself_full", budget_run_dir(root, "known_jump")
    ) + cself_attrition("phi4_4bit_budget_cself_heldout", budget_run_dir(root, "heldout_jump"))
    budget_ledgers = [
        call_ledger(
            "phi4_4bit_budget_cself_full",
            budget_run_dir(root, "known_jump") / "llm_calls.jsonl",
        ),
        call_ledger(
            "phi4_4bit_budget_cself_heldout",
            budget_run_dir(root, "heldout_jump") / "llm_calls.jsonl",
        ),
    ]

    analysis_dir = base / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    write_csv(analysis_dir / "world_summary.csv", summaries)
    write_csv(analysis_dir / "per_family.csv", per_family)
    write_csv(analysis_dir / "paired_world_differences.csv", paired)
    write_csv(analysis_dir / "gate_attrition.csv", attrition)
    write_csv(analysis_dir / "compute_ledger.csv", ledgers)
    write_csv(analysis_dir / "phi_budget_world_summary.csv", budget_summaries)
    write_csv(analysis_dir / "phi_budget_paired_differences.csv", budget_paired)
    write_csv(analysis_dir / "phi_budget_gate_attrition.csv", budget_attrition)
    write_csv(analysis_dir / "phi_budget_compute_ledger.csv", budget_ledgers)
    report = {
        "analysis_scope": "minimal targeted sensitivity; world is the replicate",
        "candidate_level_significance_tests": False,
        "validations": validations,
        "phi_budget_validations": budget_validations,
        "world_summary": summaries,
        "paired_world_differences": paired,
        "gate_attrition": attrition,
        "compute_ledger": ledgers,
        "phi_budget_full_world_summary": budget_summaries,
        "phi_budget_full_paired_differences": budget_paired,
        "phi_budget_full_gate_attrition": budget_attrition,
        "phi_budget_full_compute_ledger": budget_ledgers,
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
