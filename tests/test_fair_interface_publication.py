from abductive_jump.fair_interface_publication import paired_row


def test_paired_row_counts_world_transitions() -> None:
    reference = {("a", 1): False, ("a", 2): True, ("b", 1): False, ("b", 2): True}
    comparison = {("a", 1): False, ("a", 2): True, ("b", 1): True, ("b", 2): False}

    row = paired_row("old", reference, "new", comparison)

    assert row == {
        "worlds": 4,
        "both_fail": 1,
        "both_succeed": 1,
        "comparison_only_success": 1,
        "reference_only_success": 1,
        "paired_jsr_difference": 0.0,
        "reference": "old",
        "comparison": "new",
    }


def test_paired_row_rejects_nonidentical_panels() -> None:
    try:
        paired_row("old", {("a", 1): False}, "new", {("a", 2): False})
    except ValueError as exc:
        assert "paired panels differ" in str(exc)
    else:
        raise AssertionError("nonidentical panels were accepted")
