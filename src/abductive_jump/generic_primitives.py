from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from .representation import Edge, Node, NodeKind, Representation


class GenericPrimitive(StrEnum):
    ADD_NODE = "ADD_NODE"
    REMOVE_NODE = "REMOVE_NODE"
    ADD_EDGE = "ADD_EDGE"
    REMOVE_EDGE = "REMOVE_EDGE"
    REVERSE_EDGE = "REVERSE_EDGE"
    CHANGE_NODE_TYPE = "CHANGE_NODE_TYPE"
    CHANGE_EDGE_TYPE = "CHANGE_EDGE_TYPE"
    CHANGE_OBSERVABILITY = "CHANGE_OBSERVABILITY"
    CHANGE_ARITY = "CHANGE_ARITY"
    BIND_ARGUMENT = "BIND_ARGUMENT"
    UNBIND_ARGUMENT = "UNBIND_ARGUMENT"
    ADD_FUNCTION = "ADD_FUNCTION"
    REMOVE_FUNCTION = "REMOVE_FUNCTION"
    ADD_EQUATION = "ADD_EQUATION"
    REMOVE_EQUATION = "REMOVE_EQUATION"
    COMPOSE_FUNCTIONS = "COMPOSE_FUNCTIONS"
    DECOMPOSE_FUNCTION = "DECOMPOSE_FUNCTION"
    ADD_TEMPORAL_INDEX = "ADD_TEMPORAL_INDEX"
    REMOVE_TEMPORAL_INDEX = "REMOVE_TEMPORAL_INDEX"
    ADD_DEPENDENCY = "ADD_DEPENDENCY"
    REMOVE_DEPENDENCY = "REMOVE_DEPENDENCY"
    ADD_CONSTRAINT = "ADD_CONSTRAINT"
    REMOVE_CONSTRAINT = "REMOVE_CONSTRAINT"
    MERGE_NODES = "MERGE_NODES"
    SPLIT_NODE = "SPLIT_NODE"
    REIFY_EDGE_AS_NODE = "REIFY_EDGE_AS_NODE"
    REIFY_NODE_AS_EDGE = "REIFY_NODE_AS_EDGE"
    SUBGRAPH_COPY = "SUBGRAPH_COPY"
    SUBGRAPH_CROSSOVER = "SUBGRAPH_CROSSOVER"


@dataclass(frozen=True, slots=True)
class PrimitiveRecord:
    parent_hash: str
    child_hash: str
    operator: GenericPrimitive
    arguments: tuple[tuple[str, str], ...]
    seed: int
    depth: int
    donor_hash: str = ""


@dataclass(frozen=True, slots=True)
class ComposedRepresentation:
    representation: Representation
    ancestry: tuple[PrimitiveRecord, ...]

    @property
    def depth(self) -> int:
        return len(self.ancestry)

    @property
    def operators(self) -> tuple[str, ...]:
        return tuple(record.operator.value for record in self.ancestry)


def _fresh_id(rep: Representation, prefix: str, rng: random.Random) -> str:
    known = {node.id for node in rep.nodes}
    while True:
        candidate = f"{prefix}_{rng.randrange(1_000_000):06d}"
        if candidate not in known:
            return candidate


def _replace_node(rep: Representation, node_id: str, replacement: Node) -> list[Node]:
    if node_id not in {node.id for node in rep.nodes}:
        raise ValueError(f"unknown node: {node_id}")
    return [replacement if node.id == node_id else node for node in rep.nodes]


