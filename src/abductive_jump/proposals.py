from __future__ import annotations

from dataclasses import dataclass

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
        (NodeKind.LATENT_VARIABLE, "causes", source.id, outcome.id),
        (NodeKind.INVARIANT, "governs", equation.id, equation.id),
        (NodeKind.REGIME, "selects", equation.id, equation.id),
        (NodeKind.RELATION, "conditions", source.id, equation.id),
        (NodeKind.STATE_VARIABLE, "updates", source.id, outcome.id),
        (NodeKind.FUNCTION, "transforms", source.id, equation.id),
        (NodeKind.CAUSAL_EDGE, "orients", source.id, outcome.id),
        (NodeKind.TRANSITION, "updates", source.id, outcome.id),
    )
    proposals: list[RepresentationProposal] = []
    for index, (kind, relation, left, right) in enumerate(plans):
        node_id = f"m{seed % 1_000_000:06d}_{index}"
        first, add_record = mutate(
            incumbent,
            MutationOperator.ADD_NODE,
            {"kind": kind.value, "id": node_id},
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

