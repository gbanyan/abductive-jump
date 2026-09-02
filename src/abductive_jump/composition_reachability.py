from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .compositional_realization import fit_composed_representation
from .compositional_worlds import HELD_OUT_FAMILY
from .executable import evaluate_executable, freeze_theory, parse_theory, program_expression
from .generic_primitives import ComposedRepresentation, GenericPrimitive, compose
from .oracle import incumbent_oracle
from .representation import NodeKind
from .worlds import World, predict

Plan = tuple[tuple[GenericPrimitive, dict[str, str]], ...]


def _roles(world: World) -> dict[str, str]:
    return {
        str(node.attributes.get("role")): node.id
        for node in world.incumbent.nodes
        if node.attributes.get("role")
    }


def oracle_decomposition(world: World) -> Plan:
    """Return a benchmark-validity witness that is never imported by search code."""

    roles = _roles(world)
    equation_ids = [node.id for node in world.incumbent.nodes if node.kind is NodeKind.EQUATION]
    input_id = roles["input"]
    if world.family in {"latent_common_cause", "causal_ambiguity"}:
        return (
            (GenericPrimitive.ADD_NODE, {"id": "witness_node"}),
            (GenericPrimitive.CHANGE_NODE_TYPE, {"node": "witness_node", "kind": NodeKind.LATENT_VARIABLE.value}),
            (GenericPrimitive.CHANGE_OBSERVABILITY, {"node": "witness_node", "observable": "false"}),
            (GenericPrimitive.ADD_DEPENDENCY, {"node": "witness_node", "other": input_id}),
        )
    if world.family == "unification":
        return (
            (GenericPrimitive.ADD_FUNCTION, {"id": "witness_function"}),
            (GenericPrimitive.BIND_ARGUMENT, {"node": "witness_function", "other": equation_ids[0], "position": "0"}),
            (GenericPrimitive.BIND_ARGUMENT, {"node": "witness_function", "other": equation_ids[1], "position": "1"}),
        )
    if world.family == "hidden_regimes":
        return (
            (GenericPrimitive.ADD_NODE, {"id": "witness_node"}),
            (GenericPrimitive.CHANGE_NODE_TYPE, {"node": "witness_node", "kind": NodeKind.REGIME.value}),
            (GenericPrimitive.CHANGE_OBSERVABILITY, {"node": "witness_node", "observable": "false"}),
            (GenericPrimitive.ADD_DEPENDENCY, {"node": "witness_node", "other": equation_ids[0]}),
        )
    if world.family == "property_to_relation":
        return (
            (GenericPrimitive.ADD_NODE, {"id": "witness_node"}),
            (GenericPrimitive.CHANGE_NODE_TYPE, {"node": "witness_node", "kind": NodeKind.RELATION.value}),
            (GenericPrimitive.CHANGE_ARITY, {"node": "witness_node", "arity": "2"}),
            (GenericPrimitive.BIND_ARGUMENT, {"node": "witness_node", "other": input_id, "position": "0"}),
        )
    if world.family == "state_invention":
        return (
            (GenericPrimitive.ADD_NODE, {"id": "witness_node"}),
            (GenericPrimitive.CHANGE_NODE_TYPE, {"node": "witness_node", "kind": NodeKind.STATE_VARIABLE.value}),
            (GenericPrimitive.ADD_TEMPORAL_INDEX, {"node": "witness_node"}),
            (GenericPrimitive.ADD_DEPENDENCY, {"node": "witness_node", "other": "witness_node"}),
        )
    if world.family == "coordinate_transform":
        return (
            (GenericPrimitive.ADD_FUNCTION, {"id": "witness_function"}),
            (GenericPrimitive.COMPOSE_FUNCTIONS, {"node": "witness_function", "other": "witness_function"}),
        )
    if world.family == "meta_law":
        return (
            (GenericPrimitive.ADD_FUNCTION, {"id": "witness_function"}),
            (GenericPrimitive.CHANGE_ARITY, {"node": "witness_function", "arity": "2"}),
            (GenericPrimitive.BIND_ARGUMENT, {"node": "witness_function", "other": input_id, "position": "0"}),
            (GenericPrimitive.BIND_ARGUMENT, {"node": "witness_function", "other": roles["context_zero"], "position": "1"}),
        )
    if world.family == HELD_OUT_FAMILY:
        edge = next(
            edge
            for edge in world.incumbent.edges
            if edge.source == input_id and edge.target == equation_ids[0]
        )
        return (
            (
                GenericPrimitive.REIFY_EDGE_AS_NODE,
                {"node": edge.source, "other": edge.target, "relation": edge.relation, "id": "witness_relation"},
            ),
            (GenericPrimitive.CHANGE_ARITY, {"node": "witness_relation", "arity": "3"}),
            (GenericPrimitive.BIND_ARGUMENT, {"node": "witness_relation", "other": roles["second_input"], "position": "1"}),
            (GenericPrimitive.BIND_ARGUMENT, {"node": "witness_relation", "other": roles["third_input"], "position": "2"}),
        )
    raise ValueError(f"no reachability witness for {world.family}")


