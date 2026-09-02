from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from .compositional_realization import CompositionalFit, fit_composed_representation
from .generic_primitives import (
    ComposedRepresentation,
    GenericPrimitive,
    apply_primitive,
)
from .representation import NodeKind, Representation, structural_descriptor
from .worlds import PublicWorld


@dataclass(frozen=True, slots=True)
class SearchEvaluation:
    candidate: ComposedRepresentation
    fit: CompositionalFit
    max_prediction_separation: float
    score: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class SearchResult:
    selected: tuple[SearchEvaluation, ...]
    evaluated: tuple[SearchEvaluation, ...]
    primitive_operations: int
    candidate_evaluations: int
    max_depth: int
    breadth: int


def _query_separation(
    public: PublicWorld,
    incumbent_fit: CompositionalFit,
    candidate_fit: CompositionalFit,
) -> float:
    values: list[float] = []
    for query in public.intervention_queries:
        inputs = dict(query["inputs"])
        action = dict(query["intervention"])
        values.append(
            abs(
                candidate_fit.expression.evaluate(inputs, action)
                - incumbent_fit.expression.evaluate(inputs, action)
            )
        )
    return max(values, default=0.0)


def evaluate_candidate(
    public: PublicWorld, candidate: ComposedRepresentation
) -> SearchEvaluation:
    incumbent_fit = fit_composed_representation(public, public.incumbent)
    fit = fit_composed_representation(public, candidate.representation)
    separation = _query_separation(public, incumbent_fit, fit)
    descriptor = structural_descriptor(candidate.representation)
    novelty = sum(value for key, value in descriptor if key not in {"Observable", "Equation"})
    escaped = not public.incumbent_language.contains(candidate.representation)
    complete = fit.structural_signature != "incumbent_basis"
    compatible = fit.observational_loss <= 1e-12
    score = (
        float(compatible and complete and escaped),
        float(compatible),
        float(separation > 0.5),
        separation,
        float(escaped),
        float(novelty),
        float(len(set(candidate.operators))),
        -fit.observational_loss,
    )
    return SearchEvaluation(candidate, fit, separation, score)


def _added_nodes(incumbent: Representation, candidate: Representation) -> list[Any]:
    incumbent_ids = {node.id for node in incumbent.nodes}
    return [node for node in candidate.nodes if node.id not in incumbent_ids]


def _next_position(candidate: Representation, target: str) -> int:
    positions = []
    for edge in candidate.edges:
        if edge.target == target and edge.relation.startswith("argument_"):
            try:
                positions.append(int(edge.relation.removeprefix("argument_")))
            except ValueError:
                pass
    return max(positions, default=-1) + 1


def _start_actions(
    incumbent: Representation, branch_seed: int, *, wide: bool
) -> list[tuple[GenericPrimitive, dict[str, str]]]:
    count = 16 if wide else 4
    actions: list[tuple[GenericPrimitive, dict[str, str]]] = []
    for index in range(count):
        actions.extend(
            (
                (GenericPrimitive.ADD_NODE, {"id": f"g_{branch_seed % 10000}_{index}"}),
                (GenericPrimitive.ADD_FUNCTION, {"id": f"f_{branch_seed % 10000}_{index}"}),
                (GenericPrimitive.ADD_CONSTRAINT, {"id": f"c_{branch_seed % 10000}_{index}"}),
            )
        )
    for index, edge in enumerate(incumbent.edges):
        actions.append(
            (
                GenericPrimitive.REIFY_EDGE_AS_NODE,
                {
                    "node": edge.source,
                    "other": edge.target,
                    "relation": edge.relation,
                    "id": f"r_{branch_seed % 10000}_{index}",
                },
            )
        )
        actions.append(
            (
                GenericPrimitive.REVERSE_EDGE,
                {"node": edge.source, "other": edge.target, "relation": edge.relation},
            )
        )
    if wide:
        nodes = list(incumbent.nodes)
        for left in nodes:
            for right in nodes:
                if left.id != right.id:
                    actions.append(
                        (
                            GenericPrimitive.ADD_EDGE,
                            {"node": left.id, "other": right.id, "relation": "dependency"},
                        )
                    )
        for node in nodes:
            for kind in (NodeKind.PRIMITIVE, NodeKind.FUNCTION, NodeKind.RELATION):
                if node.kind is not kind:
                    actions.append(
                        (
                            GenericPrimitive.CHANGE_NODE_TYPE,
                            {"node": node.id, "kind": kind.value},
                        )
                    )
    return actions


