from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Any


class NodeKind(StrEnum):
    PRIMITIVE = "Primitive"
    OBSERVABLE = "Observable"
    LATENT_VARIABLE = "LatentVariable"
    STATE_VARIABLE = "StateVariable"
    ENTITY = "Entity"
    PROPERTY = "Property"
    RELATION = "Relation"
    PROCESS = "Process"
    CONTEXT = "Context"
    REGIME = "Regime"
    PARAMETER = "Parameter"
    FUNCTION = "Function"
    EQUATION = "Equation"
    INVARIANT = "Invariant"
    CAUSAL_EDGE = "CausalEdge"
    TRANSITION = "Transition"
    CONSTRAINT = "Constraint"


JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def _normalize(value: Any) -> JsonValue:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite numbers are forbidden")
        return 0.0 if value == 0 else float(format(value, ".15g"))
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, Mapping):
        return {str(k): _normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class Node:
    id: str
    kind: NodeKind
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def canonical(self) -> dict[str, JsonValue]:
        if not self.id or any(ch.isspace() for ch in self.id):
            raise ValueError(f"invalid node id: {self.id!r}")
        return {"id": self.id, "kind": self.kind.value, "attributes": _normalize(self.attributes)}


@dataclass(frozen=True, slots=True, order=True)
class Edge:
    source: str
    relation: str
    target: str

    def canonical(self) -> dict[str, str]:
        return {"source": self.source, "relation": self.relation, "target": self.target}


@dataclass(frozen=True, slots=True)
class Representation:
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...] = ()
    schema_version: str = "1"

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        ids = [node.id for node in self.nodes]
        if len(ids) != len(set(ids)):
            errors.append("duplicate node id")
        known = set(ids)
        for node in self.nodes:
            try:
                node.canonical()
            except (TypeError, ValueError) as exc:
                errors.append(str(exc))
        for edge in self.edges:
            if edge.source not in known or edge.target not in known:
                errors.append(f"dangling edge {edge.source}-{edge.relation}->{edge.target}")
            if not edge.relation:
                errors.append("empty edge relation")
        if len(self.edges) != len(set(self.edges)):
            errors.append("duplicate edge")
        return tuple(sorted(set(errors)))

    def canonical_dict(self) -> dict[str, JsonValue]:
        errors = self.validate()
        if errors:
            raise ValueError("; ".join(errors))
        nodes = sorted((node.canonical() for node in self.nodes), key=lambda x: (x["kind"], x["id"]))
        edges = sorted((edge.canonical() for edge in self.edges), key=lambda x: (x["source"], x["relation"], x["target"]))
        return {"schema_version": self.schema_version, "nodes": nodes, "edges": edges}

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @property
    def structural_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()

    def node(self, node_id: str) -> Node:
        return next(node for node in self.nodes if node.id == node_id)

    def replace_node(self, node_id: str, **changes: Any) -> Representation:
        return replace(self, nodes=tuple(replace(n, **changes) if n.id == node_id else n for n in self.nodes))


@dataclass(frozen=True, slots=True)
class LanguageSpec:
    allowed_kinds: frozenset[NodeKind]
    max_kind_counts: Mapping[NodeKind, int]
    allowed_relations: frozenset[str]
    allowed_edge_signatures: frozenset[tuple[NodeKind, str, NodeKind]] = frozenset()
    allowed_equation_families: frozenset[str] = frozenset()

    def membership_failures(self, representation: Representation) -> tuple[str, ...]:
        failures = list(representation.validate())
        counts: dict[NodeKind, int] = {}
        by_id = {node.id: node for node in representation.nodes}
        for node in representation.nodes:
            counts[node.kind] = counts.get(node.kind, 0) + 1
            if node.kind not in self.allowed_kinds:
                failures.append(f"kind:{node.kind.value}")
            if node.kind is NodeKind.EQUATION:
                family = str(node.attributes.get("family", ""))
                if family not in self.allowed_equation_families:
                    failures.append(f"equation_family:{family}")
        for kind, count in counts.items():
            if count > self.max_kind_counts.get(kind, 0):
                failures.append(f"count:{kind.value}:{count}")
        for edge in representation.edges:
            if edge.relation not in self.allowed_relations:
                failures.append(f"relation:{edge.relation}")
            elif self.allowed_edge_signatures:
                signature = (by_id[edge.source].kind, edge.relation, by_id[edge.target].kind)
                if signature not in self.allowed_edge_signatures:
                    failures.append("edge_signature:" + ":".join(x.value if isinstance(x, NodeKind) else x for x in signature))
        return tuple(sorted(set(failures)))

    def contains(self, representation: Representation) -> bool:
        return not self.membership_failures(representation)


def structural_descriptor(representation: Representation) -> tuple[tuple[str, int], ...]:
    counts: dict[str, int] = {}
    for node in representation.nodes:
        counts[node.kind.value] = counts.get(node.kind.value, 0) + 1
    relation_arities: dict[str, int] = {}
    for edge in representation.edges:
        relation_arities[edge.relation] = relation_arities.get(edge.relation, 0) + 1
    values = {**counts, **{f"edge:{k}": v for k, v in relation_arities.items()}}
    return tuple(sorted(values.items()))


def representation(nodes: Iterable[Node], edges: Iterable[Edge] = ()) -> Representation:
    return Representation(tuple(nodes), tuple(edges))

