from abductive_jump.extension_analysis import _aggregate_boolean_stages, _holm, _paired


def test_paired_analysis_uses_worlds_and_preserves_family_effects():
    left = [
        {"family": "a", "world_seed": 1, "condition_success": True},
        {"family": "a", "world_seed": 2, "condition_success": False},
        {"family": "b", "world_seed": 1, "condition_success": True},
        {"family": "b", "world_seed": 2, "condition_success": True},
    ]
    right = [
        {"family": "a", "world_seed": 1, "condition_success": False},
        {"family": "a", "world_seed": 2, "condition_success": False},
        {"family": "b", "world_seed": 1, "condition_success": True},
        {"family": "b", "world_seed": 2, "condition_success": False},
    ]
    result = _paired(left, right, "toy")
    assert result["paired_worlds"] == 4
    assert result["estimate"] == 0.5
    assert result["discordant_left_wins"] == 2
    assert result["discordant_right_wins"] == 0


def test_holm_is_applied_within_declared_multiplicity_family():
    rows = [
        {"multiplicity_family": "a", "mcnemar_exact_p_two_sided": 0.01},
        {"multiplicity_family": "a", "mcnemar_exact_p_two_sided": 0.04},
        {"multiplicity_family": "b", "mcnemar_exact_p_two_sided": 0.03},
    ]
    _holm(rows)
    assert rows[0]["mcnemar_holm_p"] == 0.02
    assert rows[1]["mcnemar_holm_p"] == 0.04
    assert rows[2]["mcnemar_holm_p"] == 0.03


def test_attrition_counts_missing_downstream_stage_as_failure():
    rows = [
        {
            "treatment_id": "x",
            "study": "s",
            "split": "p",
            "family": "f",
            "a": True,
            "b": True,
        },
        {
            "treatment_id": "x",
            "study": "s",
            "split": "p",
            "family": "f",
            "a": False,
        },
    ]
    result = _aggregate_boolean_stages(rows, ("a", "b"), "candidate")
    assert result[1]["total"] == 2
    assert result[1]["cumulative_successes"] == 1
    assert result[1]["conditional_denominator"] == 1