def apply_primitive(
    parent: Representation,
    operator: GenericPrimitive,
    arguments: Mapping[str, str],
    seed: int,
    *,
    depth: int,
    donor: Representation | None = None,
) -> tuple[Representation, PrimitiveRecord]:
    """Apply one family-blind local rewrite.

    `ADD_NODE` deliberately cannot accept a scientific type or attributes. Scientific types,
    observability, arity, temporal indexing, dependencies, and bindings require separate
    primitive records.
    """

    rng = random.Random(seed)
    nodes, edges = list(parent.nodes), list(parent.edges)
    by_id = {node.id: node for node in nodes}
    node_id = str(arguments.get("node", ""))
    other_id = str(arguments.get("other", ""))
    relation = str(arguments.get("relation", "dependency"))

    if operator is GenericPrimitive.ADD_NODE:
        if set(arguments) - {"id"}:
            raise ValueError("ADD_NODE accepts only an optional id")
        nodes.append(Node(arguments.get("id") or _fresh_id(parent, "node", rng), NodeKind.PRIMITIVE))
    elif operator is GenericPrimitive.REMOVE_NODE:
        if node_id not in by_id:
            raise ValueError(f"unknown node: {node_id}")
        nodes = [node for node in nodes if node.id != node_id]
        edges = [edge for edge in edges if edge.source != node_id and edge.target != node_id]
    elif operator is GenericPrimitive.ADD_EDGE:
        edges.append(Edge(node_id, relation, other_id))
    elif operator is GenericPrimitive.REMOVE_EDGE:
        edge = Edge(node_id, relation, other_id)
        if edge not in edges:
            raise ValueError("edge does not exist")
        edges.remove(edge)
    elif operator is GenericPrimitive.REVERSE_EDGE:
        edge = Edge(node_id, relation, other_id)
        if edge not in edges:
            raise ValueError("edge does not exist")
        edges[edges.index(edge)] = Edge(other_id, relation, node_id)
    elif operator is GenericPrimitive.CHANGE_NODE_TYPE:
        old = by_id[node_id]
        replacement = Node(old.id, NodeKind(str(arguments["kind"])), old.attributes)
        nodes = _replace_node(parent, node_id, replacement)
    elif operator is GenericPrimitive.CHANGE_EDGE_TYPE:
        old = Edge(node_id, str(arguments["from_relation"]), other_id)
        if old not in edges:
            raise ValueError("edge does not exist")
        edges[edges.index(old)] = Edge(node_id, str(arguments["to_relation"]), other_id)
    elif operator is GenericPrimitive.CHANGE_OBSERVABILITY:
        old = by_id[node_id]
        attrs = {**old.attributes, "observable": str(arguments["observable"]).lower() == "true"}
        nodes = _replace_node(parent, node_id, Node(old.id, old.kind, attrs))
    elif operator is GenericPrimitive.CHANGE_ARITY:
        old = by_id[node_id]
        arity = int(arguments["arity"])
        if arity < 0 or arity > 8:
            raise ValueError("arity must be in 0..8")
        nodes = _replace_node(parent, node_id, Node(old.id, old.kind, {**old.attributes, "arity": arity}))
    elif operator is GenericPrimitive.BIND_ARGUMENT:
        position = int(arguments["position"])
        edges.append(Edge(other_id, f"argument_{position}", node_id))
    elif operator is GenericPrimitive.UNBIND_ARGUMENT:
        position = int(arguments["position"])
        edge = Edge(other_id, f"argument_{position}", node_id)
        if edge not in edges:
            raise ValueError("argument binding does not exist")
        edges.remove(edge)
    elif operator is GenericPrimitive.ADD_FUNCTION:
        if set(arguments) - {"id"}:
            raise ValueError("ADD_FUNCTION accepts only an optional id")
        nodes.append(Node(arguments.get("id") or _fresh_id(parent, "function", rng), NodeKind.FUNCTION))
    elif operator is GenericPrimitive.REMOVE_FUNCTION:
        old = by_id[node_id]
        if old.kind is not NodeKind.FUNCTION:
            raise ValueError("REMOVE_FUNCTION requires a Function node")
        nodes = [node for node in nodes if node.id != node_id]
        edges = [edge for edge in edges if edge.source != node_id and edge.target != node_id]
    elif operator is GenericPrimitive.ADD_EQUATION:
        if set(arguments) - {"id"}:
            raise ValueError("ADD_EQUATION accepts only an optional id")
        nodes.append(Node(arguments.get("id") or _fresh_id(parent, "equation", rng), NodeKind.EQUATION, {"family": "generic"}))
    elif operator is GenericPrimitive.REMOVE_EQUATION:
        old = by_id[node_id]
        if old.kind is not NodeKind.EQUATION:
            raise ValueError("REMOVE_EQUATION requires an Equation node")
        nodes = [node for node in nodes if node.id != node_id]
        edges = [edge for edge in edges if edge.source != node_id and edge.target != node_id]
    elif operator is GenericPrimitive.COMPOSE_FUNCTIONS:
        edges.append(Edge(node_id, "composes_into", other_id))
    elif operator is GenericPrimitive.DECOMPOSE_FUNCTION:
        edge = Edge(node_id, "composes_into", other_id)
        if edge not in edges:
            raise ValueError("composition edge does not exist")
        edges.remove(edge)
    elif operator is GenericPrimitive.ADD_TEMPORAL_INDEX:
        old = by_id[node_id]
        nodes = _replace_node(parent, node_id, Node(old.id, old.kind, {**old.attributes, "temporal_index": "t"}))
    elif operator is GenericPrimitive.REMOVE_TEMPORAL_INDEX:
        old = by_id[node_id]
        attrs = dict(old.attributes)
        if "temporal_index" not in attrs:
            raise ValueError("node has no temporal index")
        del attrs["temporal_index"]
        nodes = _replace_node(parent, node_id, Node(old.id, old.kind, attrs))
    elif operator is GenericPrimitive.ADD_DEPENDENCY:
        edges.append(Edge(node_id, "dependency", other_id))
    elif operator is GenericPrimitive.REMOVE_DEPENDENCY:
        edge = Edge(node_id, "dependency", other_id)
        if edge not in edges:
            raise ValueError("dependency does not exist")
        edges.remove(edge)
    elif operator is GenericPrimitive.ADD_CONSTRAINT:
        if set(arguments) - {"id"}:
            raise ValueError("ADD_CONSTRAINT accepts only an optional id")
        nodes.append(Node(arguments.get("id") or _fresh_id(parent, "constraint", rng), NodeKind.CONSTRAINT))
    elif operator is GenericPrimitive.REMOVE_CONSTRAINT:
        old = by_id[node_id]
        if old.kind is not NodeKind.CONSTRAINT:
            raise ValueError("REMOVE_CONSTRAINT requires a Constraint node")
        nodes = [node for node in nodes if node.id != node_id]
        edges = [edge for edge in edges if edge.source != node_id and edge.target != node_id]
    elif operator is GenericPrimitive.MERGE_NODES:
        first = by_id[node_id]
        merged_id = arguments.get("id") or _fresh_id(parent, "merged", rng)
        nodes = [node for node in nodes if node.id not in {node_id, other_id}]
        nodes.append(Node(merged_id, first.kind))
        edges = [
            Edge(
                merged_id if edge.source in {node_id, other_id} else edge.source,
                edge.relation,
                merged_id if edge.target in {node_id, other_id} else edge.target,
            )
            for edge in edges
        ]
        edges = list(dict.fromkeys(edges))
    elif operator is GenericPrimitive.SPLIT_NODE:
        old = by_id[node_id]
        left = arguments.get("left") or _fresh_id(parent, "split", rng)
        right = arguments.get("right") or _fresh_id(parent, "split", random.Random(seed ^ 0x51))
        if left == right:
            raise ValueError("split ids must differ")
        nodes = [node for node in nodes if node.id != node_id] + [Node(left, old.kind), Node(right, old.kind)]
        edges = [Edge(left if edge.source == node_id else edge.source, edge.relation, left if edge.target == node_id else edge.target) for edge in edges]
    elif operator is GenericPrimitive.REIFY_EDGE_AS_NODE:
        edge = Edge(node_id, relation, other_id)
        if edge not in edges:
            raise ValueError("edge does not exist")
        reified = arguments.get("id") or _fresh_id(parent, "reified", rng)
        edges.remove(edge)
        nodes.append(Node(reified, NodeKind.RELATION, {"arity": 2}))
        edges.extend((Edge(node_id, "argument_0", reified), Edge(reified, "result_of", other_id)))
    elif operator is GenericPrimitive.REIFY_NODE_AS_EDGE:
        old = by_id[node_id]
        incoming = [edge for edge in edges if edge.target == node_id]
        outgoing = [edge for edge in edges if edge.source == node_id]
        if not incoming or not outgoing:
            raise ValueError("reified node needs incoming and outgoing edges")
        nodes = [node for node in nodes if node.id != node_id]
        edges = [edge for edge in edges if edge.source != node_id and edge.target != node_id]
        edges.append(Edge(incoming[0].source, relation, outgoing[0].target))
    elif operator is GenericPrimitive.SUBGRAPH_COPY:
        old = by_id[node_id]
        copy_id = arguments.get("id") or _fresh_id(parent, "copy", rng)
        nodes.append(Node(copy_id, old.kind, old.attributes))
    elif operator is GenericPrimitive.SUBGRAPH_CROSSOVER:
        if donor is None:
            raise ValueError("SUBGRAPH_CROSSOVER requires a donor")
        donor_node = donor.node(str(arguments["donor_node"]))
        copy_id = arguments.get("id") or _fresh_id(parent, "cross", rng)
        nodes.append(Node(copy_id, donor_node.kind, donor_node.attributes))
    else:  # pragma: no cover
        raise ValueError(operator)

    child = Representation(tuple(nodes), tuple(edges))
    errors = child.validate()
    if errors:
        raise ValueError("invalid primitive result: " + "; ".join(errors))
    record = PrimitiveRecord(
        parent.structural_hash,
        child.structural_hash,
        operator,
        tuple(sorted((str(key), str(value)) for key, value in arguments.items())),
        seed,
        depth,
        donor.structural_hash if donor is not None else "",
    )
    return child, record


def compose(
    incumbent: Representation,
    steps: tuple[tuple[GenericPrimitive, Mapping[str, str]], ...],
    seed: int,
) -> ComposedRepresentation:
    current = incumbent
    records: list[PrimitiveRecord] = []
    for index, (operator, arguments) in enumerate(steps, start=1):
        current, record = apply_primitive(
            current, operator, arguments, seed + index - 1, depth=index
        )
        records.append(record)
    return ComposedRepresentation(current, tuple(records))
