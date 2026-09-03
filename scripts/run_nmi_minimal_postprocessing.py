"""Run completion-locked replay, analysis and reporting with zero model calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from abductive_jump.minimal_sensitivity_analysis import run as analyze
from abductive_jump.minimal_sensitivity_replay import replay_all
from abductive_jump.minimal_sensitivity_reports import build as build_reports


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    base = root / "experiments" / "nmi_minimal_sensitivity_v1"

    replay = replay_all(root)
    if replay["status"] != "complete_verified" or replay["mismatches"] != 0:
        raise ValueError("postprocessing stopped: replay was not complete with zero mismatches")
    analysis = analyze(root)
    reports = build_reports(root)

    outputs = [
        base / "analysis" / "replay_report.json",
        base / "analysis" / "analysis.json",
        base / "analysis" / "world_summary.csv",
        base / "analysis" / "per_family.csv",
        base / "analysis" / "paired_world_differences.csv",
        base / "analysis" / "gate_attrition.csv",
        base / "analysis" / "compute_ledger.csv",
        base / "analysis" / "minimal_sensitivity_report.md",
        root / "reports" / "figures" / "minimal_sensitivity" / "figure1-world-jsr.svg",
        root / "reports" / "figures" / "minimal_sensitivity" / "figure2-gate-attrition.svg",
        root / "reports" / "figures" / "minimal_sensitivity" / "figure3-per-family.svg",
    ]
    missing = [str(path) for path in outputs if not path.is_file()]
    if missing:
        raise ValueError(f"postprocessing outputs missing: {missing}")
    manifest = {
        "status": "complete_verified",
        "model_calls_made": 0,
        "replay_candidate_rows": replay["candidate_rows"],
        "replay_mismatches": replay["mismatches"],
        "analysis_conditions": len(analysis["world_summary"]),
        "reports": reports,
        "output_sha256": {str(path.relative_to(root)): digest(path) for path in outputs},
    }
    destination = base / "analysis" / "postprocessing_manifest.json"
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
