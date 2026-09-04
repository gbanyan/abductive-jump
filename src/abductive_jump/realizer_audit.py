"""Counterfactual, inference-free audits of the compositional motif realizer."""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from typing import Any

from .compositional_experiment import _fit_for_condition, _prediction_table
from .compositional_realization import _motif
from .conditions import Condition
from .executable import evaluate_executable, freeze_theory, parse_theory
from .expressions import Expression
from .primary_experiment import _thresholds
from .realization import _clean, _evaluate_public, _solve_linear
from .representation import Edge, Node, NodeKind, Representation
from .worlds import PublicWorld, World

ALIGNED = "aligned"
MOTIF_DISABLED = "motif_disabled"
ROLE_BLIND = "role_action_blind_binding"
MASK_PREFIX = "mask_signature:"

REALIZER_SIGNATURES = (
    "relation_arity_3",
    "temporally_indexed_recurrence",
    "unobserved_dependency",
    "unobserved_selector",
    "bound_relation",
    "self_composed_function",
    "shared_rule_binding",
    "multi_argument_function",
)


@dataclass(frozen=True, slots=True)
class CounterfactualFit:
    expression: Expression
    observational_loss: float
    detected_signature: str
    realized_signature: str


def representation_from_json(raw: str) -> Representation:
    payload = json.loads(raw)
    nodes = tuple(
        Node(str(row["id"]), NodeKind(row["kind"]), dict(row.get("attributes", {})))
        for row in payload["nodes"]
    )
    edges = tuple(
        Edge(str(row["source"]), str(row["relation"]), str(row["target"]))
        for row in payload.get("edges", [])
    )
    return Representation(nodes, edges)


def _expression_from_terms(
    public: PublicWorld, terms: list[tuple[str, dict[str, Any]]]
) -> tuple[Expression, float]:
    matrix = [
        [_evaluate_public(tree, case["inputs"], case["intervention"]) for _, tree in terms]
        for case in public.observations
    ]
    targets = [float(case["outcome"]) for case in public.observations]
    coefficients = [_clean(value) for value in _solve_linear(matrix, targets)]
    pieces = [
        {
            "op": "mul",
            "left": {"op": "const", "value": coefficient},
            "right": tree,
        }
        for coefficient, (_, tree) in zip(coefficients, terms, strict=True)
    ]
    tree = pieces[0]
    for piece in pieces[1:]:
        tree = {"op": "add", "left": tree, "right": piece}
    expression = Expression(tree)
    predictions = [
        expression.evaluate(case["inputs"], case["intervention"]) for case in public.observations
    ]
    loss = sum(
        (prediction - target) ** 2 for prediction, target in zip(predictions, targets, strict=True)
    ) / len(targets)
    return expression, loss


def _variable_occurrences(tree: Any) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        operation = str(node.get("op", ""))
        if operation in {"var", "raw_var", "history_sum"}:
            item = (operation, str(node.get("name", "")))
            if item not in found:
                found.append(item)
        for key in ("arg", "left", "right", "then", "else"):
            if key in node:
                walk(node[key])

    walk(tree)
    return found


