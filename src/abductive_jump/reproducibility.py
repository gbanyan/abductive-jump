from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

TRACKED_OUTPUTS = (
    "artifacts/world_manifest.parquet",
    "artifacts/world_ground_truth.parquet",
    "artifacts/incumbent_oracle.parquet",
    "artifacts/candidate_theories.parquet",
    "artifacts/intervention_predictions.parquet",
    "artifacts/mutation_trace.parquet",
    "artifacts/confirmatory_jump_gate_results.parquet",
    "artifacts/confirmatory_no_jump_controls.parquet",
    "artifacts/proposal_reasoning_factorial.parquet",
    "artifacts/condition_summary.parquet",
    "artifacts/confirmatory_comparisons.parquet",
    "artifacts/ablation_summary.parquet",
    "artifacts/compute_quality_frontier.parquet",
    "artifacts/seed_sensitivity.parquet",
    "artifacts/per_family_results.parquet",
    "artifacts/negative_controls.parquet",
    "artifacts/negative_controls_summary.json",
    "artifacts/hypothesis_genome_validation.parquet",
    "artifacts/hypothesis_genome_validation_summary.json",
    "artifacts/quality_diversity_archive.parquet",
    "artifacts/quality_diversity_archive_summary.json",
    "artifacts/final_claim_matrix.csv",
    "artifacts/final_verdict.json",
    "artifacts/replay-validation.json",
    "docs/abductive-jump-preregistration.md",
    "reports/abductive-jump-final.md",
    "reports/abductive-jump-reviewer2.md",
    "reports/completion-audit.md",
)

RAW_TRACES = (
    "artifacts/confirmatory/primary-jump/llm_calls.jsonl",
    "artifacts/confirmatory/primary-control/llm_calls.jsonl",
    "artifacts/confirmatory/factorial-jump/llm_calls.jsonl",
    "artifacts/confirmatory/factorial-control/llm_calls.jsonl",
    "artifacts/confirmatory/ablation-a6-jump/llm_calls.jsonl",
    "artifacts/confirmatory/ablation-a6-control/llm_calls.jsonl",
)


def run(root: Path) -> dict[str, Any]:
    files = {}
    for relative in TRACKED_OUTPUTS:
        path = root / relative
        payload = path.read_bytes()
        record: dict[str, Any] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        }
        if path.suffix == ".parquet":
            table = pq.read_table(path)
            record["rows"] = table.num_rows
            record["columns"] = len(table.column_names)
        files[relative] = record
    manifest = {
        "preregistration_commit": "895ebb9118ffd0046825b88868621f2a70f69f61",
        "replay_verified_candidates": 10_800,
        "preregistered_llm_calls": 32_400,
        "triggered_secondary_llm_calls": 3_600,
        "files": files,
        "raw_traces": {
            relative: {
                "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest(),
                "bytes": (root / relative).stat().st_size,
                "lines": sum(1 for _ in (root / relative).open()),
                "gitignored": True,
            }
            for relative in RAW_TRACES
        },
    }
    (root / "artifacts" / "reproducibility-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return manifest


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(run(root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
