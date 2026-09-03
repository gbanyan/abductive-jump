import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from abductive_jump.minimal_sensitivity_analysis import (
    call_ledger,
    cself_attrition,
    cumulative_pass_count,
    paired_difference,
    wilson_interval,
)


def test_wilson_interval_bounds_extremes() -> None:
    low_zero, high_zero = wilson_interval(0, 96)
    low_all, high_all = wilson_interval(96, 96)
    assert low_zero == pytest.approx(0.0)
    assert 0.0 < high_zero < 0.05
    assert 0.95 < low_all < 1.0
    assert high_all == pytest.approx(1.0)


def test_paired_difference_uses_worlds_not_candidates() -> None:
    reference = [
        {"family": "a", "world_seed": 1, "condition_success": False},
        {"family": "a", "world_seed": 2, "condition_success": True},
    ]
    comparison = [
        {"family": "a", "world_seed": 1, "condition_success": True},
        {"family": "a", "world_seed": 2, "condition_success": True},
    ]
    result = paired_difference(reference, comparison)
    assert result["comparison_only_success"] == 1
    assert result["paired_jsr_difference"] == 0.5


def test_paired_difference_rejects_nonidentical_panels() -> None:
    with pytest.raises(ValueError, match="identical worlds"):
        paired_difference(
            [{"family": "a", "world_seed": 1, "condition_success": False}],
            [{"family": "a", "world_seed": 2, "condition_success": False}],
        )


def test_gate_attrition_definition_is_cumulative() -> None:
    rows = [
        {"j1": True, "j2": False, "j3": True},
        {"j1": True, "j2": True, "j3": True},
    ]
    gates = ("j1", "j2", "j3")
    counts = [cumulative_pass_count(rows, gates, index) for index in range(len(gates))]
    assert counts == [2, 1, 1]


def test_call_ledger_can_extract_a_frozen_world_panel(tmp_path: Path) -> None:
    path = tmp_path / "calls.jsonl"
    rows = [
        {
            "world_id": "included",
            "attempt_count": 1,
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "answer_tokens": 20,
            "latency_seconds": 1.5,
        },
        {
            "world_id": "excluded",
            "attempt_count": 1,
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "answer_tokens": 200,
            "latency_seconds": 15,
        },
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    ledger = call_ledger("panel", path, {"included"})
    assert ledger["llm_calls"] == 1
    assert ledger["prompt_tokens"] == 10
    assert ledger["completion_tokens"] == 20


def test_cself_attrition_joins_legacy_plans_to_panel_by_world_id(tmp_path: Path) -> None:
    plan_rows = []
    candidate_rows = []
    for world_id, world_seed in (("included", 1), ("excluded", 2)):
        plan_rows.append(
            {
                "world_id": world_id,
                "family": "a",
                "slot": 0,
                "repair_stage": "initial",
                "request_returned": True,
                "non_empty_answer": True,
                "json_parse_valid": True,
                "plan_schema_valid": True,
                "operation_names_valid": True,
                "argument_types_valid": True,
                "executable": True,
                "representation_constructed": True,
            }
        )
        candidate_rows.append(
            {
                "world_id": world_id,
                "world_seed": world_seed,
                "family": "a",
                "slot": 0,
                "j1": True,
                "j2": True,
                "j3": True,
                "j4": True,
                "j5": True,
            }
        )
    pq.write_table(pa.Table.from_pylist(plan_rows), tmp_path / "llm_self_plans.parquet")
    pq.write_table(pa.Table.from_pylist(candidate_rows), tmp_path / "candidate_results.parquet")

    rows = cself_attrition("legacy", tmp_path, {("a", 1)})

    assert rows[0]["passed"] == 1
    assert rows[0]["denominator"] == 1
    assert rows[-1]["stage"] == "J5"
    assert rows[-1]["passed"] == 1
