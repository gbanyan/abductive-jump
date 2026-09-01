import dataclasses

import pytest

from abductive_jump.gates import evaluate_jump, freeze_predictions
from abductive_jump.oracle import incumbent_oracle
from abductive_jump.worlds import FAMILIES, generate_world


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("seed", [7, 42, 901])
def test_jump_worlds_are_locally_adequate_and_truth_passes_all_gates(family, seed):
    world = generate_world(family, seed)
    oracle = incumbent_oracle(world)
    commitment = freeze_predictions(world, world.truth, oracle)
    result = evaluate_jump(world, world.truth, commitment)
    assert oracle.exact
    assert oracle.hypotheses_evaluated == len(world.incumbent_programs)
    assert oracle.observational_loss <= 1e-12
    assert result.validated_jump
    assert result.counterfactual_candidate_loss == 0
    assert result.counterfactual_oracle_loss > 0
    split_ids = [
        {case.case_id for case in split}
        for split in (world.observations, world.validation, world.interventions, world.falsification)
    ]
    assert all(not left & right for i, left in enumerate(split_ids) for right in split_ids[i + 1 :])


@pytest.mark.parametrize("family", FAMILIES)
def test_no_jump_truth_is_in_incumbent_language_and_not_accepted(family):
    world = generate_world(family, 18, no_jump=True)
    oracle = incumbent_oracle(world)
    result = evaluate_jump(world, world.truth, freeze_predictions(world, world.truth, oracle))
    assert world.incumbent_language.contains(world.truth.representation)
    assert not result.j1_representation_escape
    assert not result.validated_jump


def test_public_world_redacts_truth_family_and_hidden_splits():
    world = generate_world("state_invention", 3)
    public = world.public()
    fields = {field.name for field in dataclasses.fields(public)}
    assert "truth" not in fields
    assert "family" not in fields
    assert "validation" not in fields
    assert "falsification" not in fields
    assert all(case["case_id"].startswith("obs-") for case in public.observations)
    public_fields = {name for case in public.observations for name in case["inputs"]}
    assert not public_fields & {"x", "x1", "x2", "history", "regime", "environment", "context"}


def test_commitment_tampering_is_rejected():
    world = generate_world("causal_ambiguity", 2)
    oracle = incumbent_oracle(world)
    commitment = freeze_predictions(world, world.truth, oracle)
    tampered = dataclasses.replace(commitment, candidate_predictions=(999.0,) + commitment.candidate_predictions[1:])
    with pytest.raises(ValueError, match="inconsistent"):
        evaluate_jump(world, world.truth, tampered)
