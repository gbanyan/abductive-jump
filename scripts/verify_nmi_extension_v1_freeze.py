#!/usr/bin/env python3
"""Fail-closed checks for the NMI extension v1 protocol/config freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "experiments" / "nmi_extension_v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def main() -> None:
    protocol = load(EXT / "protocol.json")
    manifest = load(EXT / "configs" / "config_manifest.json")
    expected_audits = {
        "component_audit_sha256": ROOT / "docs" / "nmi_component_audit.md",
        "component_causality_matrix_sha256": ROOT / "docs" / "nmi_component_causality_matrix.md",
        "deepseek_runtime_manifest_sha256": EXT / "runtime" / "deepseek_manifest.json",
        "phi4_runtime_manifest_sha256": EXT / "runtime" / "phi4_manifest.json",
        "operational_config_manifest_sha256": EXT / "configs" / "config_manifest.json",
    }
    for key, path in expected_audits.items():
        assert protocol["audit_inputs"][key] == sha(path), (key, path)
    generator = ROOT / manifest["generator"]
    assert manifest["generator_sha256"] == sha(generator)
    for relative, expected in manifest["configs"].items():
        path = ROOT / relative
        assert path.is_file() and sha(path) == expected, relative
        config = load(path)
        assert config["candidate_slots"] == 3
        assert config["gate_thresholds"] == {
            "delta_cf": 0.1,
            "delta_falsification": 0.1,
            "epsilon_candidate_obs": 1e-12,
            "epsilon_falsification": 1e-12,
            "epsilon_obs": 1e-12,
            "min_prediction_separation": 0.5,
        }
        treatment = config["treatment_id"]
        if "factorial_" not in path.name:
            assert config["conditions"] == ["C_SELF_LLM_COMPOSITION"]
            assert config["self_plans_per_slot"] == 16
            assert config["max_depth"] == 4
            assert config["search_breadth"] == 48
            assert config["primitive_operation_budget"] == 192
        if treatment == "phi_budget":
            historical = load(ROOT / config["historical_source_config"])
            for key in (
                "model",
                "revision",
                "quantization",
                "engine",
                "engine_version",
                "context_limit",
                "prompt_template",
                "families",
                "world_seeds",
                "gate_thresholds",
                "candidate_slots",
                "max_depth",
                "search_breadth",
                "self_plans_per_slot",
                "primitive_operation_budget",
                "decoding_seed_base",
                "search_seed_base",
                "no_jump",
            ):
                assert config[key] == historical[key], (path, key)
            assert historical["generation"]["max_tokens"] == 700
            assert config["generation"] == {**historical["generation"], "max_tokens": 2048}
            assert config["validator_repair_attempts"] == 0
            assert "response_format" not in config
    server = ROOT / protocol["models"]["phi4_precision_runtime"]["server_script"]
    assert protocol["models"]["phi4_precision_runtime"]["server_script_sha256"] == sha(server)
    assert not (EXT / "results").exists(), "confirmatory results existed before freeze verification"
    print(
        json.dumps(
            {
                "protocol_id": protocol["protocol_id"],
                "configs_verified": len(manifest["configs"]),
                "confirmatory_results_present": False,
                "status": "freeze_candidate_verified",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
