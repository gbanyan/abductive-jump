import pytest

from abductive_jump.minimal_sensitivity_analysis import (
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
