from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum

from .expressions import Expression
from .mutations import MutationOperator
from .representation import NodeKind, Representation
from .worlds import PublicWorld


class Condition(StrEnum):
    B0_DIRECT_LLM = "B0_DIRECT_LLM"
    B1_SAMPLE_MATCHED = "B1_SAMPLE_MATCHED"
    B2_FIXED_SPACE_AGENT = "B2_FIXED_SPACE_AGENT"
    B3_ATTRIBUTE_MUTATION = "B3_ATTRIBUTE_MUTATION"
    B4_REPRESENTATION_MUTATION = "B4_REPRESENTATION_MUTATION"
    B5_FULL_SYSTEM = "B5_FULL_SYSTEM"


class ProposalSource(StrEnum):
    P0_LLM = "P0_LLM"
    P1_EXTERNAL = "P1_EXTERNAL"
    P2_ORACLE = "P2_ORACLE"


@dataclass(frozen=True, slots=True)
class PromptSpec:
    template_version: str
    condition: Condition
    proposal_source: ProposalSource
    system: str
    user: str


EXPRESSION_GRAMMAR = {
    "operator_signatures": [
        "const(value)",
        "var(name)",
        "raw_var(name)",
        "history_sum(name)",
        "neg(arg)",
        "add(left,right)",
        "sub(left,right)",
        "mul(left,right)",
        "div(left,right)",
        "pow(left,right)",
        "if_eq(left,right,then,else)",
    ],
    "finite_examples": [
        {"op": "mul", "left": {"op": "const", "value": 2}, "right": {"op": "var", "name": "q123"}},
        {
            "op": "add",
            "left": {"op": "var", "name": "q123"},
            "right": {"op": "history_sum", "name": "q456"},
        },
    ],
    "limits": {"nodes": 32, "depth": 8},
}

MUTATION_PLAN_CONTRACT = {
    "max_steps": 3,
    "operators": [operator.value for operator in MutationOperator if operator.value != "SUBGRAPH_CROSSOVER"],
    "step_schema": {"operator": "OPERATOR_NAME", "arguments": {"argument_name": "string_value"}},
    "common_arguments": {
        "node": "existing node id",
        "other": "existing node id",
        "id": "new unique node id",
        "kind": "allowed node kind",
        "relation": "relation label",
        "attr_transform": "optional structural attribute such as square",
        "attr_form": "optional structural form such as affine_context or additive_linear",
        "attr_contrast": "optional structural contrast such as sign_flip",
    },
}


def _public_payload(world: PublicWorld) -> dict[str, object]:
    variable_types: dict[str, str] = {}
    for case in world.observations:
        for name, value in case["inputs"].items():
            variable_types[name] = "sequence_use_history_sum" if isinstance(value, (list, tuple)) else "scalar"
    return {
        "world_id": world.world_id,
        "observations": list(world.observations),
        "incumbent_representation": world.incumbent.canonical_dict(),
        "prospective_intervention_queries_without_outcomes": world.intervention_queries,
        "expression_grammar": EXPRESSION_GRAMMAR,
        "allowed_representation_node_kinds": [kind.value for kind in NodeKind],
        "public_variable_types": variable_types,
        "known_nuisance_fields": list(world.known_nuisance_fields),
    }


def _representation_delta(incumbent: Representation, candidate: Representation) -> dict[str, object]:
    incumbent_nodes = {node.id: node for node in incumbent.nodes}
    candidate_nodes = {node.id: node for node in candidate.nodes}
    incumbent_edges = set(incumbent.edges)
    candidate_edges = set(candidate.edges)
    return {
        "added_nodes": [candidate_nodes[node_id].canonical() for node_id in sorted(candidate_nodes.keys() - incumbent_nodes.keys())],
        "removed_node_ids": sorted(incumbent_nodes.keys() - candidate_nodes.keys()),
        "changed_nodes": [
            candidate_nodes[node_id].canonical()
            for node_id in sorted(candidate_nodes.keys() & incumbent_nodes.keys())
            if candidate_nodes[node_id] != incumbent_nodes[node_id]
        ],
        "added_edges": [edge.canonical() for edge in sorted(candidate_edges - incumbent_edges)],
        "removed_edges": [edge.canonical() for edge in sorted(incumbent_edges - candidate_edges)],
    }


