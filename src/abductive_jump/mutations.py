from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from .representation import Edge, Node, NodeKind, Representation


class MutationOperator(StrEnum):
    ADD_NODE = "ADD_NODE"
    REMOVE_NODE = "REMOVE_NODE"
    SPLIT_NODE = "SPLIT_NODE"
    MERGE_NODES = "MERGE_NODES"
    ADD_RELATION = "ADD_RELATION"
    REMOVE_RELATION = "REMOVE_RELATION"
    REVERSE_EDGE = "REVERSE_EDGE"
    REIFY_RELATION = "REIFY_RELATION"
    LATENTIZE = "LATENTIZE"
    OBSERVABILIZE = "OBSERVABILIZE"
    CONSTANT_TO_VARIABLE = "CONSTANT_TO_VARIABLE"
    VARIABLE_TO_FUNCTION = "VARIABLE_TO_FUNCTION"
    PROPERTY_TO_RELATION = "PROPERTY_TO_RELATION"
    ADD_STATE = "ADD_STATE"
    REMOVE_STATE = "REMOVE_STATE"
    ADD_REGIME = "ADD_REGIME"
    MERGE_RULES = "MERGE_RULES"
    SPLIT_RULE = "SPLIT_RULE"
    ADD_INVARIANT = "ADD_INVARIANT"
    BREAK_INVARIANT = "BREAK_INVARIANT"
    COMPOSE = "COMPOSE"
    SUBGRAPH_CROSSOVER = "SUBGRAPH_CROSSOVER"


@dataclass(frozen=True, slots=True)
class MutationRecord:
    parent_hash: str
    operator: MutationOperator
    arguments: tuple[tuple[str, str], ...]
    seed: int
    child_hash: str
    created_at_utc: str


def _fresh_id(rep: Representation, prefix: str, rng: random.Random) -> str:
    known = {n.id for n in rep.nodes}
    while True:
        candidate = f"{prefix}_{rng.randrange(1_000_000):06d}"
        if candidate not in known:
            return candidate


