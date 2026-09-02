from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED = (
    "artifacts/compositional-execution-source-audit.json",
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
    "reports/compositional-completion-audit.md",
    "reports/figures/compositional/figure1-atomic-vs-composition.svg",
    "reports/figures/compositional/figure2-jsr.svg",
    "reports/figures/compositional/figure3-rho-by-family.svg",
    "reports/figures/compositional/figure4-success-vs-depth.svg",
    "reports/figures/compositional/figure5-heldout.svg",
    "reports/figures/compositional/figure6-jsr-vs-fjr.svg",
    "reports/figures/compositional/figure7-cost-frontier.svg",
    "artifacts/compositional/confirmatory-existing/run_audit.json",
    "artifacts/compositional/confirmatory-existing-control/run_audit.json",
    "artifacts/compositional/confirmatory-heldout/run_audit.json",
    "artifacts/compositional/confirmatory-heldout-control/run_audit.json",
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


def _validate_required_outputs(root: Path) -> None:
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    if missing:
        raise ValueError(f"missing compositional outputs: {missing}")
    empty = [name for name in REQUIRED if (root / name).stat().st_size == 0]
    if empty:
        raise ValueError(f"empty compositional outputs: {empty}")
    incomplete_audit = root / "reports" / "compositional-completion-audit.md"
    if "| PENDING |" in incomplete_audit.read_text():
        raise ValueError("compositional completion audit still contains PENDING requirements")
    for name in REQUIRED:
        if name.endswith(".svg") and not (root / name).read_text().lstrip().startswith("<svg"):
            raise ValueError(f"invalid SVG output: {name}")


def run(root: Path) -> dict[str, Any]:
    _validate_required_outputs(root)
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
    execution_source = json.loads(
        (root / "artifacts" / "compositional-execution-source-audit.json").read_text()
    )
    if not execution_source["local_remote_sha256_match"]:
        raise ValueError("execution-source audit did not establish local/remote parity")
    if execution_source["aggregate_confirmatory_outcomes_inspected"]:
        raise ValueError("execution-source audit reports premature confirmatory inspection")
    for name, expected_hash in execution_source["sha256"].items():
        actual = _hash(root / name)
        if actual != expected_hash:
            raise ValueError(f"execution source changed: {name}")
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
        "execution_source_hashes_verified": True,
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
