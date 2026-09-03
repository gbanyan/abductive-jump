import pytest

from abductive_jump.minimal_sensitivity import select_panel_seeds


def test_panel_selection_is_deterministic_and_unique() -> None:
    source = list(range(30000, 30050))
    first = select_panel_seeds(source, 12)
    assert first == select_panel_seeds(source, 12)
    assert len(first) == len(set(first)) == 12
    assert set(first) <= set(source)


def test_panel_selection_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        select_panel_seeds([1, 1], 1)
    with pytest.raises(ValueError):
        select_panel_seeds([1, 2], 3)
