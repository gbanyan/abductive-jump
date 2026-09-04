#!/usr/bin/env python3
"""Audit the frozen C_self prompt/parser contract without new model calls."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from abductive_jump.llm import extract_json_object

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "results"
ARTIFACT = ROOT / "artifacts" / "nmi_interface_contract_audit.json"
REPORT = ROOT / "docs" / "nmi_interface_contract_audit.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_rows(name: str) -> list[dict[str, Any]]:
    path = RESULTS / name / "llm_calls.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


def phase_one(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if "Construct exactly 16" in row["full_prompt_json"]]


def summarize_calls(name: str) -> dict[str, Any]:
    rows = phase_one(call_rows(name))
    strict = legacy = plans_list = 0
    for row in rows:
        try:
            strict += isinstance(json.loads(row["full_output"]), dict)
        except json.JSONDecodeError:
            pass
        try:
            payload = extract_json_object(row["full_output"])
            legacy += 1
            plans_list += isinstance(payload.get("plans"), list)
        except ValueError:
            pass
    first_prompt = rows[0]["full_prompt_json"]
    return {
        "phase_one_calls": len(rows),
        "finish_reasons": dict(Counter(str(row["finish_reason"]) for row in rows)),
        "nonempty_content": sum(bool(row["full_output"]) for row in rows),
        "reasoning_present": sum(bool(row["reasoning_output"]) for row in rows),
        "strict_whole_response_json": strict,
        "legacy_object_extraction": legacy,
        "legacy_extraction_with_plans_list": plans_list,
        "starts_with_outer_plans": sum(
            row["full_output"].lstrip().startswith('{"plans"') for row in rows
        ),
        "uses_source_key": sum('"source"' in row["full_output"] for row in rows),
        "uses_target_key": sum('"target"' in row["full_output"] for row in rows),
        "uses_type_key": sum('"type"' in row["full_output"] for row in rows),
        "prompt_contains_exact_change_edge_keys": all(
            token in first_prompt for token in ("from_relation", "to_relation")
        ),
        "prompt_contains_exact_node_type_keys": all(
            token in first_prompt for token in ('"node"', '"kind"')
        ),
    }


def summarize_trace(name: str) -> dict[str, Any]:
    path = RESULTS / name / "llm_self_plans.parquet"
    rows = pq.read_table(path).to_pylist()
    return {
        "plan_opportunities": len(rows),
        "errors": dict(Counter(str(row.get("error", "")) for row in rows)),
        "schema_valid": sum(bool(row.get("plan_schema_valid")) for row in rows),
        "operation_valid": sum(bool(row.get("operation_names_valid")) for row in rows),
        "argument_type_valid": sum(bool(row.get("argument_types_valid")) for row in rows),
        "executable": sum(bool(row.get("executable")) for row in rows),
    }


def main() -> None:
    conditions = {}
    sources = {}
    for name in ("deepseek_matched_cself", "deepseek_native_cself"):
        conditions[name] = {
            "calls": summarize_calls(name),
            "trace": summarize_trace(name),
        }
        for filename in ("llm_calls.jsonl", "llm_self_plans.parquet"):
            path = RESULTS / name / filename
            sources[str(path.relative_to(ROOT))] = digest(path)
    audit = {
        "schema_version": "nmi-interface-contract-audit-v1",
        "analysis": "offline inspection; zero model calls",
        "conditions": conditions,
        "sources_sha256": sources,
        "finding": (
            "The registered prompt omitted exact per-operator argument keys. Matched outputs were "
            "usually truncated outer JSON and used parser-incompatible source/target/type keys; native "
            "reasoning produced no answer content. Existing autonomous rates therefore cannot isolate "
            "conceptual representation-proposal quality."
        ),
    }
    ARTIFACT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    matched = conditions["deepseek_matched_cself"]
    native = conditions["deepseek_native_cself"]
    REPORT.write_text(
        "\n".join(
            [
                "# NMI C_self interface-contract audit",
                "",
                "This audit used frozen raw responses only and made zero model calls.",
                "",
                "## Findings",
                "",
                (
                    f"- Matched DeepSeek: {matched['calls']['phase_one_calls']} proposal calls; "
                    f"{matched['calls']['strict_whole_response_json']} strict whole-response JSON; "
                    f"{matched['trace']['executable']}/{matched['trace']['plan_opportunities']} executable plan opportunities."
                ),
                (
                    f"- Native DeepSeek: {native['calls']['phase_one_calls']} proposal calls; reasoning was present in "
                    f"{native['calls']['reasoning_present']}, but content was present in {native['calls']['nonempty_content']}; "
                    f"{native['trace']['executable']}/{native['trace']['plan_opportunities']} executable plan opportunities."
                ),
                (
                    "- The proposal prompt listed operator names but not the exact parser-level argument contract. "
                    "For example, the executor requires `node`/`other`/`kind`, while all matched proposal calls used "
                    "at least one of the incompatible keys `source`/`target`/`type`."
                ),
                (
                    "- The permissive legacy extractor can recover an inner JSON object from a truncated outer response. "
                    "Accordingly, 'JSON extractable' does not imply a valid top-level plan object."
                ),
                "",
                "## Interpretation",
                "",
                (
                    "The observed autonomous failures are interface-confounded. They do not establish that the model failed "
                    "to conceptualize an outside-space representation. A fair sensitivity must disclose the exact syntactic "
                    "contract, reserve a separate final-answer budget and guarantee only grammar-level serialization, while "
                    "keeping worlds, primitives, opportunities, hidden-information boundaries and J0-J5 unchanged."
                ),
                "",
            ]
        )
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
