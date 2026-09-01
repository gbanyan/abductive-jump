from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .expressions import Expression
from .representation import NodeKind, Representation
from .worlds import PublicWorld


@dataclass(frozen=True, slots=True)
class FittedRealization:
    expression: Expression
    observational_loss: float
    basis_names: tuple[str, ...]
    coefficients: tuple[float, ...]


def _evaluate_public(tree: dict[str, Any], inputs: dict[str, Any], intervention: dict[str, Any]) -> float:
    return Expression(tree).evaluate(inputs, intervention)


def _solve_linear(matrix: list[list[float]], targets: list[float]) -> list[float]:
    width = len(matrix[0])
    normal = [
        [sum(row[i] * row[j] for row in matrix) for j in range(width)]
        + [sum(row[i] * target for row, target in zip(matrix, targets))]
        for i in range(width)
    ]
    for column in range(width):
        pivot = max(range(column, width), key=lambda row: abs(normal[row][column]))
        if abs(normal[pivot][column]) < 1e-10:
            raise ValueError("singular realization basis")
        normal[column], normal[pivot] = normal[pivot], normal[column]
        scale = normal[column][column]
        normal[column] = [value / scale for value in normal[column]]
        for row in range(width):
            if row == column:
                continue
            factor = normal[row][column]
            normal[row] = [left - factor * right for left, right in zip(normal[row], normal[column])]
    return [normal[row][-1] for row in range(width)]


def _clean(value: float) -> float:
    rounded = round(value)
    return float(rounded) if abs(value - rounded) < 1e-9 else float(format(value, ".12g"))


def fit_representation(public: PublicWorld, candidate: Representation) -> FittedRealization:
    """Fit a generic linear-in-basis hypothesis genome licensed by a typed representation."""
    observations = list(public.observations)
    nuisance = set(public.known_nuisance_fields)
    sample_inputs = observations[0]["inputs"]
    scalar_fields = [
        name
        for name, value in sample_inputs.items()
        if name not in nuisance and not isinstance(value, (list, tuple))
    ]
    sequence_fields = [
        name
        for name, value in sample_inputs.items()
        if name not in nuisance and isinstance(value, (list, tuple))
    ]
    role_to_id = {
        str(node.attributes.get("role")): node.id
        for node in candidate.nodes
        if node.attributes.get("role")
    }
    primary = role_to_id.get("input")
    if primary not in scalar_fields:
        primary = scalar_fields[0]
    context = role_to_id.get("context_zero")
    regime = role_to_id.get("regime")
    added_nodes = [node for node in candidate.nodes if node.id not in {old.id for old in public.incumbent.nodes}]
    added_kinds = {node.kind for node in added_nodes}
    added_attributes = {
        str(key): value for node in added_nodes for key, value in node.attributes.items()
    }

    terms: list[tuple[str, dict[str, Any]]] = []
    if NodeKind.STATE_VARIABLE in added_kinds and sequence_fields:
        terms = [(primary, {"op": "var", "name": primary})]
        terms += [
            (f"sum({name})", {"op": "history_sum", "name": name})
            for name in sequence_fields
        ]
    elif NodeKind.RELATION in added_kinds:
        terms = [(name, {"op": "var", "name": name}) for name in scalar_fields]
    elif added_attributes.get("transform") == "square":
        terms = [
            (
                f"{primary}^2",
                {
                    "op": "pow",
                    "left": {"op": "var", "name": primary},
                    "right": {"op": "const", "value": 2},
                },
            )
        ]
    elif added_attributes.get("form") == "affine_context" and context in scalar_fields:
        terms = [
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
    elif NodeKind.REGIME in added_kinds and regime in scalar_fields:
        terms = [
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
    elif NodeKind.LATENT_VARIABLE in added_kinds:
        intervened = {
            name
            for query in public.intervention_queries
            for name in query["intervention"]
        }
        stable = [name for name in scalar_fields if name not in intervened]
        latent_proxy = stable[0] if stable else primary
        terms = [(f"raw({latent_proxy})", {"op": "raw_var", "name": latent_proxy})]
    elif NodeKind.INVARIANT in added_kinds or NodeKind.FUNCTION in added_kinds:
        terms = [(primary, {"op": "var", "name": primary})]
    else:
        terms = [(name, {"op": "var", "name": name}) for name in scalar_fields[:2]]

    matrix = [
        [_evaluate_public(tree, case["inputs"], case["intervention"]) for _, tree in terms]
        for case in observations
    ]
    targets = [float(case["outcome"]) for case in observations]
    coefficients = [_clean(value) for value in _solve_linear(matrix, targets)]
    pieces = [
        {
            "op": "mul",
            "left": {"op": "const", "value": coefficient},
            "right": tree,
        }
        for coefficient, (_, tree) in zip(coefficients, terms)
    ]
    expression_tree = pieces[0]
    for piece in pieces[1:]:
        expression_tree = {"op": "add", "left": expression_tree, "right": piece}
    expression = Expression(expression_tree)
    predictions = [
        expression.evaluate(case["inputs"], case["intervention"])
        for case in observations
    ]
    observed_loss = sum((prediction - target) ** 2 for prediction, target in zip(predictions, targets)) / len(targets)
    return FittedRealization(
        expression,
        observed_loss,
        tuple(name for name, _ in terms),
        tuple(coefficients),
    )

