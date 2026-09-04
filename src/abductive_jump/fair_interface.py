"""Grammar-valid two-stage interface for the targeted DeepSeek sensitivity."""

from __future__ import annotations

import json
from typing import Any

from .compositional_experiment import _public_payload
from .conditions import Condition, PromptSpec, ProposalSource
from .generic_primitives import GenericPrimitive
from .representation import NodeKind
from .worlds import World


def _arguments(
    required: tuple[str, ...],
    *,
    properties: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    fields = properties or {name: {"type": "string", "minLength": 1} for name in required}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(required),
        "properties": fields,
    }


def primitive_argument_schemas() -> dict[str, dict[str, Any]]:
    """Exact parser-level argument contract; no outcome or target information."""
    string = {"type": "string", "minLength": 1}
    node_other = {"node": string, "other": string}
    node_other_relation = {**node_other, "relation": string}
    return {
        "ADD_NODE": _arguments(("id",)),
        "REMOVE_NODE": _arguments(("node",)),
        "ADD_EDGE": _arguments(("node", "other", "relation"), properties=node_other_relation),
        "REMOVE_EDGE": _arguments(("node", "other", "relation"), properties=node_other_relation),
        "REVERSE_EDGE": _arguments(("node", "other", "relation"), properties=node_other_relation),
        "CHANGE_NODE_TYPE": _arguments(
            ("node", "kind"),
            properties={
                "node": string,
                "kind": {"type": "string", "enum": [kind.value for kind in NodeKind]},
            },
        ),
        "CHANGE_EDGE_TYPE": _arguments(
            ("node", "other", "from_relation", "to_relation"),
            properties={**node_other, "from_relation": string, "to_relation": string},
        ),
        "CHANGE_OBSERVABILITY": _arguments(
            ("node", "observable"),
            properties={
                "node": string,
                "observable": {"type": "string", "enum": ["true", "false"]},
            },
        ),
        "CHANGE_ARITY": _arguments(
            ("node", "arity"),
            properties={"node": string, "arity": {"type": "string", "pattern": "^[0-8]$"}},
        ),
        "BIND_ARGUMENT": _arguments(
            ("node", "other", "position"),
            properties={**node_other, "position": {"type": "string", "pattern": "^[0-8]$"}},
        ),
        "UNBIND_ARGUMENT": _arguments(
            ("node", "other", "position"),
            properties={**node_other, "position": {"type": "string", "pattern": "^[0-8]$"}},
        ),
        "ADD_FUNCTION": _arguments(("id",)),
        "REMOVE_FUNCTION": _arguments(("node",)),
        "ADD_EQUATION": _arguments(("id",)),
        "REMOVE_EQUATION": _arguments(("node",)),
        "COMPOSE_FUNCTIONS": _arguments(("node", "other"), properties=node_other),
        "DECOMPOSE_FUNCTION": _arguments(("node", "other"), properties=node_other),
        "ADD_TEMPORAL_INDEX": _arguments(("node",)),
        "REMOVE_TEMPORAL_INDEX": _arguments(("node",)),
        "ADD_DEPENDENCY": _arguments(("node", "other"), properties=node_other),
        "REMOVE_DEPENDENCY": _arguments(("node", "other"), properties=node_other),
        "ADD_CONSTRAINT": _arguments(("id",)),
        "REMOVE_CONSTRAINT": _arguments(("node",)),
        "MERGE_NODES": _arguments(("node", "other", "id"), properties={**node_other, "id": string}),
        "SPLIT_NODE": _arguments(
            ("node", "left", "right"),
            properties={"node": string, "left": string, "right": string},
        ),
        "REIFY_EDGE_AS_NODE": _arguments(
            ("node", "other", "relation", "id"),
            properties={**node_other_relation, "id": string},
        ),
        "REIFY_NODE_AS_EDGE": _arguments(
            ("node", "relation"), properties={"node": string, "relation": string}
        ),
        "SUBGRAPH_COPY": _arguments(("node", "id"), properties={"node": string, "id": string}),
    }


def step_schema() -> dict[str, Any]:
    return {
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["operator", "arguments"],
                "properties": {
                    "operator": {"const": operator},
                    "arguments": arguments,
                },
            }
            for operator, arguments in primitive_argument_schemas().items()
        ]
    }


def response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "fair_interface_plans_v1",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["plans"],
                "properties": {
                    "plans": {
                        "type": "array",
                        "minItems": 16,
                        "maxItems": 16,
                        "items": {
                            "type": "array",
                            "minItems": 4,
                            "maxItems": 4,
                            "items": step_schema(),
                        },
                    }
                },
            },
        },
    }


def syntax_manifest() -> dict[str, Any]:
    return {
        "portfolio": "GENERIC_PRIMITIVE_SET_V1",
        "steps_per_plan": 4,
        "plans_required": 16,
        "operators": primitive_argument_schemas(),
        "execution_rules": [
            "Each plan starts from the supplied incumbent representation.",
            "A node created in an earlier step may be referenced by a later step.",
            "Every node or edge reference must exist when its step executes.",
            "SUBGRAPH_CROSSOVER is unavailable because no donor is supplied.",
        ],
    }


def deliberation_prompt(world: World) -> PromptSpec:
    payload = _public_payload(world.public())
    payload["generic_primitive_syntax"] = syntax_manifest()
    return PromptSpec(
        "generic-self-composition-fair-deliberation-v1",
        Condition.C_SELF_LLM_COMPOSITION,
        ProposalSource.LLM_COMPOSITION,
        (
            "Reason about executable representation changes using only the supplied public world and "
            "primitive syntax. Do not use or invent intervention outcomes, hidden truth, target distance "
            "or gate feedback. A separate call will serialize your reasoning, so prioritize sixteen "
            "independent four-step plans and exact references."
        ),
        "Develop candidate plans for this public world: "
        + json.dumps(payload, sort_keys=True, separators=(",", ":")),
    )


def serialization_prompt(world: World, deliberation: str) -> PromptSpec:
    payload = _public_payload(world.public())
    payload["generic_primitive_syntax"] = syntax_manifest()
    payload["prior_model_deliberation"] = deliberation
    return PromptSpec(
        "generic-self-composition-fair-serialization-v1",
        Condition.C_SELF_LLM_COMPOSITION,
        ProposalSource.LLM_COMPOSITION,
        (
            "Return only the compact JSON plan object required by the response schema. Do not explain, "
            "repair semantically, use hidden information or add any outcome claim."
        ),
        "Serialize exactly sixteen independent four-step plans from the prior deliberation. "
        "All arguments must follow the supplied parser-level syntax: "
        + json.dumps(payload, sort_keys=True, separators=(",", ":")),
    )


def operator_vocabulary() -> tuple[str, ...]:
    expected = tuple(
        operator.value
        for operator in GenericPrimitive
        if operator is not GenericPrimitive.SUBGRAPH_CROSSOVER
    )
    actual = tuple(primitive_argument_schemas())
    if set(actual) != set(expected):
        raise ValueError(
            "fair-interface syntax manifest does not match the frozen primitive vocabulary"
        )
    return actual
