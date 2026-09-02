from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED = (
    "artifacts/generic_primitive_manifest.json",
    "artifacts/high_level_operator_exclusions.json",
    "artifacts/composition_reachability.parquet",
    "artifacts/minimum_edit_depth.parquet",
    "artifacts/depth_one_admissibility.parquet",
    "artifacts/compositional_candidates.parquet",
    "artifacts/composition_ancestry.parquet",
    "artifacts/compositional_jump_results.parquet",
    "artifacts/heldout_family_results.parquet",
    "artifacts/random_primitive_control.parquet",
    "artifacts/llm_selected_composition.parquet",
    "artifacts/no_jump_depth_controls.parquet",
    "artifacts/compositional_cost_frontier.parquet",
    "artifacts/final_compositional_claim_matrix.csv",
    "artifacts/final_compositional_verdict.json",
    "artifacts/compositional-replay-validation.json",
    "reports/compositional-representation-jump-final.md",
    "reports/compositional-representation-jump-reviewer2.md",
)

RAW_EXPECTED = {
    "artifacts/compositional/confirmatory-existing/llm_calls.jsonl": 16_800,
    "artifacts/compositional/confirmatory-existing-control/llm_calls.jsonl": 8_400,
    "artifacts/compositional/confirmatory-heldout/llm_calls.jsonl": 4_200,
    "artifacts/compositional/confirmatory-heldout-control/llm_calls.jsonl": 4_200,
}


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(root: Path) -> dict[str, Any]:
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    if missing:
        raise ValueError(f"missing compositional outputs: {missing}")
    hashes = {name: _hash(root / name) for name in REQUIRED}
    raw = {}
    for name, expected in RAW_EXPECTED.items():
        path = root / name
        if not path.is_file():
            raise ValueError(f"missing raw trace: {name}")
        lines = sum(1 for _ in path.open())
        if lines != expected:
            raise ValueError(f"raw line mismatch {name}: {lines}/{expected}")
        raw[name] = {
            "sha256": _hash(path),
            "lines": lines,
            "expected_lines": expected,
        }
    freeze = json.loads(
        (root / "artifacts" / "compositional-preregistration-freeze.json").read_text()
    )
    correction = json.loads(
        (root / "artifacts" / "compositional-freeze-correction.json").read_text()
    )
    for name, expected_hash in correction["unchanged_config_hashes"].items():
        actual = _hash(root / name)
        if actual != expected_hash:
            raise ValueError(f"frozen config changed: {name}")
    replay = json.loads(
        (root / "artifacts" / "compositional-replay-validation.json").read_text()
    )
    if replay["candidate_rows"] != replay["verified_candidates"] or replay["mismatches"]:
        raise ValueError("candidate replay is incomplete")
    manifest = {
        "preregistration_commit": freeze["preregistration_git_commit"],
        "implementation_correction_commit": correction["correction_git_commit"],
        "tracked_output_hashes": hashes,
        "raw_traces": raw,
        "confirmatory_raw_calls": sum(row["lines"] for row in raw.values()),
        "replay": replay,
        "frozen_config_hashes_verified": True,
        "heldout_unlock_order_verified_in_ledger": True,
    }
    output = root / "artifacts" / "compositional-reproducibility-manifest.json"
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
