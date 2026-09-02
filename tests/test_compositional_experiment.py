import json

from abductive_jump.compositional_experiment import _parse_self_plans
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
