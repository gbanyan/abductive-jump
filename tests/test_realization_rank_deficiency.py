import math

from abductive_jump.proposals import external_representation_proposals
from abductive_jump.realization import fit_representation
from abductive_jump.worlds import FAMILIES, generate_world


def test_all_external_slots_return_a_finite_least_squares_realization():
    for family in FAMILIES:
        world = generate_world(family, 41)
        for proposal in external_representation_proposals(world.public(), 41 ^ 0x5151):
            fitted = fit_representation(world.public(), proposal.representation)
            assert math.isfinite(fitted.observational_loss)


def test_rank_deficient_relation_basis_still_fits_an_exact_public_solution():
    world = generate_world("property_to_relation", 41)
    proposal = external_representation_proposals(world.public(), 41 ^ 0x5151)[3]
    assert fit_representation(world.public(), proposal.representation).observational_loss < 1e-10
