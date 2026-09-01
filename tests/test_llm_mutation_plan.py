import pytest

from abductive_jump.proposals import apply_mutation_plan
from abductive_jump.representation import NodeKind
from abductive_jump.worlds import generate_world


def test_llm_plan_uses_same_typed_mutation_engine_and_records_ancestry():
    world = generate_world("coordinate_transform", 2)
    source = next(node.id for node in world.incumbent.nodes if node.attributes.get("role") == "input")
    plan = [
        {
            "operator": "ADD_NODE",
            "arguments": {
                "kind": "Function",
                "id": "new_transform",
                "attr_transform": "square",
            },
        },
        {
            "operator": "ADD_RELATION",
            "arguments": {
                "node": source,
                "other": "new_transform",
                "relation": "transforms",
            },
        },
    ]
    proposal = apply_mutation_plan(world.incumbent, plan, 10)
    assert proposal.representation.node("new_transform").kind is NodeKind.FUNCTION
    assert proposal.operators == ("ADD_NODE", "ADD_RELATION")


def test_llm_plan_has_frozen_complexity_and_schema():
    world = generate_world("unification", 2)
    with pytest.raises(ValueError):
        apply_mutation_plan(world.incumbent, [], 10)
    with pytest.raises(ValueError):
        apply_mutation_plan(
            world.incumbent,
            [{"operator": "ADD_NODE", "arguments": {}, "comment": "extra"}],
            10,
        )
