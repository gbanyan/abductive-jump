from abductive_jump.negative_controls import CONTROL_CATEGORIES, _candidate
from abductive_jump.worlds import generate_world


def test_all_required_negative_control_categories_are_constructible_and_distinct():
    world = generate_world("latent_common_cause", 10_000)
    candidates = {category: _candidate(world, category) for category in CONTROL_CATEGORIES}
    assert candidates["RANDOM_SEMANTIC_PARAPHRASE"][0] == world.incumbent
    assert candidates["INVALID_STRUCTURAL_CHANGE"][0] != world.incumbent
    assert len(candidates["UNNECESSARY_LATENT"][2]) == 3
    assert len(candidates["OVERCOMPLICATED_NO_GAIN"][2]) == 12
