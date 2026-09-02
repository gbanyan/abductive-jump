from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .executable import ExecutableTheory, evaluate_executable, freeze_theory, program_expression
from .mutations import MutationOperator, MutationRecord, mutate
from .oracle import incumbent_oracle
from .representation import NodeKind, Representation
from .worlds import FAMILIES, World, generate_world, predict

CONTROL_CATEGORIES = (
    "RANDOM_SEMANTIC_PARAPHRASE",
    "INVALID_STRUCTURAL_CHANGE",
    "UNNECESSARY_LATENT",
    "OVERCOMPLICATED_NO_GAIN",
)


def _add_node_and_edge(
    representation: Representation,
    kind: NodeKind,
    node_id: str,
    source: str,
    target: str,
    seed: int,
) -> tuple[Representation, tuple[MutationRecord, ...]]:
    first, node_record = mutate(
        representation,
        MutationOperator.ADD_NODE,
        {"kind": kind.value, "id": node_id},
        seed,
    )
    second, edge_record = mutate(
        first,
        MutationOperator.ADD_RELATION,
        {"node": source, "other": node_id, "relation": "supports"},
        seed + 1,
    )
    third, consequence = mutate(
        second,
        MutationOperator.ADD_RELATION,
        {"node": node_id, "other": target, "relation": "predicts"},
        seed + 2,
    )
    return third, (node_record, edge_record, consequence)


def _candidate(
    world: World, category: str
) -> tuple[Representation, Any, tuple[MutationRecord, ...]]:
    incumbent = world.incumbent
    source = next(
        (node.id for node in incumbent.nodes if node.attributes.get("role") == "input"),
        incumbent.nodes[0].id,
    )
    outcome = next(
        (node.id for node in incumbent.nodes if node.attributes.get("role") == "outcome"),
        incumbent.nodes[-1].id,
    )
    oracle_expression = program_expression(incumbent_oracle(world).program)
    if category == "RANDOM_SEMANTIC_PARAPHRASE":
        return incumbent, oracle_expression, ()
    if category == "INVALID_STRUCTURAL_CHANGE":
        representation, records = _add_node_and_edge(
            incumbent,
            NodeKind.STATE_VARIABLE,
            f"invalid_{world.seed}",
            source,
            outcome,
            world.seed ^ 0xBAD,
        )
        from .expressions import Expression

        return representation, Expression({"op": "const", "value": 0.0}), records
    if category == "UNNECESSARY_LATENT":
        representation, records = _add_node_and_edge(
            incumbent,
            NodeKind.LATENT_VARIABLE,
            f"unused_{world.seed}",
            source,
            outcome,
            world.seed ^ 0x1A7,
        )
        return representation, oracle_expression, records
    if category == "OVERCOMPLICATED_NO_GAIN":
        current = incumbent
        records: list[MutationRecord] = []
        for index, kind in enumerate(
            (NodeKind.LATENT_VARIABLE, NodeKind.STATE_VARIABLE, NodeKind.REGIME, NodeKind.FUNCTION)
        ):
            current, created = _add_node_and_edge(
                current,
                kind,
                f"extra_{world.seed}_{index}",
                source,
                outcome,
                (world.seed ^ 0xC0DE) + index * 10,
            )
            records.extend(created)
        return current, oracle_expression, tuple(records)
    raise ValueError(category)


def run(root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for no_jump, seeds in ((False, range(10_000, 10_050)), (True, range(20_000, 20_025))):
        for family in FAMILIES:
            for seed in seeds:
                world = generate_world(family, seed, no_jump=no_jump)
                oracle = incumbent_oracle(world)
                for category in CONTROL_CATEGORIES:
                    representation, expression, records = _candidate(world, category)
                    separations = [
                        abs(
                            expression.evaluate(dict(case.inputs), dict(case.intervention))
                            - predict(oracle.program, dict(case.inputs), dict(case.intervention))
                        )
                        for case in world.interventions
                    ]
                    selected_index = max(range(len(separations)), key=separations.__getitem__)
                    theory = ExecutableTheory(
                        representation,
                        expression,
                        category.lower().replace("_", " "),
                        (world.interventions[selected_index].case_id,),
                    )
                    result = evaluate_executable(world, theory, freeze_theory(world, theory))
                    rows.append(
                        {
                            "category": category,
                            "world_id": world.world_id,
                            "family": family,
                            "world_seed": seed,
                            "no_jump": no_jump,
                            "representation_hash": representation.structural_hash,
                            "mutation_count": len(records),
                            "mutation_operators": [record.operator.value for record in records],
                            **asdict(result),
                            "validated_jump": result.validated_jump,
                        }
                    )
    output = root / "artifacts" / "negative_controls.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output, compression="zstd")
    summary = {
        category: {
            "rows": sum(row["category"] == category for row in rows),
            "accepted": sum(
                row["category"] == category and row["validated_jump"] for row in rows
            ),
        }
        for category in CONTROL_CATEGORIES
    }
    (root / "artifacts" / "negative_controls_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return {"rows": len(rows), "summary": summary}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(run(root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
