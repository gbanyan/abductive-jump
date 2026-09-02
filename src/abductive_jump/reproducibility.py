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
    "artifacts/final_claim_matrix.csv",
    "artifacts/final_verdict.json",
    "artifacts/replay-validation.json",
    "docs/abductive-jump-preregistration.md",
    "reports/abductive-jump-final.md",
    "reports/abductive-jump-reviewer2.md",
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
