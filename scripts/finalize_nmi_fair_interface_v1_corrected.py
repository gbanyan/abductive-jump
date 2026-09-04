#!/usr/bin/env python3
"""Correct one metadata-location defect in the frozen fair-interface verifier.

The frozen verifier expected ``engine`` on every call-ledger row, although the
runner records engine metadata in ``summary.json.model_manifests``.  This
wrapper leaves the frozen verifier and all inference artifacts unchanged,
checks the engine metadata where it is actually stored, and then reuses every
other frozen replay check while omitting only that absent per-call field.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "nmi_fair_interface_v1"
RUN_DIR = BASE / "results" / "deepseek_fair_cself"
FROZEN_FINALIZER = ROOT / "scripts" / "finalize_nmi_fair_interface_v1.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    protocol = json.loads((BASE / "protocol.json").read_text())
    config = json.loads((BASE / "configs" / "deepseek_fair_cself.json").read_text())
    shard_summaries = [
        json.loads(
            (BASE / "shards" / "results" / f"shard_{index}" / "summary.json").read_text()
        )
        for index in range(4)
    ]

    expected_finalizer_hash = protocol["code_sha256"][
        "scripts/finalize_nmi_fair_interface_v1.py"
    ]
    if digest(FROZEN_FINALIZER) != expected_finalizer_hash:
        raise ValueError("frozen finalizer no longer matches the protocol hash")

    for stage in ("deliberation", "serialization"):
        expected_generation = config[f"{stage}_generation"]
        expected = {
            "model": config["model"],
            "revision": config["revision"],
            "quantization": config["quantization"],
            "engine": config["engine"],
            "engine_version": config["engine_version"],
            "context_limit": int(config["context_limit"]),
            "temperature": float(expected_generation["temperature"]),
            "top_p": float(expected_generation["top_p"]),
            "max_tokens": int(expected_generation["max_tokens"]),
            "reasoning_effort": str(expected_generation["reasoning_effort"]),
            "transport_retries": int(config.get("transport_retries", 0)),
        }
        for index, shard_summary in enumerate(shard_summaries):
            manifest = shard_summary["model_manifests"][stage]
            mismatches = [key for key, value in expected.items() if manifest.get(key) != value]
            if mismatches:
                raise ValueError(f"shard {index} {stage} model manifest mismatch: {mismatches}")

    initial_paths: dict[str, str] = {}
    for name in ("validation.json", "replay_report.json"):
        source = RUN_DIR / name
        if source.is_file():
            archived = RUN_DIR / f"initial_{name}"
            if not archived.exists():
                shutil.copy2(source, archived)
            initial_paths[str(archived.relative_to(ROOT))] = digest(archived)

    spec = importlib.util.spec_from_file_location("frozen_fair_finalizer", FROZEN_FINALIZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen finalizer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    frozen_compare = module.compare

    def corrected_compare(
        saved: dict[str, Any], expected: dict[str, Any], prefix: str
    ) -> list[str]:
        local_expected = dict(expected)
        if "engine" in local_expected and "engine" not in saved:
            local_expected.pop("engine")
        return frozen_compare(saved, local_expected, prefix)

    module.compare = corrected_compare
    previous_argv = sys.argv
    try:
        sys.argv = [str(FROZEN_FINALIZER), "--experiment-dir", str(BASE)]
        module.main()
    finally:
        sys.argv = previous_argv

    correction = {
        "schema_version": "nmi-fair-interface-verifier-correction-v1",
        "model_calls_made": 0,
        "scope": "verification metadata only; no inference or scientific artifact changed",
        "defect": (
            "The frozen verifier expected engine on each call-ledger row, but the frozen "
            "runner stores engine metadata in summary.json.model_manifests."
        ),
        "correction": (
            "Verified engine and engine_version in both stage manifests and omitted only the "
            "absent per-call engine comparison; all other frozen replay checks were reused."
        ),
        "frozen_finalizer_sha256": digest(FROZEN_FINALIZER),
        "initial_reports": initial_paths,
        "verified_stage_manifests": {
            stage: shard_summaries[0]["model_manifests"][stage]
            for stage in ("deliberation", "serialization")
        },
        "verified_shards": len(shard_summaries),
    }
    correction_path = RUN_DIR / "verification_correction_001.json"
    correction_path.write_text(json.dumps(correction, indent=2, sort_keys=True) + "\n")

    for name in ("validation.json", "replay_report.json"):
        path = RUN_DIR / name
        report = json.loads(path.read_text())
        report["verification_correction"] = str(correction_path.relative_to(ROOT))
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