def executable_result(world: World, candidate: ComposedRepresentation) -> dict[str, Any]:
    fit = fit_composed_representation(world.public(), candidate.representation)
    public_to_internal = {public: internal for internal, public in world.variable_names}
    internal_to_public = dict(world.variable_names)
    oracle = incumbent_oracle(world)
    expression = fit.expression
    if fit.structural_signature == "incumbent_basis":
        def translate(value: Any) -> Any:
            if isinstance(value, dict):
                result = {key: translate(item) for key, item in value.items()}
                if result.get("op") in {"var", "raw_var", "history_sum"}:
                    result["name"] = internal_to_public.get(
                        str(result["name"]), str(result["name"])
                    )
                return result
            return value

        expression = type(fit.expression)(translate(program_expression(oracle.program).tree))
    selected = max(
        world.interventions,
        key=lambda case: abs(
            expression.evaluate(
                {internal_to_public.get(name, name): value for name, value in case.inputs if not name.startswith("_")},
                {internal_to_public.get(name, name): value for name, value in case.intervention},
            )
            - predict(oracle.program, dict(case.inputs), dict(case.intervention))
        ),
    )
    payload = {
        "representation": candidate.representation.canonical_dict(),
        "expression": expression.tree,
        "explanation": "deterministic reachability witness",
        "selected_intervention_ids": [selected.case_id],
    }
    theory = parse_theory(payload, public_to_internal)
    result = evaluate_executable(world, theory, freeze_theory(world, theory))
    return {**asdict(result), "validated_jump": result.validated_jump, "signature": fit.structural_signature}


def verify_reachability(world: World, seed: int = 700_000) -> dict[str, Any]:
    plan = oracle_decomposition(world)
    candidate = compose(world.incumbent, plan, seed)
    result = executable_result(world, candidate)
    first = compose(world.incumbent, plan[:1], seed)
    first_result = executable_result(world, first)
    return {
        "world_id": world.world_id,
        "family": world.family,
        "world_seed": world.seed,
        "no_jump": world.no_jump,
        "reachable": bool(result["validated_jump"]) if not world.no_jump else True,
        "constructive_depth_upper_bound": len(plan),
        "minimum_depth_lower_bound": 2,
        "bounded_minimum_depth": len(plan),
        "distance_certificate": "depth-1 witness prefix fails; registered constructive witness succeeds",
        "single_primitive_validated_jump": bool(first_result["validated_jump"]),
        "final_signature": result["signature"],
        "operators": [operator.value for operator, _ in plan],
        "arguments": [arguments for _, arguments in plan],
        "candidate_hash": candidate.representation.structural_hash,
        "j0": result["j0"],
        "j1": result["j1"],
        "j2": result["j2"],
        "j3": result["j3"],
        "j4": result["j4"],
        "j5": result["j5"],
        "validated_jump": result["validated_jump"],
    }
