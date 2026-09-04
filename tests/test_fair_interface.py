from __future__ import annotations

import json

from abductive_jump.compositional_experiment import _parse_self_plans, _world
from abductive_jump.fair_interface import (
    deliberation_prompt,
    operator_vocabulary,
    primitive_argument_schemas,
    response_format,
    serialization_prompt,
)
from abductive_jump.fair_interface_experiment import evaluate_selected_science


def test_fair_interface_preserves_frozen_operator_vocabulary() -> None:
    assert len(operator_vocabulary()) == 28
    assert "SUBGRAPH_CROSSOVER" not in operator_vocabulary()


def test_exact_argument_contract_matches_executor_names() -> None:
    schemas = primitive_argument_schemas()
    assert schemas["CHANGE_NODE_TYPE"]["required"] == ["node", "kind"]
    assert schemas["ADD_EDGE"]["required"] == ["node", "other", "relation"]
    assert schemas["BIND_ARGUMENT"]["required"] == ["node", "other", "position"]


def test_response_schema_fixes_plan_count_and_depth() -> None:
    schema = response_format()["json_schema"]["schema"]
    plans = schema["properties"]["plans"]
    assert plans["minItems"] == plans["maxItems"] == 16
    assert plans["items"]["minItems"] == plans["items"]["maxItems"] == 4


def test_prompts_expose_no_hidden_outcomes() -> None:
    config = {
        "families": ["latent_common_cause"],
        "world_seeds": [30014],
        "no_jump": False,
    }
    world = _world(config, "latent_common_cause", 30014)
    first = deliberation_prompt(world)
    second = serialization_prompt(world, "candidate deliberation")
    for prompt in (first, second):
        body = json.loads(prompt.user.split(": ", 1)[1])
        assert "truth" not in body
        assert "outcome" not in json.dumps(
            body["prospective_intervention_queries_without_outcomes"]
        )
        assert "from_relation" in prompt.user
        assert "to_relation" in prompt.user


def test_schema_valid_plan_reaches_dynamic_executor() -> None:
    config = {
        "families": ["latent_common_cause"],
        "world_seeds": [30014],
        "no_jump": False,
    }
    world = _world(config, "latent_common_cause", 30014)
    node = world.incumbent.nodes[0].id
    plans = [
        [
            {"operator": "ADD_NODE", "arguments": {"id": f"n{i}"}},
            {
                "operator": "CHANGE_NODE_TYPE",
                "arguments": {"node": f"n{i}", "kind": "LatentVariable"},
            },
            {
                "operator": "ADD_DEPENDENCY",
                "arguments": {"node": f"n{i}", "other": node},
            },
            {
                "operator": "CHANGE_OBSERVABILITY",
                "arguments": {"node": f"n{i}", "observable": "false"},
            },
        ]
        for i in range(16)
    ]
    evaluated, trace = _parse_self_plans(world, json.dumps({"plans": plans}), 1)
    assert len(evaluated) == 16
    assert all(row["executable"] for row in trace)
    result = evaluate_selected_science(
        world,
        evaluated[0],
        gate_thresholds={
            "epsilon_obs": 1e-12,
            "epsilon_candidate_obs": 1e-12,
            "min_prediction_separation": 0.5,
            "delta_cf": 0.1,
            "epsilon_falsification": 1e-12,
            "delta_falsification": 0.1,
        },
        proposal_executable=True,
    )
    assert result["proposal_executable"] is True
    assert set(result) >= {"j0", "j1", "j2", "j3", "j4", "j5", "validated_jump"}
