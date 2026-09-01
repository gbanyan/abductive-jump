import pytest

from abductive_jump.mutations import MutationOperator, mutate
from abductive_jump.representation import Edge, Node, NodeKind, Representation

BASE = Representation(
    (
        Node("x", NodeKind.OBSERVABLE),
        Node("y", NodeKind.OBSERVABLE),
        Node("eq", NodeKind.EQUATION, {"family": "linear"}),
        Node("prop", NodeKind.PROPERTY),
        Node("inv", NodeKind.INVARIANT),
    ),
    (Edge("x", "input", "eq"), Edge("eq", "output", "y")),
)


CASES = [
    (MutationOperator.ADD_NODE, {"kind": "Primitive", "id": "p"}),
    (MutationOperator.REMOVE_NODE, {"node": "prop"}),
    (MutationOperator.SPLIT_NODE, {"node": "prop"}),
    (MutationOperator.MERGE_NODES, {"node": "x", "other": "y", "id": "xy"}),
    (MutationOperator.ADD_RELATION, {"node": "x", "other": "y", "relation": "links"}),
    (MutationOperator.REMOVE_RELATION, {"node": "x", "other": "eq", "relation": "input"}),
    (MutationOperator.REVERSE_EDGE, {"node": "x", "other": "eq", "relation": "input"}),
    (MutationOperator.REIFY_RELATION, {"node": "x", "other": "eq", "relation": "input", "id": "r"}),
    (MutationOperator.LATENTIZE, {"node": "x"}),
    (MutationOperator.OBSERVABILIZE, {"node": "prop"}),
    (MutationOperator.CONSTANT_TO_VARIABLE, {"value": "3", "id": "v"}),
    (MutationOperator.VARIABLE_TO_FUNCTION, {"node": "x"}),
    (MutationOperator.PROPERTY_TO_RELATION, {"node": "prop"}),
    (MutationOperator.ADD_STATE, {"id": "s"}),
    (MutationOperator.REMOVE_STATE, {"node": "prop"}),
    (MutationOperator.ADD_REGIME, {"id": "reg"}),
    (MutationOperator.MERGE_RULES, {"node": "eq", "other": "prop", "id": "merged"}),
    (MutationOperator.SPLIT_RULE, {"node": "eq"}),
    (MutationOperator.ADD_INVARIANT, {"id": "inv2"}),
    (MutationOperator.BREAK_INVARIANT, {"node": "inv"}),
    (MutationOperator.COMPOSE, {"node": "eq", "other": "prop", "id": "composition"}),
]


@pytest.mark.parametrize("operator,arguments", CASES)
def test_generic_mutations_are_valid_and_fully_provenanced(operator, arguments):
    child, record = mutate(BASE, operator, arguments, 123)
    assert not child.validate()
    assert record.parent_hash == BASE.structural_hash
    assert record.child_hash == child.structural_hash
    assert record.operator is operator
    assert record.seed == 123


def test_subgraph_crossover_records_donor_content():
    donor = Representation((Node("latent", NodeKind.LATENT_VARIABLE),))
    child, record = mutate(BASE, MutationOperator.SUBGRAPH_CROSSOVER, {}, 9, donor=donor)
    assert child.node("latent").kind is NodeKind.LATENT_VARIABLE
    assert record.child_hash == child.structural_hash