def build_prompt(
    world: PublicWorld,
    condition: Condition,
    proposal_source: ProposalSource,
    supplied_representation: Representation | None = None,
    supplied_expression: Expression | None = None,
    supplied_observational_loss: float | None = None,
    prediction_separation_table: list[dict[str, object]] | None = None,
    prior_summary: str | None = None,
) -> PromptSpec:
    payload = _public_payload(world)
    if condition is Condition.B1_SAMPLE_MATCHED:
        payload["mutation_plan_contract"] = MUTATION_PLAN_CONTRACT
    if supplied_representation is not None:
        payload["supplied_candidate_representation"] = supplied_representation.canonical_dict()
        payload["supplied_representation_delta_from_incumbent"] = _representation_delta(
            world.incumbent, supplied_representation
        )
    if supplied_expression is not None:
        payload["supplied_fitted_expression"] = supplied_expression.tree
        if supplied_observational_loss is not None:
            payload["supplied_observational_loss"] = supplied_observational_loss
    if prediction_separation_table is not None:
        payload["prediction_separation_table_without_outcomes"] = prediction_separation_table
    constraint = {
        Condition.B0_DIRECT_LLM: "Propose one strongest explanatory representation and executable rule directly.",
        Condition.B1_SAMPLE_MATCHED: "Produce one independent proposal. Do not refine or quote earlier proposals.",
        Condition.B2_FIXED_SPACE_AGENT: "You must retain the incumbent representation exactly; revise only its values or executable rule.",
        Condition.B3_ATTRIBUTE_MUTATION: "Use the incumbent representation exactly. External search may alter coefficients, thresholds, signs, or rule values only.",
        Condition.B4_REPRESENTATION_MUTATION: "Use the supplied externally mutated representation exactly and realize its strongest executable theory.",
        Condition.B5_FULL_SYSTEM: "Use the supplied representation exactly; prioritize observed fit and a discriminating prediction. Archive diversity is handled externally.",
    }[condition]
    if proposal_source is ProposalSource.P2_ORACLE:
        constraint = "Assume the supplied representation is correct. Infer its executable law from observations and choose the most discriminating listed intervention."
    elif proposal_source is ProposalSource.P1_EXTERNAL:
        constraint += " The representation was proposed by a family-blind structural process; do not replace it."

    system = (
        "You construct executable scientific theories. Return exactly one JSON object and no markdown. "
        "Truth is determined only by an external simulator. Never invent outcomes or refer to hidden fields. "
        "Silently calculate and verify the simplest exact rule against every observation before writing JSON. "
        "Start with {, keep derivation and explanation to one short sentence each, and finish within 160 tokens."
    )
    representation_output: object = (
        "USE_SUPPLIED_REPRESENTATION"
        if supplied_representation is not None
        else {"schema_version": "1", "nodes": [], "edges": []}
    )
    output_contract = {
        "representation": representation_output,
        "derivation": "brief arithmetic check of the rule on every observation",
        "expression": (
            "USE_SUPPLIED_FITTED_EXPRESSION"
            if supplied_expression is not None
            else {"op": "...bounded expression AST..."}
        ),
        "explanation": "short mechanistic explanation",
        "selected_intervention_ids": ["exactly one listed test case id"],
    }
    if condition is Condition.B1_SAMPLE_MATCHED and supplied_representation is None:
        output_contract.pop("representation")
        output_contract["mutation_plan"] = [MUTATION_PLAN_CONTRACT["step_schema"]]
    user_parts = [
        constraint,
        "Expression variable names must be copied exactly from the public observation/query field names, never from representation node IDs unless a node ID is also a public field. For a sequence field, either history_sum or var (which sums the sequence) is valid. Fields listed in known_nuisance_fields are irrelevant distractors and must not appear in the expression. Read the supplied representation delta carefully: its node attributes are part of the assumed representation. Every operator must use exactly the keys shown in the expression grammar. Fit every observation exactly without using its outcome as an input; numerically check the rule on every row. The selected intervention and its prediction are frozen before the simulator reveals outcomes.",
        "Output schema: " + json.dumps(output_contract, separators=(",", ":")),
        "World: " + json.dumps(payload, sort_keys=True, separators=(",", ":")),
    ]
    if supplied_expression is not None:
        fit_status = (
            "fits every observation exactly"
            if supplied_observational_loss is None or supplied_observational_loss <= 1e-12
            else "is the deterministic best fit but does not fit every observation exactly"
        )
        user_parts.insert(
            1,
            "The shared deterministic hypothesis-genome fitter supplied an expression that "
            + fit_status
            + ". Use it unchanged. The exact experiment designer has computed candidate and incumbent-oracle predictions without seeing simulator outcomes. Choose exactly one listed experiment with maximum absolute separation; some rows are non-discriminating controls.",
        )
    if prior_summary:
        user_parts.append("Prior structured search summary: " + prior_summary)
    return PromptSpec("theory-json-v9", condition, proposal_source, system, "\n".join(user_parts))
