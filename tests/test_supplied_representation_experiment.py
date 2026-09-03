import json

import pytest

from abductive_jump.supplied_representation_experiment import evaluate_model_output
from abductive_jump.worlds import generate_world


def test_positive_control_does_not_accept_missing_model_expression() -> None:
    world = generate_world("unification", 30014, no_jump=False)
    output = json.dumps(
        {
            "representation": "USE_SUPPLIED_REPRESENTATION",
            "explanation": "test",
            "selected_intervention_ids": [world.interventions[0].case_id],
        }
    )
    with pytest.raises(KeyError):
        evaluate_model_output(world, output)


def test_positive_control_does_not_replace_invalid_model_intervention() -> None:
    world = generate_world("unification", 30014, no_jump=False)
    output = json.dumps(
        {
            "representation": "USE_SUPPLIED_REPRESENTATION",
            "expression": {"op": "const", "value": 0},
            "explanation": "test",
            "selected_intervention_ids": ["not-a-public-intervention"],
        }
    )
    with pytest.raises(ValueError, match="exactly one selected intervention"):
        evaluate_model_output(world, output)
