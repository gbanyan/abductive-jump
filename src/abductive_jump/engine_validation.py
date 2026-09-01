from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .gates import GateThresholds, evaluate_jump, freeze_predictions
from .oracle import incumbent_oracle
from .worlds import generate_world


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")


def run(config_path: Path, artifact_dir: Path, report_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    thresholds = GateThresholds(**config["thresholds"])
    seeds = range(config["seeds"]["start"], config["seeds"]["stop_exclusive"])
    manifests: list[dict[str, Any]] = []
    truths: list[dict[str, Any]] = []
    oracles: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    for family in config["families"]:
        for seed in seeds:
            for no_jump in (False, True) if config["include_matched_no_jump"] else (False,):
                world = generate_world(family, seed, no_jump=no_jump)
                oracle = incumbent_oracle(world)
                commitment = freeze_predictions(world, world.truth, oracle)
                result = evaluate_jump(world, world.truth, commitment, thresholds)
                manifests.append(
                    {
                        "world_id": world.world_id,
                        "family": family,
                        "world_seed": seed,
                        "lexical_seed": world.lexical_seed,
                        "no_jump": no_jump,
                        "incumbent_hash": world.incumbent.structural_hash,
                        "ground_truth_representation_hash": world.truth.representation.structural_hash,
                        "ground_truth_hash": world.ground_truth_hash,
                        "split_hash": world.split_hash,
                        "n_observations": len(world.observations),
                        "n_validation": len(world.validation),
                        "n_interventions": len(world.interventions),
                        "n_falsification": len(world.falsification),
                    }
                )
                truths.append(
                    {
                        "world_id": world.world_id,
                        "representation_json": world.truth.representation.canonical_json(),
                        "program_json": world.truth.program.canonical_json,
                        "candidate_hash": world.truth.candidate_hash,
                    }
                )
                oracles.append(
                    {
                        "world_id": world.world_id,
                        "program_json": oracle.program.canonical_json,
                        "observational_loss": oracle.observational_loss,
                        "exact": oracle.exact,
                        "hypotheses_evaluated": oracle.hypotheses_evaluated,
                        "certificate_json": json.dumps(oracle.certificate, separators=(",", ":")),
                    }
                )
                gate_row = asdict(result)
                gate_row["validated_jump"] = result.validated_jump
                gate_row["escape_reasons"] = list(result.escape_reasons)
                gates.append(gate_row)
                if no_jump:
                    controls.append(
                        {
                            "world_id": world.world_id,
                            "family": family,
                            "seed": seed,
                            "accepted_jump": result.validated_jump,
                            "j1_escape": result.j1_representation_escape,
                            "counterfactual_gain": result.counterfactual_oracle_loss - result.counterfactual_candidate_loss,
                        }
                    )

    _write(artifact_dir / "world_manifest.parquet", manifests)
    _write(artifact_dir / "world_ground_truth.parquet", truths)
    _write(artifact_dir / "incumbent_oracle.parquet", oracles)
    _write(artifact_dir / "jump_gate_results.parquet", gates)
    _write(artifact_dir / "no_jump_controls.parquet", controls)

    jump_rows = [row for row in gates if "-jump-" in row["world_id"]]
    summary = {
        "worlds": len(manifests),
        "jump_worlds": len(jump_rows),
        "no_jump_worlds": len(controls),
        "all_oracles_exact": all(row["exact"] for row in oracles),
        "all_j0": all(row["j0_local_adequacy"] for row in gates),
        "truth_jump_pass_rate": sum(row["validated_jump"] for row in jump_rows) / len(jump_rows),
        "truth_no_jump_accept_rate": sum(row["accepted_jump"] for row in controls) / len(controls),
        "unique_ground_truth_hashes": len({row["ground_truth_hash"] for row in manifests}),
        "unique_split_hashes": len({row["split_hash"] for row in manifests}),
    }
    lines = [
        "# World-engine validation",
        "",
        "Status: engine-only pilot; no LLM was called and these are not confirmatory results.",
        "",
        f"- Generated worlds: {summary['worlds']:,} ({summary['jump_worlds']:,} jump; {summary['no_jump_worlds']:,} matched no-jump).",
        f"- Exact incumbent oracles: {summary['all_oracles_exact']}.",
        f"- J0 local adequacy passed for every world: {summary['all_j0']}.",
        f"- Ground-truth candidate J0–J5 pass rate in jump worlds: {summary['truth_jump_pass_rate']:.3f}.",
        f"- Ground-truth acceptance rate in no-jump worlds: {summary['truth_no_jump_accept_rate']:.3f}.",
        f"- Unique ground-truth candidate hashes: {summary['unique_ground_truth_hashes']:,}.",
        f"- Unique split hashes: {summary['unique_split_hashes']:,}.",
        "",
        "This pilot proves internal gate separability for generated truths, not benchmark difficulty for an LLM. Difficulty, lexical leakage, mutation reachability, and candidate realization remain calibration tasks.",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))
    return summary


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    summary = run(root / "configs/engine-pilot.json", root / "artifacts", root / "reports/world-engine-validation.md")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