def mutate(
    parent: Representation,
    operator: MutationOperator,
    arguments: Mapping[str, str],
    seed: int,
    *,
    donor: Representation | None = None,
) -> tuple[Representation, MutationRecord]:
    """Apply a family-blind structural operator; arguments are recorded canonically."""
    rng = random.Random(seed)
    nodes, edges = list(parent.nodes), list(parent.edges)
    by_id = {n.id: n for n in nodes}
    node_id = arguments.get("node", "")
    other_id = arguments.get("other", "")

    if operator is MutationOperator.ADD_NODE:
        kind = NodeKind(arguments.get("kind", NodeKind.PRIMITIVE.value))
        attributes = {
            key.removeprefix("attr_"): value
            for key, value in arguments.items()
            if key.startswith("attr_")
        }
        nodes.append(
            Node(
                arguments.get("id") or _fresh_id(parent, kind.value.lower(), rng),
                kind,
                attributes,
            )
        )
    elif operator is MutationOperator.REMOVE_NODE:
        nodes = [n for n in nodes if n.id != node_id]
        edges = [e for e in edges if e.source != node_id and e.target != node_id]
    elif operator is MutationOperator.SPLIT_NODE:
        old = by_id[node_id]
        a, b = _fresh_id(parent, old.id + "a", rng), _fresh_id(parent, old.id + "b", rng)
        nodes = [n for n in nodes if n.id != node_id] + [Node(a, old.kind, old.attributes), Node(b, old.kind, old.attributes)]
        edges = [Edge(a if e.source == node_id else e.source, e.relation, a if e.target == node_id else e.target) for e in edges]
    elif operator is MutationOperator.MERGE_NODES:
        first, second = by_id[node_id], by_id[other_id]
        merged = arguments.get("id") or _fresh_id(parent, "merged", rng)
        nodes = [n for n in nodes if n.id not in {first.id, second.id}] + [Node(merged, first.kind)]
        edges = [Edge(merged if e.source in {first.id, second.id} else e.source, e.relation, merged if e.target in {first.id, second.id} else e.target) for e in edges]
        edges = list(dict.fromkeys(edges))
    elif operator is MutationOperator.ADD_RELATION:
        edges.append(Edge(node_id, arguments.get("relation", "relates"), other_id))
    elif operator is MutationOperator.REMOVE_RELATION:
        edge = Edge(node_id, arguments.get("relation", "relates"), other_id)
        edges = [e for e in edges if e != edge]
    elif operator is MutationOperator.REVERSE_EDGE:
        relation = arguments.get("relation", "relates")
        edge = Edge(node_id, relation, other_id)
        edges = [Edge(other_id, relation, node_id) if e == edge else e for e in edges]
    elif operator is MutationOperator.REIFY_RELATION:
        relation = arguments.get("relation", "relates")
        edge = Edge(node_id, relation, other_id)
        rid = arguments.get("id") or _fresh_id(parent, "relation", rng)
        edges = [e for e in edges if e != edge] + [Edge(node_id, "source_of", rid), Edge(rid, "target_of", other_id)]
        nodes.append(Node(rid, NodeKind.RELATION, {"reified": relation}))
    elif operator in {MutationOperator.LATENTIZE, MutationOperator.OBSERVABILIZE, MutationOperator.VARIABLE_TO_FUNCTION, MutationOperator.PROPERTY_TO_RELATION}:
        target_kind = {
            MutationOperator.LATENTIZE: NodeKind.LATENT_VARIABLE,
            MutationOperator.OBSERVABILIZE: NodeKind.OBSERVABLE,
            MutationOperator.VARIABLE_TO_FUNCTION: NodeKind.FUNCTION,
            MutationOperator.PROPERTY_TO_RELATION: NodeKind.RELATION,
        }[operator]
        nodes = [Node(n.id, target_kind, n.attributes) if n.id == node_id else n for n in nodes]
    elif operator is MutationOperator.CONSTANT_TO_VARIABLE:
        new_id = arguments.get("id") or _fresh_id(parent, "variable", rng)
        nodes.append(Node(new_id, NodeKind.PARAMETER, {"source_constant": arguments.get("value", "") }))
    elif operator is MutationOperator.ADD_STATE:
        sid = arguments.get("id") or _fresh_id(parent, "state", rng)
        nodes.append(Node(sid, NodeKind.STATE_VARIABLE))
        edges.append(Edge(sid, "transitions", sid))
    elif operator is MutationOperator.REMOVE_STATE:
        nodes = [n for n in nodes if not (n.id == node_id and n.kind is NodeKind.STATE_VARIABLE)]
        edges = [e for e in edges if e.source != node_id and e.target != node_id]
    elif operator is MutationOperator.ADD_REGIME:
        nodes.append(Node(arguments.get("id") or _fresh_id(parent, "regime", rng), NodeKind.REGIME))
    elif operator in {MutationOperator.MERGE_RULES, MutationOperator.COMPOSE}:
        nid = arguments.get("id") or _fresh_id(parent, "composed", rng)
        nodes.append(Node(nid, NodeKind.FUNCTION, {"operation": operator.value}))
        for source in filter(None, (node_id, other_id)):
            edges.append(Edge(source, "composes_into", nid))
    elif operator is MutationOperator.SPLIT_RULE:
        old = by_id[node_id]
        if old.kind not in {NodeKind.FUNCTION, NodeKind.EQUATION, NodeKind.PROCESS}:
            raise ValueError("SPLIT_RULE requires a rule-like node")
        a, b = _fresh_id(parent, "rule", rng), _fresh_id(parent, "rule", rng)
        nodes += [Node(a, old.kind, old.attributes), Node(b, old.kind, old.attributes)]
    elif operator is MutationOperator.ADD_INVARIANT:
        nodes.append(Node(arguments.get("id") or _fresh_id(parent, "invariant", rng), NodeKind.INVARIANT))
    elif operator is MutationOperator.BREAK_INVARIANT:
        nodes = [n for n in nodes if not (n.id == node_id and n.kind is NodeKind.INVARIANT)]
        edges = [e for e in edges if e.source != node_id and e.target != node_id]
    elif operator is MutationOperator.SUBGRAPH_CROSSOVER:
        if donor is None:
            raise ValueError("SUBGRAPH_CROSSOVER requires donor")
        existing = {n.id for n in nodes}
        for n in donor.nodes:
            if n.id not in existing:
                nodes.append(n)
        known = {n.id for n in nodes}
        edges.extend(e for e in donor.edges if e.source in known and e.target in known and e not in edges)
    else:  # pragma: no cover - exhaustive enum guard
        raise ValueError(operator)

    child = Representation(tuple(nodes), tuple(edges))
    errors = child.validate()
    if errors:
        raise ValueError("invalid mutation result: " + "; ".join(errors))
    record = MutationRecord(
        parent.structural_hash,
        operator,
        tuple(sorted((str(k), str(v)) for k, v in arguments.items())),
        seed,
        child.structural_hash,
        datetime.now(UTC).isoformat(),
    )
    return child, record
