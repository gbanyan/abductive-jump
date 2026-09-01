import pytest

from abductive_jump.executable import (
    evaluate_executable,
    freeze_theory,
    parse_theory,
)
from abductive_jump.realization import fit_representation
from abductive_jump.worlds import FAMILIES, generate_world


@pytest.mark.parametrize("family", FAMILIES)
def test_family_blind_realizer_fits_supplied_truth_and_passes_gates(family):
    world = generate_world(family, 1101)
    public = world.public()
    realization = fit_representation(public, world.truth.representation)
    payload = {
        "representation": world.truth.representation.canonical_dict(),
        "expression": realization.expression.tree,
        "selected_intervention_ids": [world.interventions[0].case_id],
    }
    theory = parse_theory(payload, {public: internal for internal, public in world.variable_names})
    result = evaluate_executable(world, theory, freeze_theory(world, theory))
    assert realization.observational_loss <= 1e-12
    assert result.validated_jump


def test_realizer_uses_only_redacted_public_world_and_rejects_singular_basis():
    world = generate_world("unification", 2)
    realization = fit_representation(world.public(), world.truth.representation)
    assert realization.basis_names
    assert world.family not in realization.basis_names
