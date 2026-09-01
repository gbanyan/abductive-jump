from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .executable import evaluate_executable, freeze_theory, parse_theory
from .oracle import incumbent_oracle
from .proposals import external_representation_proposals
from .realization import fit_representation
from .worlds import FAMILIES, generate_world, predict


def run(output_path: Path, seeds: range = range(100)) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    world_results: list[dict[str, Any]] = []
    for family in FAMILIES:
        for seed in seeds:
            for no_jump in (False, True):
                world = generate_world(family, seed, no_jump=no_jump)
                public = world.public()
                oracle = incumbent_oracle(world)
                successes = 0
                for proposal_index, proposal in enumerate(
                    external_representation_proposals(public, seed ^ 0x5151)
                ):
                    row: dict[str, Any] = {
                        "world_id": world.world_id,
                        "family": family,
                        "seed": seed,
                        "no_jump": no_jump,
                        "proposal_index": proposal_index,
                        "representation_hash": proposal.representation.structural_hash,
                        "operators": list(proposal.operators),
                        "valid_realization": False,
                        "validated_jump": False,
                    }
                    try:
                        fitted = fit_representation(public, proposal.representation)
                        separations = [
                            abs(
                                fitted.expression.evaluate(
                                    query["inputs"], query["intervention"]
                                )
                                - predict(
                                    oracle.program,
                                    dict(case.inputs),
                                    dict(case.intervention),
                                )
                            )
                            for case, query in zip(
                                world.interventions, public.intervention_queries
                            )
                        ]
                        best = max(range(len(separations)), key=separations.__getitem__)
                        theory = parse_theory(
                            {
                                "representation": proposal.representation.canonical_dict(),
                                "expression": fitted.expression.tree,
                                "selected_intervention_ids": [
                                    world.interventions[best].case_id
                                ],
                            },
                            {
                                public_name: internal
                                for internal, public_name in world.variable_names
                            },
                        )
                        gates = evaluate_executable(
                            world, theory, freeze_theory(world, theory)
                        )
                        row.update(asdict(gates))
                        row["valid_realization"] = True
                        row["validated_jump"] = gates.validated_jump
                        row["basis_names"] = list(fitted.basis_names)
                        row["coefficients"] = list(fitted.coefficients)
                        row["max_prediction_separation"] = separations[best]
                        successes += gates.validated_jump
                    except (KeyError, TypeError, ValueError, OverflowError) as exc:
                        row["error_type"] = type(exc).__name__
                        row["error"] = str(exc)
                    rows.append(row)
                world_results.append(
                    {
                        "world_id": world.world_id,
                        "family": family,
                        "seed": seed,
                        "no_jump": no_jump,
                        "condition_success": successes > 0,
                        "validated_candidates": successes,
                    }
                )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), output_path, compression="zstd")
    summary_path = output_path.with_name("external_reachability_worlds.parquet")
    pq.write_table(pa.Table.from_pylist(world_results), summary_path, compression="zstd")
    jumps = [row for row in world_results if not row["no_jump"]]
    controls = [row for row in world_results if row["no_jump"]]
    return {
        "candidates": len(rows),
        "jump_worlds": len(jumps),
        "controls": len(controls),
        "jump_reachability": sum(row["condition_success"] for row in jumps) / len(jumps),
        "false_jump_rate": sum(row["condition_success"] for row in controls) / len(controls),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    summary = run(root / "artifacts/pilot/external_reachability_candidates.parquet")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

