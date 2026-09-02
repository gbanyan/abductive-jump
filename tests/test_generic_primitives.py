import pytest

from abductive_jump.generic_primitives import GenericPrimitive, apply_primitive
from abductive_jump.representation import Edge, Node, NodeKind, Representation

BASE = Representation(
    (
        Node("p", NodeKind.PRIMITIVE),
        Node("q", NodeKind.PRIMITIVE),
        Node("fun", NodeKind.FUNCTION),
        Node("eq", NodeKind.EQUATION, {"family": "generic"}),
        Node("constraint", NodeKind.CONSTRAINT),
    ),
    (
        Edge("p", "link", "q"),
        Edge("p", "dependency", "q"),
        Edge("p", "argument_0", "fun"),
        Edge("fun", "result_of", "eq"),
    ),
)


CASES = {
    GenericPrimitive.ADD_NODE: (BASE, {"id": "new"}, None),
    GenericPrimitive.REMOVE_NODE: (BASE, {"node": "q"}, None),
    GenericPrimitive.ADD_EDGE: (BASE, {"node": "q", "other": "p", "relation": "new"}, None),
    GenericPrimitive.REMOVE_EDGE: (BASE, {"node": "p", "other": "q", "relation": "link"}, None),
    GenericPrimitive.REVERSE_EDGE: (BASE, {"node": "p", "other": "q", "relation": "link"}, None),
    GenericPrimitive.CHANGE_NODE_TYPE: (BASE, {"node": "p", "kind": "Relation"}, None),
    GenericPrimitive.CHANGE_EDGE_TYPE: (BASE, {"node": "p", "other": "q", "from_relation": "link", "to_relation": "other"}, None),
    GenericPrimitive.CHANGE_OBSERVABILITY: (BASE, {"node": "p", "observable": "false"}, None),
    GenericPrimitive.CHANGE_ARITY: (BASE, {"node": "p", "arity": "2"}, None),
    GenericPrimitive.BIND_ARGUMENT: (BASE, {"node": "fun", "other": "q", "position": "1"}, None),
    GenericPrimitive.UNBIND_ARGUMENT: (BASE, {"node": "fun", "other": "p", "position": "0"}, None),
    GenericPrimitive.ADD_FUNCTION: (BASE, {"id": "fun2"}, None),
    GenericPrimitive.REMOVE_FUNCTION: (BASE, {"node": "fun"}, None),
    GenericPrimitive.ADD_EQUATION: (BASE, {"id": "eq2"}, None),
    GenericPrimitive.REMOVE_EQUATION: (BASE, {"node": "eq"}, None),
    GenericPrimitive.COMPOSE_FUNCTIONS: (BASE, {"node": "fun", "other": "fun"}, None),
    GenericPrimitive.DECOMPOSE_FUNCTION: (
        Representation(BASE.nodes, BASE.edges + (Edge("fun", "composes_into", "fun"),)),
        {"node": "fun", "other": "fun"},
        None,
    ),
    GenericPrimitive.ADD_TEMPORAL_INDEX: (BASE, {"node": "p"}, None),
    GenericPrimitive.REMOVE_TEMPORAL_INDEX: (
        Representation((Node("p", NodeKind.PRIMITIVE, {"temporal_index": "t"}), *BASE.nodes[1:]), BASE.edges),
        {"node": "p"},
        None,
    ),
    GenericPrimitive.ADD_DEPENDENCY: (BASE, {"node": "q", "other": "p"}, None),
    GenericPrimitive.REMOVE_DEPENDENCY: (BASE, {"node": "p", "other": "q"}, None),
    GenericPrimitive.ADD_CONSTRAINT: (BASE, {"id": "constraint2"}, None),
    GenericPrimitive.REMOVE_CONSTRAINT: (BASE, {"node": "constraint"}, None),
    GenericPrimitive.MERGE_NODES: (BASE, {"node": "p", "other": "q", "id": "merged"}, None),
    GenericPrimitive.SPLIT_NODE: (BASE, {"node": "p", "left": "left", "right": "right"}, None),
    GenericPrimitive.REIFY_EDGE_AS_NODE: (BASE, {"node": "p", "other": "q", "relation": "link", "id": "rel"}, None),
    GenericPrimitive.REIFY_NODE_AS_EDGE: (BASE, {"node": "fun", "relation": "collapsed"}, None),
    GenericPrimitive.SUBGRAPH_COPY: (BASE, {"node": "p", "id": "copy"}, None),
    GenericPrimitive.SUBGRAPH_CROSSOVER: (
        BASE,
        {"donor_node": "donor", "id": "cross"},
        Representation((Node("donor", NodeKind.RELATION),)),
    ),
}


@pytest.mark.parametrize("operator", tuple(GenericPrimitive))
def test_every_generic_primitive_is_local_valid_and_provenanced(operator):
    parent, arguments, donor = CASES[operator]
    child, record = apply_primitive(parent, operator, arguments, 123, depth=1, donor=donor)
    assert not child.validate()
    assert child.structural_hash != parent.structural_hash
    assert record.parent_hash == parent.structural_hash
    assert record.child_hash == child.structural_hash
    assert record.operator is operator
    assert record.seed == 123
    assert record.depth == 1


def test_add_node_cannot_smuggle_type_or_semantic_attributes():
    with pytest.raises(ValueError):
        apply_primitive(
            BASE,
            GenericPrimitive.ADD_NODE,
            {"id": "answer", "kind": "StateVariable"},
            1,
            depth=1,
        )

