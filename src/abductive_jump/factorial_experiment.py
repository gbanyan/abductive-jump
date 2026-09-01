from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .budget import EqualBudgetContract
from .conditions import Condition, ProposalSource
from .external_reasoning_calibration import _manifest
from .primary_experiment import _arrow_table, _run_slot, _world_seeds

SOURCE_CONDITIONS = {
    ProposalSource.P0_LLM: Condition.B1_SAMPLE_MATCHED,
    ProposalSource.P1_EXTERNAL: Condition.B4_REPRESENTATION_MUTATION,
    ProposalSource.P2_ORACLE: Condition.B4_REPRESENTATION_MUTATION,
}


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    sources = tuple(ProposalSource(value) for value in config["proposal_sources"])
    slots = int(config["candidate_slots"])
    contract = EqualBudgetContract(slots, 2, int(config["generation"]["max_tokens"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        {
            "config": config,
            "condition": SOURCE_CONDITIONS[source],
            "family": family,
            "world_seed": seed,
            "slot": slot,
            "base_url": base_url,
            "log_path": output_dir / "llm_calls.jsonl",
            "source_override": source,
        }
        for source in sources
        for family in config["families"]
        for seed in _world_seeds(config)
        for slot in range(slots)
    ]
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=int(config.get("concurrency", 1))) as executor:
        futures = [executor.submit(_run_slot, **job) for job in jobs]
        for future in as_completed(futures):
            row = future.result()
            row["factorial_source"] = row["proposal_source"]
            rows.append(row)
    rows.sort(key=lambda row: (row["factorial_source"], row["family"], row["world_seed"], row["slot"]))
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["factorial_source"], row["world_id"])].append(row)
    worlds: list[dict[str, Any]] = []
    for (source, world_id), candidates in sorted(grouped.items()):
        worlds.append(
            {
                "proposal_source": source,
                "world_id": world_id,
                "family": candidates[0]["family"],
                "world_seed": candidates[0]["world_seed"],
                "no_jump": candidates[0]["no_jump"],
                "condition_success": any(row["validated_jump"] for row in candidates),
                "validated_candidates": sum(row["validated_jump"] for row in candidates),
                "llm_calls_used": len(candidates) * 2,
                "llm_tokens_used": sum(
                    row["phase_one_tokens"] + row["phase_two_tokens"]
                    for row in candidates
                ),
                "candidate_evaluations_used": len(candidates),
                "interventions_used": len(candidates),
            }
        )
    summaries: list[dict[str, Any]] = []
    for source in sources:
        selected = [row for row in worlds if row["proposal_source"] == source.value]
        jumps = [row for row in selected if not row["no_jump"]]
        controls = [row for row in selected if row["no_jump"]]
        summaries.append(
            {
                "proposal_source": source.value,
                "worlds": len(selected),
                "jsr": sum(row["condition_success"] for row in jumps) / len(jumps) if jumps else None,
                "fjr": sum(row["condition_success"] for row in controls) / len(controls) if controls else None,
                "mean_tokens": sum(row["llm_tokens_used"] for row in selected) / len(selected),
            }
        )
    pq.write_table(_arrow_table(rows), output_dir / "candidate_results.parquet", compression="zstd")
    pq.write_table(_arrow_table(worlds), output_dir / "world_results.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pylist(summaries), output_dir / "factorial_summary.parquet", compression="zstd")
    summary = {
        "model_manifest": asdict(_manifest(config)),
        "budget_contract": contract.canonical_dict(),
        "sources": summaries,
        "candidate_rows": len(rows),
        "world_source_rows": len(worlds),
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
