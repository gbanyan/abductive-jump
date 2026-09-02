from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .expressions import Expression
from .realization import _clean, _evaluate_public, _solve_linear
from .representation import Node, NodeKind, Representation
from .worlds import PublicWorld


@dataclass(frozen=True, slots=True)
class CompositionalFit:
    expression: Expression
    observational_loss: float
    basis_names: tuple[str, ...]
    coefficients: tuple[float, ...]
    structural_signature: str


def _argument_sources(candidate: Representation, node: Node) -> tuple[str, ...]:
    pairs: list[tuple[int, str]] = []
    for edge in candidate.edges:
        if edge.target != node.id or not edge.relation.startswith("argument_"):
            continue
        try:
            position = int(edge.relation.removeprefix("argument_"))
        except ValueError:
            continue
        pairs.append((position, edge.source))
    return tuple(source for _, source in sorted(pairs))


def _motif(
    public: PublicWorld, candidate: Representation
) -> tuple[str, list[tuple[str, dict[str, Any]]]]:
    incumbent_ids = {node.id for node in public.incumbent.nodes}
    added = [node for node in candidate.nodes if node.id not in incumbent_ids]
    roles = {
        str(node.attributes.get("role")): node.id
        for node in candidate.nodes
        if node.attributes.get("role")
    }
    sample = public.observations[0]["inputs"]
    nuisances = set(public.known_nuisance_fields)
    scalar = [
        name
        for name, value in sample.items()
        if name not in nuisances and not isinstance(value, (list, tuple))
    ]
    sequences = [
        name
        for name, value in sample.items()
        if name not in nuisances and isinstance(value, (list, tuple))
    ]
    primary = roles.get("input") if roles.get("input") in scalar else scalar[0]
    changed = {
        name
        for query in public.intervention_queries
        for name in query["intervention"]
    }
    secondary = [name for name in scalar if name != primary and name in changed]

    for node in added:
        args = _argument_sources(candidate, node)
        arity = int(node.attributes.get("arity", len(args)))
        if node.kind is NodeKind.RELATION and arity >= 3 and len(args) >= 3:
            names = [name for name in args if name in scalar][:3]
            if len(names) < 3:
                names = scalar[:3]
            if len(names) >= 3:
                tree = {
                    "op": "mul",
                    "left": {"op": "mul", "left": {"op": "var", "name": names[0]}, "right": {"op": "var", "name": names[1]}},
                    "right": {"op": "var", "name": names[2]},
                }
                return "relation_arity_3", [("triadic_product", tree)]
        if node.kind is NodeKind.STATE_VARIABLE and node.attributes.get("temporal_index"):
            recurrent = any(
                edge.source == node.id
                and edge.target == node.id
                and edge.relation == "dependency"
                for edge in candidate.edges
            )
            if recurrent and sequences:
                return "temporally_indexed_recurrence", [
                    (primary, {"op": "var", "name": primary}),
                    *[(f"sum({name})", {"op": "history_sum", "name": name}) for name in sequences],
                ]
        if node.kind is NodeKind.LATENT_VARIABLE and node.attributes.get("observable") is False:
            has_dependency = any(
                edge.source == node.id and edge.relation == "dependency"
                for edge in candidate.edges
            )
            if has_dependency:
                stable = [name for name in scalar if name not in changed]
                proxy = stable[0] if stable else primary
                return "unobserved_dependency", [(f"raw({proxy})", {"op": "raw_var", "name": proxy})]
        if node.kind is NodeKind.REGIME and node.attributes.get("observable") is False:
            has_dependency = any(
                edge.source == node.id and edge.relation == "dependency"
                for edge in candidate.edges
            )
            if has_dependency and secondary:
                regime = secondary[0]
                return "unobserved_selector", [
                    (
                        f"signed({primary},{regime})",
                        {
                            "op": "mul",
                            "left": {"op": "var", "name": primary},
                            "right": {
                                "op": "if_eq",
                                "left": {"op": "var", "name": regime},
                                "right": {"op": "const", "value": 1},
                                "then": {"op": "const", "value": -1},
                                "else": {"op": "const", "value": 1},
                            },
                        },
                    )
                ]
        if node.kind is NodeKind.RELATION and arity >= 2 and args:
            return "bound_relation", [(name, {"op": "var", "name": name}) for name in scalar]
        if node.kind is NodeKind.FUNCTION:
            self_composed = any(
                edge.source == node.id
                and edge.target == node.id
                and edge.relation == "composes_into"
                for edge in candidate.edges
            )
            if self_composed:
                return "self_composed_function", [
                    (
                        f"{primary}^2",
                        {
                            "op": "pow",
                            "left": {"op": "var", "name": primary},
                            "right": {"op": "const", "value": 2},
                        },
                    )
                ]
            bound_kinds = {
                candidate.node(source).kind for source in args if source in {n.id for n in candidate.nodes}
            }
            if len(args) >= 2 and bound_kinds == {NodeKind.EQUATION}:
                context = roles.get("context_zero")
                terms = [(primary, {"op": "var", "name": primary})]
                if context in scalar:
                    terms.append((context, {"op": "var", "name": context}))
                return "shared_rule_binding", terms
            context = roles.get("context_zero")
            if arity >= 2 and len(args) >= 2 and context in scalar:
                return "multi_argument_function", [
                    (primary, {"op": "var", "name": primary}),
                    (
                        f"{primary}*{context}",
                        {
                            "op": "mul",
                            "left": {"op": "var", "name": primary},
                            "right": {"op": "var", "name": context},
                        },
                    ),
                ]

    return "incumbent_basis", [(name, {"op": "var", "name": name}) for name in scalar[:2]]


def fit_composed_representation(
    public: PublicWorld, candidate: Representation
) -> CompositionalFit:
    signature, terms = _motif(public, candidate)
    matrix = [
        [_evaluate_public(tree, case["inputs"], case["intervention"]) for _, tree in terms]
        for case in public.observations
    ]
    targets = [float(case["outcome"]) for case in public.observations]
    coefficients = [_clean(value) for value in _solve_linear(matrix, targets)]
    pieces = [
        {"op": "mul", "left": {"op": "const", "value": coefficient}, "right": tree}
        for coefficient, (_, tree) in zip(coefficients, terms)
    ]
    expression_tree = pieces[0]
    for piece in pieces[1:]:
        expression_tree = {"op": "add", "left": expression_tree, "right": piece}
    expression = Expression(expression_tree)
    predictions = [
        expression.evaluate(case["inputs"], case["intervention"])
        for case in public.observations
    ]
    loss = sum((prediction - target) ** 2 for prediction, target in zip(predictions, targets)) / len(targets)
    return CompositionalFit(
        expression,
        loss,
        tuple(name for name, _ in terms),
        tuple(coefficients),
        signature,
    )
