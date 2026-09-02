from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from .conditions import Condition, ProposalSource
from .primary_experiment import _arrow_table, _run_slot, _world_seeds
from .proposals import random_untyped_proposal
from .worlds import generate_world


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    slots = int(config["candidate_slots"])
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for family in config["families"]:
        for world_seed in _world_seeds(config):
            world = generate_world(family, world_seed, no_jump=bool(config["no_jump"]))
            for slot in range(slots):
                proposal = random_untyped_proposal(
                    world.public(), world_seed * 1009 + slot * 17 + 0xA6
                )
                jobs.append(
                    {
                        "config": config,
                        "condition": Condition.B4_REPRESENTATION_MUTATION,
                        "family": family,
                        "world_seed": world_seed,
                        "slot": slot,
                        "base_url": base_url,
                        "log_path": output_dir / "llm_calls.jsonl",
                        "source_override": ProposalSource.P1_EXTERNAL,
                        "representation_override": proposal.representation,
                        "ancestry_override": proposal.operators,
                    }
                )
    rows = []
    with ThreadPoolExecutor(max_workers=int(config["concurrency"])) as executor:
        futures = [executor.submit(_run_slot, **job) for job in jobs]
        for future in as_completed(futures):
            row = future.result()
            row["ablation"] = "A6_RANDOM_UNTYPED"
            rows.append(row)
    rows.sort(key=lambda row: (row["family"], row["world_seed"], row["slot"]))
    worlds = []
    keys = sorted({(row["family"], row["world_id"], row["world_seed"], row["no_jump"]) for row in rows})
    for family, world_id, world_seed, no_jump in keys:
        candidates = [row for row in rows if row["world_id"] == world_id]
        worlds.append(
            {
                "ablation": "A6_RANDOM_UNTYPED",
                "family": family,
                "world_id": world_id,
                "world_seed": world_seed,
                "no_jump": no_jump,
                "condition_success": any(row["validated_jump"] for row in candidates),
                "validated_candidates": sum(row["validated_jump"] for row in candidates),
                "llm_calls_used": len(candidates) * 2,
                "candidate_evaluations_used": len(candidates),
                "interventions_used": len(candidates),
                "llm_tokens_used": sum(row["phase_one_tokens"] + row["phase_two_tokens"] for row in candidates),
            }
        )
    pq.write_table(_arrow_table(rows), output_dir / "candidate_results.parquet", compression="zstd")
    pq.write_table(_arrow_table(worlds), output_dir / "world_results.parquet", compression="zstd")
    jumps = [row for row in worlds if not row["no_jump"]]
    controls = [row for row in worlds if row["no_jump"]]
    summary = {
        "ablation": "A6_RANDOM_UNTYPED",
        "worlds": len(worlds),
        "jsr": sum(row["condition_success"] for row in jumps) / len(jumps) if jumps else None,
        "fjr": sum(row["condition_success"] for row in controls) / len(controls) if controls else None,
        "candidate_rows": len(rows),
        "llm_calls": len(rows) * 2,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output_dir, args.base_url), indent=2))


if __name__ == "__main__":
    main()
