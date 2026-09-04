#!/usr/bin/env python3
"""Materialize and hash the single-condition fair-interface protocol before inference."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from abductive_jump.fair_interface import operator_vocabulary, response_format

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "nmi_fair_interface_v1"
CONFIG_PATH = BASE / "configs" / "deepseek_fair_cself.json"
PROTOCOL_PATH = BASE / "protocol.json"
PANEL = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "panel_manifest.json"
NATIVE = (
    ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "configs" / "deepseek_native_cself.json"
)


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if (BASE / "results").exists() and any((BASE / "results").iterdir()):
        raise ValueError("refusing to rematerialize after fair-interface results exist")
    native = json.loads(NATIVE.read_text())
    panel = json.loads(PANEL.read_text())
    config = {
        "experiment_id": "NMI-FAIR-INTERFACE-V1::deepseek_fair_cself",
        "sensitivity_panel_id": native["sensitivity_panel_id"],
        "role": "grammar-valid, reasoning/answer-separated proposal-interface sensitivity",
        "conditions": ["C_SELF_LLM_COMPOSITION"],
        "families": native["families"],
        "world_seeds": native["world_seeds"],
        "candidate_slots": native["candidate_slots"],
        "self_plans_per_slot": native["self_plans_per_slot"],
        "max_depth": native["max_depth"],
        "primitive_operation_budget": native["primitive_operation_budget"],
        "search_breadth": native["search_breadth"],
        "gate_thresholds": native["gate_thresholds"],
        "no_jump": False,
        "phase": native["phase"],
        "model": native["model"],
        "revision": native["revision"],
        "quantization": native["quantization"],
        "engine": native["engine"],
        "engine_version": native["engine_version"],
        "context_limit": native["context_limit"],
        "concurrency": native["concurrency"],
        "transport_retries": native["transport_retries"],
        "decoding_seed_base": 520_000_001,
        "search_seed_base": native["search_seed_base"],
        "deliberation_generation": {
            "reasoning_effort": "max",
            "max_tokens": 4096,
            "temperature": 0.2,
            "top_p": 0.95,
        },
        "serialization_generation": {
            "reasoning_effort": "none",
            "max_tokens": 4096,
            "temperature": 0.2,
            "top_p": 0.95,
        },
        "calls_per_slot": 2,
        "semantic_feedback": False,
        "outcome_feedback": False,
        "validator_repair_attempts": 0,
        "response_format_sha256": hashlib.sha256(
            json.dumps(response_format(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "primitive_vocabulary": list(operator_vocabulary()),
        "historical_native_config": str(NATIVE.relative_to(ROOT)),
        "historical_native_config_sha256": digest(NATIVE),
        "panel_manifest": str(PANEL.relative_to(ROOT)),
        "panel_manifest_sha256": digest(PANEL),
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(canonical(config))
    tracked_code = [
        ROOT / "src" / "abductive_jump" / "fair_interface.py",
        ROOT / "src" / "abductive_jump" / "fair_interface_experiment.py",
        ROOT / "src" / "abductive_jump" / "fair_interface_analysis.py",
        ROOT / "scripts" / "finalize_nmi_fair_interface_v1.py",
        Path(__file__),
    ]
    protocol = {
        "schema_version": "nmi-fair-interface-protocol-v1",
        "status": "frozen_before_inference",
        "objective": (
            "Test whether grammar-valid serialization with separate reasoning and answer budgets "
            "allows DeepSeek representation plans to reach executable and J1-J5 gates."
        ),
        "scope": "one fixed-panel sensitivity; not a replacement confirmatory population",
        "fixed_worlds": 96,
        "worlds_per_family": 12,
        "candidate_slots_per_world": 3,
        "plans_per_slot": 16,
        "steps_per_plan": 4,
        "representation_opportunities_per_world": 48,
        "model_calls_per_world": 6,
        "expected_model_calls": 576,
        "interpretation": {
            "executable_then_late_gate_failure": "supports a bounded proposal-quality limitation",
            "validated_success": "shows that prior autonomous zero rates were interface-bound",
            "pre_executable_failure": "supports a remaining reference/operation planning limitation, not universal model incapacity",
        },
        "prohibited_claims": [
            "LLMs generally cannot expand hypothesis spaces",
            "frontier models are intrinsically incapable of scientific reasoning",
            "other discovery systems misattribute model capability without direct audit",
        ],
        "config": str(CONFIG_PATH.relative_to(ROOT)),
        "config_sha256": digest(CONFIG_PATH),
        "code_sha256": {str(path.relative_to(ROOT)): digest(path) for path in tracked_code},
        "panel_selected_worlds_sha256": hashlib.sha256(
            json.dumps(panel["selected_worlds"], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "operational_probes": {
            "research_worlds_used": False,
            "json_schema_supported": True,
            "one_of_supported": True,
            "excluded_from_analysis": True,
        },
    }
    PROTOCOL_PATH.write_text(canonical(protocol))
    print(canonical(protocol), end="")


if __name__ == "__main__":
    main()
