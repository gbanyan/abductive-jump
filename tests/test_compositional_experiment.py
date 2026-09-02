import json

from abductive_jump.compositional_experiment import (
    _needs_validator_repair,
    _parse_self_plans,
    _repair_prompt,
)
from abductive_jump.worlds import generate_world


def test_llm_self_plan_uses_exact_generic_engine_and_records_depth():
    world = generate_world("coordinate_transform", 73)
    plans = []
    for index in range(16):
        node_id = f"f{index}"
        plans.append(
            [
                {"operator": "ADD_FUNCTION", "arguments": {"id": node_id}},
                {"operator": "COMPOSE_FUNCTIONS", "arguments": {"node": node_id, "other": node_id}},
                {"operator": "ADD_CONSTRAINT", "arguments": {"id": f"c{index}"}},
                {"operator": "CHANGE_ARITY", "arguments": {"node": node_id, "arity": "1"}},
            ]
        )
    evaluations, trace = _parse_self_plans(world, json.dumps({"plans": plans}), 99)
    assert len(evaluations) == 16
    assert all(item.candidate.depth == 4 for item in evaluations)
    assert all(row["valid"] for row in trace)
    assert all(row["representation_constructed"] for row in trace)


def test_repair_prompt_contains_only_public_world_and_structural_errors():
    world = generate_world("coordinate_transform", 73)
    prompt = _repair_prompt(
        world,
        '{"plans":"wrong"}',
        [{"valid": False, "error": "invalid_schema:plans_must_be_a_list"}],
    )
    assert "invalid_schema:plans_must_be_a_list" in prompt.user
    assert "hidden truth" not in prompt.user
    assert "falsification" not in prompt.user


def test_invalid_self_output_consumes_all_fixed_plan_opportunities():
    world = generate_world("coordinate_transform", 74)
    evaluations, trace = _parse_self_plans(world, "not-json", 99)
    assert evaluations == []
    assert len(trace) == 16
    assert all(not row["valid"] and row["error"].startswith("invalid_output") for row in trace)
    evaluations, trace = _parse_self_plans(world, "{}", 99)
    assert evaluations == []
    assert len(trace) == 16
    assert all(row["error"].startswith("invalid_schema") for row in trace)


def test_one_invalid_plan_triggers_fixed_portfolio_replacement():
    assert _needs_validator_repair([], 16)
    assert _needs_validator_repair([object()] * 15, 16)
    assert not _needs_validator_repair([object()] * 16, 16)
