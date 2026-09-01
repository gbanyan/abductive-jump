from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from .mutations import MutationOperator, MutationRecord, mutate
from .representation import NodeKind, Representation
from .worlds import PublicWorld


@dataclass(frozen=True, slots=True)
class RepresentationProposal:
    representation: Representation
    ancestry: tuple[MutationRecord, ...]

    @property
    def operators(self) -> tuple[str, ...]:
        return tuple(record.operator.value for record in self.ancestry)


def apply_mutation_plan(
    incumbent: Representation,
    plan: list[dict[str, Any]],
    seed: int,
    *,
    max_steps: int = 3,
) -> RepresentationProposal:
    """Execute a compact LLM-chosen plan through the same typed mutation API."""
    if not 1 <= len(plan) <= max_steps:
        raise ValueError(f"mutation plan must contain 1..{max_steps} steps")
    current = incumbent
    records: list[MutationRecord] = []
    for index, step in enumerate(plan):
        if set(step) != {"operator", "arguments"}:
            raise ValueError("each mutation step requires only operator and arguments")
        operator = MutationOperator(str(step["operator"]))
        raw_arguments = step["arguments"]
        if not isinstance(raw_arguments, dict):
            raise TypeError("mutation arguments must be an object")
        arguments = {str(key): str(value) for key, value in raw_arguments.items()}
        current, record = mutate(current, operator, arguments, seed + index)
        records.append(record)
    return RepresentationProposal(current, tuple(records))


def external_representation_proposals(
    world: PublicWorld,
    seed: int,
) -> tuple[RepresentationProposal, ...]:
    """Generate a fixed family-blind portfolio using only the redacted incumbent graph."""
    incumbent = world.incumbent
    input_nodes = [node for node in incumbent.nodes if node.attributes.get("role") == "input"]
    outcome_nodes = [node for node in incumbent.nodes if node.attributes.get("role") == "outcome"]
    equation_nodes = [node for node in incumbent.nodes if node.kind is NodeKind.EQUATION]
    source = input_nodes[0] if input_nodes else incumbent.nodes[0]
    outcome = outcome_nodes[0] if outcome_nodes else incumbent.nodes[-1]
    equation = equation_nodes[0] if equation_nodes else outcome
    plans = (
        (NodeKind.LATENT_VARIABLE, "causes", source.id, outcome.id, {}),
        (NodeKind.INVARIANT, "governs", equation.id, equation.id, {}),
        (NodeKind.REGIME, "selects", equation.id, equation.id, {"contrast": "sign_flip"}),
        (NodeKind.RELATION, "conditions", source.id, equation.id, {"form": "additive_linear"}),
        (NodeKind.STATE_VARIABLE, "updates", source.id, outcome.id, {"form": "additive_state"}),
        (NodeKind.FUNCTION, "transforms", source.id, equation.id, {"transform": "square"}),
        (NodeKind.FUNCTION, "governs", source.id, equation.id, {"form": "affine_context"}),
        (NodeKind.CAUSAL_EDGE, "orients", source.id, outcome.id, {}),
        (NodeKind.TRANSITION, "updates", source.id, outcome.id, {}),
    )
    proposals: list[RepresentationProposal] = []
    for index, (kind, relation, left, right, attributes) in enumerate(plans):
        node_id = f"m{seed % 1_000_000:06d}_{index}"
        first, add_record = mutate(
            incumbent,
            MutationOperator.ADD_NODE,
            {
                "kind": kind.value,
                "id": node_id,
                **{f"attr_{key}": value for key, value in attributes.items()},
            },
            seed + index * 10,
        )
        if kind in {NodeKind.INVARIANT, NodeKind.REGIME}:
            edge_source, edge_target = node_id, right
        elif kind in {NodeKind.LATENT_VARIABLE}:
            edge_source, edge_target = node_id, left
        else:
            edge_source, edge_target = left, node_id
        second, edge_record = mutate(
            first,
            MutationOperator.ADD_RELATION,
            {"node": edge_source, "other": edge_target, "relation": relation},
            seed + index * 10 + 1,
        )
        # Give newly reified mechanisms an observable consequence without family knowledge.
        records = [add_record, edge_record]
        if kind in {NodeKind.LATENT_VARIABLE, NodeKind.RELATION, NodeKind.STATE_VARIABLE, NodeKind.FUNCTION, NodeKind.CAUSAL_EDGE, NodeKind.TRANSITION}:
            third, consequence_record = mutate(
                second,
                MutationOperator.ADD_RELATION,
                {"node": node_id, "other": outcome.id, "relation": "predicts"},
                seed + index * 10 + 2,
            )
            second = third
            records.append(consequence_record)
        proposals.append(RepresentationProposal(second, tuple(records)))
    return tuple(proposals)


def select_external_proposals(
    world: PublicWorld, seed: int, slots: int, *, diverse: bool = True
) -> tuple[RepresentationProposal, ...]:
    """Select a seed-randomized family-blind subset without outcome access.

    The full-system condition uses structural uniqueness (the archive analogue),
    while the plain representation-mutation condition samples with replacement.
    """
    proposals = list(external_representation_proposals(world, seed))
    rng = random.Random(seed ^ 0xB4B5)
    if not 1 <= slots <= len(proposals):
        raise ValueError("external proposal slots exceed the frozen portfolio")
    if diverse:
        rng.shuffle(proposals)
        return tuple(proposals[:slots])
    return tuple(rng.choice(proposals) for _ in range(slots))