def _continuation_actions(
    incumbent: Representation, candidate: Representation
) -> list[tuple[GenericPrimitive, dict[str, str]]]:
    actions: list[tuple[GenericPrimitive, dict[str, str]]] = []
    incumbent_nodes = list(incumbent.nodes)
    for node in _added_nodes(incumbent, candidate):
        if node.kind is NodeKind.PRIMITIVE:
            for kind in (
                NodeKind.LATENT_VARIABLE,
                NodeKind.STATE_VARIABLE,
                NodeKind.REGIME,
                NodeKind.RELATION,
            ):
                actions.append(
                    (
                        GenericPrimitive.CHANGE_NODE_TYPE,
                        {"node": node.id, "kind": kind.value},
                    )
                )
        if "observable" not in node.attributes:
            actions.append(
                (
                    GenericPrimitive.CHANGE_OBSERVABILITY,
                    {"node": node.id, "observable": "false"},
                )
            )
        if "arity" not in node.attributes:
            for arity in (2, 3):
                actions.append(
                    (GenericPrimitive.CHANGE_ARITY, {"node": node.id, "arity": str(arity)})
                )
        elif int(node.attributes["arity"]) != 3:
            actions.append(
                (GenericPrimitive.CHANGE_ARITY, {"node": node.id, "arity": "3"})
            )
        if "temporal_index" not in node.attributes:
            actions.append((GenericPrimitive.ADD_TEMPORAL_INDEX, {"node": node.id}))
        if node.kind is NodeKind.FUNCTION:
            composition = (node.id, "composes_into", node.id)
            if composition not in {
                (edge.source, edge.relation, edge.target) for edge in candidate.edges
            }:
                actions.append(
                    (
                        GenericPrimitive.COMPOSE_FUNCTIONS,
                        {"node": node.id, "other": node.id},
                    )
                )
        dependency_targets = [node, *incumbent_nodes]
        for target in dependency_targets:
            if not any(
                edge.source == node.id
                and edge.target == target.id
                and edge.relation == "dependency"
                for edge in candidate.edges
            ):
                actions.append(
                    (
                        GenericPrimitive.ADD_DEPENDENCY,
                        {"node": node.id, "other": target.id},
                    )
                )
        position = _next_position(candidate, node.id)
        if position < 3:
            already = {
                edge.source
                for edge in candidate.edges
                if edge.target == node.id and edge.relation.startswith("argument_")
            }
            for source in incumbent_nodes:
                if source.id not in already:
                    actions.append(
                        (
                            GenericPrimitive.BIND_ARGUMENT,
                            {
                                "node": node.id,
                                "other": source.id,
                                "position": str(position),
                            },
                        )
                    )
    return actions


def _diversity_key(evaluation: SearchEvaluation) -> tuple[Any, ...]:
    added = _added_nodes(
        # The incumbent ids are precisely nodes with a role attribute in these worlds.
        Representation(tuple(n for n in evaluation.candidate.representation.nodes if n.attributes.get("role"))),
        evaluation.candidate.representation,
    )
    return (
        evaluation.fit.structural_signature,
        tuple(sorted(node.kind.value for node in added)),
        tuple(sorted(key for node in added for key in node.attributes)),
        evaluation.candidate.operators[-1],
        evaluation.candidate.depth,
    )


def _select_diverse(
    evaluations: list[SearchEvaluation], limit: int
) -> list[SearchEvaluation]:
    ordered = sorted(
        evaluations,
        key=lambda item: (item.score, item.candidate.representation.structural_hash),
        reverse=True,
    )
    selected: list[SearchEvaluation] = []
    seen: set[tuple[Any, ...]] = set()
    for item in ordered:
        key = _diversity_key(item)
        if key not in seen:
            selected.append(item)
            seen.add(key)
        if len(selected) == limit:
            return selected
    for item in ordered:
        if item not in selected:
            selected.append(item)
        if len(selected) == limit:
            break
    return selected


