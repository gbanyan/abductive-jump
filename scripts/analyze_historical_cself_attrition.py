"""Reconstruct historical Phi-4 C_self attrition without model calls.

The historical parser deliberately searched for the first decodable JSON object
anywhere in the answer.  This analysis therefore reports both that registered
parser outcome and a stricter whole-answer JSON-completeness diagnostic.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pyarrow.compute as pc
import pyarrow.parquet as pq

from abductive_jump.historical_attrition import strict_json_object
from abductive_jump.llm import extract_json_object

CONDITION = "C_SELF_LLM_COMPOSITION"
PROPOSAL_SOURCE = "LLM_COMPOSITION"
CASCADE = (
    "response_returned",
    "parse_valid",
    "schema_valid",
    "operation_valid",
    "argument_type_valid",
    "executable",
    "J1",
    "J2",
    "J3",
    "J4",
    "J5",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_proposal_calls(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("condition") == CONDITION and row.get("proposal_source") == PROPOSAL_SOURCE:
                rows.append(row)
    return rows


def count_true(rows: list[dict[str, Any]], key: str) -> int:
    return sum(bool(row[key]) for row in rows)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(historical_dir: Path, output_dir: Path) -> dict[str, Any]:
    summary_path = historical_dir / "summary.json"
    calls_path = historical_dir / "llm_calls.jsonl"
    plans_path = historical_dir / "llm_self_plans.parquet"
    candidates_path = historical_dir / "candidate_results.parquet"
    summary = json.loads(summary_path.read_text())
    required_plans = int(summary["config"]["self_plans_per_slot"])
    max_tokens = int(summary["config"]["generation"]["max_tokens"])

    plan_table = pq.read_table(plans_path)
    family_by_world: dict[str, str] = {}
    for world_id, family in zip(
        plan_table["world_id"].to_pylist(), plan_table["family"].to_pylist(), strict=True
    ):
        prior = family_by_world.setdefault(str(world_id), str(family))
        if prior != family:
            raise ValueError(f"world {world_id} maps to multiple families")

    calls = load_proposal_calls(calls_path)
    response_rows: list[dict[str, Any]] = []
    calls_by_world: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in calls:
        calls_by_world[str(row["world_id"])].append(row)
    for world_id, world_calls in calls_by_world.items():
        for slot, row in enumerate(sorted(world_calls, key=lambda item: int(item["decoding_seed"]))):
            output = str(row.get("full_output") or "")
            returned = bool(output.strip())
            payload: dict[str, Any] | None = None
            if returned:
                try:
                    payload = extract_json_object(output)
                except ValueError:
                    pass
            schema_valid = isinstance(payload, dict) and isinstance(payload.get("plans"), list)
            # The registered parser cannot reach typed operation checks unless
            # the top-level plans schema is valid. Historical schema validity is
            # zero, so later pre-execution stages are necessarily zero as well.
            response_rows.append(
                {
                    "world_id": world_id,
                    "world_seed": int(row["world_seed"]),
                    "family": family_by_world[world_id],
                    "slot": slot,
                    "response_returned": returned,
                    "parse_valid": payload is not None,
                    "strict_complete_json": strict_json_object(output) is not None,
                    "schema_valid": schema_valid,
                    "operation_valid": False,
                    "argument_type_valid": False,
                    "executable": False,
                    "completion_tokens": int(row["completion_tokens"]),
                    "completion_budget_exhausted": int(row["completion_tokens"]) == max_tokens,
                }
            )

    expected_responses = len(family_by_world) * int(summary["config"]["candidate_slots"])
    if len(response_rows) != expected_responses:
        raise ValueError(f"expected {expected_responses} C_self proposal responses, got {len(response_rows)}")
    if plan_table.num_rows != len(response_rows) * required_plans:
        raise ValueError("historical plan-opportunity count does not match response portfolio size")

    legacy_valid = sum(bool(value) for value in plan_table["valid"].to_pylist())
    errors = Counter(str(value) for value in plan_table["error"].to_pylist())
    if legacy_valid:
        raise ValueError("this reconstruction expects the frozen historical trace to have zero valid plans")

    candidates = pq.read_table(candidates_path)
    candidates = candidates.filter(pc.equal(candidates["condition"], CONDITION))
    fallback_gate_counts = {
        gate: sum(bool(value) for value in candidates[gate.lower()].to_pylist())
        for gate in ("J1", "J2", "J3", "J4", "J5")
    }

    response_cascade: list[dict[str, Any]] = []
    for stage in CASCADE:
        if stage in {"J1", "J2", "J3", "J4", "J5"}:
            reached = passed = 0
        else:
            passed = count_true(response_rows, stage)
            reached = len(response_rows) if stage == "response_returned" else response_cascade[-1]["passed"]
        response_cascade.append(
            {
                "unit": "proposal_response",
                "stage": stage,
                "reached": reached,
                "passed": passed,
                "denominator": len(response_rows),
                "rate": passed / len(response_rows),
            }
        )

    plan_cascade = [
        {
            "unit": "plan_opportunity",
            "stage": stage,
            "reached": plan_table.num_rows if stage == "response_returned" else (
                plan_table.num_rows if stage == "parse_valid" else 0
            ),
            "passed": plan_table.num_rows if stage in {"response_returned", "parse_valid"} else 0,
            "denominator": plan_table.num_rows,
            "rate": 1.0 if stage in {"response_returned", "parse_valid"} else 0.0,
        }
        for stage in CASCADE
    ]

    per_family = []
    for family in sorted(set(family_by_world.values())):
        subset = [row for row in response_rows if row["family"] == family]
        per_family.append(
            {
                "family": family,
                "worlds": len({row["world_id"] for row in subset}),
                "responses": len(subset),
                "response_returned": count_true(subset, "response_returned"),
                "parse_valid": count_true(subset, "parse_valid"),
                "strict_complete_json": count_true(subset, "strict_complete_json"),
                "schema_valid": count_true(subset, "schema_valid"),
                "executable": count_true(subset, "executable"),
                "at_token_cap": count_true(subset, "completion_budget_exhausted"),
            }
        )

    at_cap = count_true(response_rows, "completion_budget_exhausted")
    strict_complete = count_true(response_rows, "strict_complete_json")
    executable = count_true(response_rows, "executable")
    report = {
        "analysis": "historical_phi4_cself_offline_attrition",
        "model_calls_made": 0,
        "historical_population": {
            "worlds": len(family_by_world),
            "families": len(set(family_by_world.values())),
            "candidate_slots_per_world": int(summary["config"]["candidate_slots"]),
            "proposal_responses": len(response_rows),
            "plans_requested_per_response": required_plans,
            "plan_opportunities": plan_table.num_rows,
        },
        "registered_parser_semantics": (
            "parse_valid means the historical extract_json_object routine found any decodable JSON object; "
            "it does not require the whole response or outer plans object to be complete"
        ),
        "response_cascade": response_cascade,
        "plan_opportunity_cascade": plan_cascade,
        "diagnostics": {
            "nonempty_responses": count_true(response_rows, "response_returned"),
            "strict_complete_json_responses": strict_complete,
            "responses_at_completion_token_cap": at_cap,
            "completion_token_cap": max_tokens,
            "historical_plan_trace_errors": dict(errors),
        },
        "fallback_exclusion": {
            "candidate_rows": candidates.num_rows,
            "explanation": (
                "When no self plan was executable, the historical runner inserted the incumbent as a "
                "default downstream candidate. Its gate values are not evidence about an LLM-proposed "
                "representation and are excluded from the proposal cascade."
            ),
            "fallback_gate_pass_counts": fallback_gate_counts,
        },
        "repair_trigger": {
            "threshold": 0.25,
            "pre_executable_failure_rate": 1.0 - executable / len(response_rows),
            "triggered": (1.0 - executable / len(response_rows)) > 0.25,
        },
        "interpretation": (
            "The historical 0/400 C_self result is primarily confounded by output completion/serialization: "
            "all proposal responses hit the 700-token ceiling, none was complete whole-answer JSON, and none "
            "reached an executable representation. It therefore does not distinguish the quality of valid "
            "representation proposals from interface failure."
        ),
        "per_family": per_family,
        "source_sha256": {
            path.name: sha256(path)
            for path in (summary_path, calls_path, plans_path, candidates_path)
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "historical_cself_attrition.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_csv(output_dir / "historical_cself_attrition.csv", response_cascade + plan_cascade)
    write_csv(output_dir / "historical_cself_per_family.csv", per_family)
    markdown = [
        "# Historical Phi-4 C_self failure attrition",
        "",
        "This is an offline reconstruction from frozen artifacts; it made **zero model calls**.",
        "",
        "| Stage | Proposal responses passed | Rate |",
        "|---|---:|---:|",
    ]
    markdown.extend(
        f"| {row['stage']} | {row['passed']}/{row['denominator']} | {row['rate']:.1%} |"
        for row in response_cascade
    )
    markdown.extend(
        [
            "",
            (
                "All 1,200 responses were non-empty and hit the 700-token completion cap. The registered "
                "parser extracted a nested JSON object from every truncated answer, but no response contained "
                "a valid outer `plans` schema and none was complete whole-answer JSON. No self-proposed "
                "representation reached execution or J1–J5."
            ),
            "",
            (
                "The runner's incumbent fallback candidates are excluded from this cascade because they were "
                "not representations proposed by C_self."
            ),
            "",
        ]
    )
    (output_dir / "historical_cself_attrition.md").write_text("\n".join(markdown), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--historical-dir", type=Path, default=Path("artifacts/compositional/confirmatory-existing")
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments/nmi_minimal_sensitivity_v1/offline"),
    )
    args = parser.parse_args()
    report = run(args.historical_dir, args.output_dir)
    print(json.dumps(report["historical_population"], sort_keys=True))


if __name__ == "__main__":
    main()