def _role_action_blind_terms(
    public: PublicWorld, terms: list[tuple[str, dict[str, Any]]]
) -> list[tuple[str, dict[str, Any]]]:
    """Rebind fields canonically without roles or intervention-key inspection.

    The algebraic form licensed by the detected motif is retained. Variable identities are
    replaced by type-compatible public fields in lexical order, using only observation field
    types and the preregistered nuisance list. This isolates the semantic field-binding prior
    from graph topology and coefficient fitting.
    """

    sample = public.observations[0]["inputs"]
    nuisances = set(public.known_nuisance_fields)
    scalar = sorted(
        name
        for name, value in sample.items()
        if name not in nuisances and not isinstance(value, (list, tuple))
    )
    sequences = sorted(
        name
        for name, value in sample.items()
        if name not in nuisances and isinstance(value, (list, tuple))
    )
    occurrences: list[tuple[str, str]] = []
    for _, tree in terms:
        for item in _variable_occurrences(tree):
            if item not in occurrences:
                occurrences.append(item)

    mapping: dict[tuple[str, str], str] = {}
    scalar_index = 0
    sequence_index = 0
    for operation, name in occurrences:
        if operation == "history_sum" or isinstance(sample.get(name), (list, tuple)):
            if sequences:
                mapping[(operation, name)] = sequences[sequence_index % len(sequences)]
                sequence_index += 1
        elif scalar:
            mapping[(operation, name)] = scalar[scalar_index % len(scalar)]
            scalar_index += 1

    def rewrite(node: Any) -> Any:
        if not isinstance(node, dict):
            return node
        result = {key: rewrite(value) for key, value in node.items()}
        operation = str(result.get("op", ""))
        key = (operation, str(result.get("name", "")))
        if key in mapping:
            result["name"] = mapping[key]
        return result

    return [(name, rewrite(copy.deepcopy(tree))) for name, tree in terms]


def fit_counterfactual(
    world: World, representation: Representation, policy: str
) -> CounterfactualFit:
    public = world.public()
    detected_signature, terms = _motif(public, representation)
    if policy == ALIGNED:
        expression, loss, realized = _fit_for_condition(
            world, Condition.C3_GENERIC_COMPOSITION, representation
        )
        return CounterfactualFit(expression, loss, detected_signature, realized)
    if policy == MOTIF_DISABLED or (
        policy.startswith(MASK_PREFIX) and detected_signature == policy.removeprefix(MASK_PREFIX)
    ):
        expression, loss, _ = _fit_for_condition(
            world, Condition.C3_GENERIC_COMPOSITION, public.incumbent
        )
        return CounterfactualFit(
            expression,
            loss,
            detected_signature,
            "incumbent_fallback",
        )
    if policy == ROLE_BLIND:
        if detected_signature == "incumbent_basis":
            expression, loss, realized = _fit_for_condition(
                world, Condition.C3_GENERIC_COMPOSITION, representation
            )
            return CounterfactualFit(expression, loss, detected_signature, realized)
        expression, loss = _expression_from_terms(public, _role_action_blind_terms(public, terms))
        return CounterfactualFit(
            expression,
            loss,
            detected_signature,
            f"{detected_signature}:role_action_blind",
        )
    if policy.startswith(MASK_PREFIX):
        expression, loss, realized = _fit_for_condition(
            world, Condition.C3_GENERIC_COMPOSITION, representation
        )
        return CounterfactualFit(expression, loss, detected_signature, realized)
    raise ValueError(f"unknown realizer policy: {policy}")


def evaluate_counterfactual(
    world: World,
    representation: Representation,
    policy: str,
    *,
    proposal_executable: bool = True,
    gate_thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fitted = fit_counterfactual(world, representation, policy)
    predictions = _prediction_table(world, fitted.expression)
    selected = max(
        predictions,
        key=lambda row: (float(row["absolute_separation"]), str(row["case_id"])),
    )
    theory = parse_theory(
        {
            "representation": representation.canonical_dict(),
            "expression": fitted.expression.tree,
            "explanation": "",
            "selected_intervention_ids": [selected["case_id"]],
        },
        {public: internal for internal, public in world.variable_names},
    )
    result = evaluate_executable(
        world,
        theory,
        freeze_theory(world, theory),
        _thresholds({"gate_thresholds": gate_thresholds}) if gate_thresholds else None,
    )
    row = asdict(result)
    row.update(
        {
            "policy": policy,
            "proposal_executable": proposal_executable,
            "representation_hash": representation.structural_hash,
            "detected_signature": fitted.detected_signature,
            "realized_signature": fitted.realized_signature,
            "selected_intervention_id": str(selected["case_id"]),
            "counterfactual_validated_jump": bool(proposal_executable and result.validated_jump),
        }
    )
    return row
