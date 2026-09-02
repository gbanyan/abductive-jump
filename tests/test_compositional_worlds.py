from abductive_jump.compositional_worlds import HELD_OUT_FAMILY, generate_heldout_world
from abductive_jump.oracle import incumbent_oracle


def test_heldout_world_is_deterministic_redacted_and_locally_adequate():
    world = generate_heldout_world(91)
    again = generate_heldout_world(91)
    assert world == again
    assert world.family == HELD_OUT_FAMILY
    assert incumbent_oracle(world).observational_loss == 0.0
    public = world.public()
    assert not hasattr(public, "family")
    assert all("outcome" not in query for query in public.intervention_queries)


def test_heldout_no_jump_truth_is_inside_incumbent_language():
    world = generate_heldout_world(92, no_jump=True)
    assert world.incumbent_language.contains(world.truth.representation)
    assert incumbent_oracle(world).observational_loss == 0.0

