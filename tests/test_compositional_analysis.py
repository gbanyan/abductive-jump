from abductive_jump.compositional_analysis import _holm, _paired_effect, _wilson


def test_wilson_zero_success_upper_is_nonzero_and_shrinks():
    assert 0 < _wilson(0, 100)[1] < _wilson(0, 50)[1]


def test_paired_effect_and_holm_are_deterministic():
    rows = []
    for seed in range(4):
        rows.extend(
            (
                {
                    "family": "heldout",
                    "world_seed": seed,
                    "condition": "left",
                    "condition_success": True,
                },
                {
                    "family": "heldout",
                    "world_seed": seed,
                    "condition": "right",
                    "condition_success": False,
                },
            )
        )
    first = _paired_effect(rows, "left", "right", stratified=False)
    again = _paired_effect(rows, "left", "right", stratified=False)
    assert first == again
    assert first["estimate"] == 1.0
    comparisons = [
        {"p_one_sided": 0.01},
        {"p_one_sided": 0.04},
    ]
    _holm(comparisons)
    assert comparisons[0]["p_holm"] == 0.02
    assert comparisons[1]["p_holm"] == 0.04