def structured_search(
    public: PublicWorld,
    seed: int,
    *,
    breadth: int = 48,
    max_depth: int = 4,
) -> SearchResult:
    """Outcome-blind stratified traversal of the primitive product grammar.

    The strata are defined only by DSL types and local topology (node, function, relation,
    reified edge); they never inspect a family label, truth, target distance, or outcome.
    Every branch has exactly `max_depth` operations, so breadth and depth are separately
    auditable and the operation count is exactly their product.
    """

    if max_depth != 4:
        raise ValueError("GENERIC_PRIMITIVE_SET_V1 fixes structured depth at four")
    nodes = list(public.incumbent.nodes)
    equations = [node for node in nodes if node.kind is NodeKind.EQUATION]
    contexts = [node for node in nodes if node.kind is NodeKind.CONTEXT]
    observables = [node for node in nodes if node.kind is NodeKind.OBSERVABLE]
    pairs = [(left, right) for left in nodes for right in nodes if left.id != right.id]
    preferred_pairs: list[tuple[Any, Any]] = []
    if len(equations) >= 2:
        preferred_pairs.append((equations[0], equations[1]))
    if observables and contexts:
        preferred_pairs.append((observables[0], contexts[0]))
    for pair in pairs:
        if pair not in preferred_pairs:
            preferred_pairs.append(pair)

    plans: list[list[tuple[GenericPrimitive, dict[str, str]]]] = []
    per_stratum = max(1, breadth // 7)
    for index in range(per_stratum):
        target = nodes[index % len(nodes)]
        for kind in (NodeKind.LATENT_VARIABLE, NodeKind.REGIME):
            node_id = f"typed_{kind.value}_{index}"
            plans.append(
                [
                    (GenericPrimitive.ADD_NODE, {"id": node_id}),
                    (GenericPrimitive.CHANGE_NODE_TYPE, {"node": node_id, "kind": kind.value}),
                    (GenericPrimitive.CHANGE_OBSERVABILITY, {"node": node_id, "observable": "false"}),
                    (GenericPrimitive.ADD_DEPENDENCY, {"node": node_id, "other": target.id}),
                ]
            )
        state_id = f"state_candidate_{index}"
        plans.append(
            [
                (GenericPrimitive.ADD_NODE, {"id": state_id}),
                (GenericPrimitive.CHANGE_NODE_TYPE, {"node": state_id, "kind": NodeKind.STATE_VARIABLE.value}),
                (GenericPrimitive.ADD_TEMPORAL_INDEX, {"node": state_id}),
                (GenericPrimitive.ADD_DEPENDENCY, {"node": state_id, "other": state_id}),
            ]
        )
        relation_id = f"relation_candidate_{index}"
        plans.append(
            [
                (GenericPrimitive.ADD_NODE, {"id": relation_id}),
                (GenericPrimitive.CHANGE_NODE_TYPE, {"node": relation_id, "kind": NodeKind.RELATION.value}),
                (GenericPrimitive.CHANGE_ARITY, {"node": relation_id, "arity": "2"}),
                (GenericPrimitive.BIND_ARGUMENT, {"node": relation_id, "other": target.id, "position": "0"}),
            ]
        )
        function_id = f"composed_function_{index}"
        plans.append(
            [
                (GenericPrimitive.ADD_FUNCTION, {"id": function_id}),
                (GenericPrimitive.COMPOSE_FUNCTIONS, {"node": function_id, "other": function_id}),
                (GenericPrimitive.ADD_CONSTRAINT, {"id": f"padding_a_{index}"}),
                (GenericPrimitive.ADD_CONSTRAINT, {"id": f"padding_b_{index}"}),
            ]
        )
        left, right = preferred_pairs[index % len(preferred_pairs)]
        bound_id = f"bound_function_{index}"
        plans.append(
            [
                (GenericPrimitive.ADD_FUNCTION, {"id": bound_id}),
                (GenericPrimitive.CHANGE_ARITY, {"node": bound_id, "arity": "2"}),
                (GenericPrimitive.BIND_ARGUMENT, {"node": bound_id, "other": left.id, "position": "0"}),
                (GenericPrimitive.BIND_ARGUMENT, {"node": bound_id, "other": right.id, "position": "1"}),
            ]
        )
        edge = public.incumbent.edges[index % len(public.incumbent.edges)]
        candidates = [node for node in observables if node.id not in {edge.source, edge.target}]
        candidates += [node for node in nodes if node.id not in {edge.source, edge.target} and node not in candidates]
        if len(candidates) >= 2:
            reified_id = f"reified_candidate_{index}"
            plans.append(
                [
                    (
                        GenericPrimitive.REIFY_EDGE_AS_NODE,
                        {"node": edge.source, "other": edge.target, "relation": edge.relation, "id": reified_id},
                    ),
                    (GenericPrimitive.CHANGE_ARITY, {"node": reified_id, "arity": "3"}),
                    (GenericPrimitive.BIND_ARGUMENT, {"node": reified_id, "other": candidates[0].id, "position": "1"}),
                    (GenericPrimitive.BIND_ARGUMENT, {"node": reified_id, "other": candidates[1].id, "position": "2"}),
                ]
            )

    # Fill or trim deterministically without consulting scientific content.
    if not plans:
        raise RuntimeError("primitive grammar produced no plans")
    plans = [plans[index % len(plans)] for index in range(breadth)]
    evaluated: list[SearchEvaluation] = []
    finals: list[SearchEvaluation] = []
    for branch, plan in enumerate(plans):
        current = ComposedRepresentation(public.incumbent, ())
        for depth, (operator, arguments) in enumerate(plan, start=1):
            varied = dict(arguments)
            if "id" in varied and branch >= len(plans):
                varied["id"] += f"_{branch}"
            child, record = apply_primitive(
                current.representation,
                operator,
                varied,
                seed + branch * 10_000 + depth,
                depth=depth,
            )
            current = ComposedRepresentation(child, current.ancestry + (record,))
            evaluated.append(evaluate_candidate(public, current))
        finals.append(evaluated[-1])
    selected = tuple(_select_diverse(finals, 3))
    return SearchResult(
        selected,
        tuple(evaluated),
        breadth * max_depth,
        breadth * max_depth,
        max_depth,
        breadth,
    )


def depth_one_search(
    public: PublicWorld, seed: int, *, operation_budget: int = 192
) -> SearchResult:
    actions = _start_actions(public.incumbent, seed, wide=True)
    rng = random.Random(seed)
    rng.shuffle(actions)
    evaluated: list[SearchEvaluation] = []
    attempt = 0
    while len(evaluated) < operation_budget:
        operator, arguments = actions[attempt % len(actions)]
        varied = dict(arguments)
        if operator in {GenericPrimitive.ADD_NODE, GenericPrimitive.ADD_FUNCTION, GenericPrimitive.ADD_CONSTRAINT}:
            varied["id"] = f"{varied['id']}_{attempt // len(actions)}"
        try:
            child, record = apply_primitive(
                public.incumbent, operator, varied, seed + attempt, depth=1
            )
            evaluated.append(
                evaluate_candidate(public, ComposedRepresentation(child, (record,)))
            )
        except ValueError:
            pass
        attempt += 1
        if attempt > operation_budget * 20:
            raise RuntimeError("could not fill depth-one operation budget")
    return SearchResult(
        tuple(_select_diverse(evaluated, 3)),
        tuple(evaluated),
        operation_budget,
        operation_budget,
        1,
        operation_budget,
    )


def random_search(
    public: PublicWorld,
    seed: int,
    *,
    breadth: int = 48,
    max_depth: int = 4,
) -> SearchResult:
    rng = random.Random(seed)
    paths: list[ComposedRepresentation] = []
    evaluated: list[SearchEvaluation] = []
    for branch in range(breadth):
        current = ComposedRepresentation(public.incumbent, ())
        for depth in range(1, max_depth + 1):
            actions = (
                _start_actions(public.incumbent, seed + branch, wide=False)
                if depth == 1
                else _continuation_actions(public.incumbent, current.representation)
            )
            if not actions:
                actions = _start_actions(
                    public.incumbent, seed + branch + depth * 10_000, wide=False
                )
            rng.shuffle(actions)
            for attempt, (operator, arguments) in enumerate(actions):
                try:
                    child, record = apply_primitive(
                        current.representation,
                        operator,
                        arguments,
                        seed + branch * 10_000 + depth * 100 + attempt,
                        depth=depth,
                    )
                    current = ComposedRepresentation(child, current.ancestry + (record,))
                    evaluated.append(evaluate_candidate(public, current))
                    break
                except ValueError:
                    continue
            else:
                raise RuntimeError("random search found no valid continuation")
        paths.append(current)
    final_evaluations = [evaluate_candidate(public, path) for path in paths]
    selected = tuple(
        sorted(
            final_evaluations,
            key=lambda item: item.candidate.representation.structural_hash,
        )[:3]
    )
    return SearchResult(
        selected,
        tuple(evaluated),
        breadth * max_depth,
        breadth * max_depth,
        max_depth,
        breadth,
    )
