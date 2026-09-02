from abductive_jump.analysis import _paired_bootstrap, _wilson
from abductive_jump.worlds import FAMILIES


def test_paired_bootstrap_excludes_no_jump_controls_from_jsr_difference():
    rows = []
    for family in FAMILIES:
        rows += [
            {"family": family, "world_seed": 1, "method": "left", "condition_success": True, "no_jump": False},
            {"family": family, "world_seed": 1, "method": "right", "condition_success": False, "no_jump": False},
            {"family": family, "world_seed": 2, "method": "left", "condition_success": False, "no_jump": True},
            {"family": family, "world_seed": 2, "method": "right", "condition_success": False, "no_jump": True},
        ]
    result = _paired_bootstrap(rows, "left", "right", "method")
    assert result["estimate"] == 1.0
    assert result["ci_low"] == 1.0


def test_zero_of_two_hundred_wilson_upper_bound_is_below_five_percent():
    assert _wilson(0, 200)[1] < 0.05
