from abductive_jump.composition_reachability import verify_reachability
from abductive_jump.compositional_worlds import generate_heldout_world
from abductive_jump.worlds import FAMILIES, generate_world


def test_constructive_witnesses_cover_depths_two_three_and_four():
    rows = [verify_reachability(generate_world(family, 17)) for family in FAMILIES]
    rows.append(verify_reachability(generate_heldout_world(17)))
    assert all(row["reachable"] and row["validated_jump"] for row in rows)
    assert all(not row["single_primitive_validated_jump"] for row in rows)
    assert {row["bounded_minimum_depth"] for row in rows} >= {2, 3, 4}

