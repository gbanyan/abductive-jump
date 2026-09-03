"""Integrity checks for the previously frozen Phi-4 budget sensitivity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BUDGET_SHARDS = {
    "phi4_4bit_budget_known": ("known_jump", 400, 2400),
    "phi4_4bit_budget_heldout": ("heldout_jump", 100, 600),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def budget_config_path(root: Path, split: str) -> Path:
    return root / "experiments" / "nmi_extension_v1" / "configs" / "phi_budget" / f"{split}.json"


def budget_run_dir(root: Path, split: str) -> Path:
    return root / "experiments" / "nmi_extension_v1" / "results" / "phi_budget" / split


def _require_only_budget_changed(root: Path, config: dict[str, Any]) -> None:
    historical = load_json(root / config["historical_source_config"])
    invariant_keys = (
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
    )
    for key in invariant_keys:
        if config[key] != historical[key]:
            raise ValueError(f"Phi budget invariant differs from historical config: {key}")
    expected_generation = {**historical["generation"], "max_tokens": 2048}
    if historical["generation"]["max_tokens"] != 700 or config["generation"] != expected_generation:
        raise ValueError("Phi budget condition must change only max_tokens from 700 to 2048")
    if config.get("validator_repair_attempts") != 0 or "response_format" in config:
        raise ValueError("Phi budget condition must not add repair or constrained decoding")


def require_phi_budget_finalized(root: Path) -> dict[str, dict[str, Any]]:
    base = root / "experiments" / "nmi_minimal_sensitivity_v1"
    amendment_path = base / "protocol_amendment_002.json"
    amendment = load_json(amendment_path)
    if amendment.get("amendment_id") != "NMI-MIN-SENS-V1-AMENDMENT-002":
        raise ValueError("missing Phi budget integration amendment")
    panel_path = base / "panel_manifest.json"
    if digest(panel_path) != amendment["analysis_lock"]["panel_manifest_sha256"]:
        raise ValueError("Phi budget paired-panel manifest hash mismatch")

    source = amendment["source_protocol"]
    source_results = amendment["source_results"]
    validations: dict[str, dict[str, Any]] = {}
    for label, (split, expected_worlds, expected_calls) in BUDGET_SHARDS.items():
        config_path = budget_config_path(root, split)
        validation_path = budget_run_dir(root, split) / "validation.json"
        config_hash_key = (
            "known_config_sha256" if split == "known_jump" else "heldout_config_sha256"
        )
        validation_hash_key = (
            "known_validation_sha256" if split == "known_jump" else "heldout_validation_sha256"
        )
        if digest(config_path) != source[config_hash_key]:
            raise ValueError(f"{label} frozen config hash mismatch")
        if digest(validation_path) != source_results[validation_hash_key]:
            raise ValueError(f"{label} validation manifest hash mismatch")
        config = load_json(config_path)
        _require_only_budget_changed(root, config)
        validation = load_json(validation_path)
        expected_config_hash = digest(config_path)
        if validation.get("status") != "complete_verified":
            raise ValueError(f"{label} is not complete_verified")
        if validation.get("config_sha256") != expected_config_hash:
            raise ValueError(f"{label} config hash does not match validation")
        if int(validation.get("world_rows", -1)) != expected_worlds:
            raise ValueError(f"{label} world count mismatch")
        if int(validation.get("candidate_rows", -1)) != expected_worlds * int(
            config["candidate_slots"]
        ):
            raise ValueError(f"{label} candidate count mismatch")
        if int(validation.get("llm_calls", -1)) != expected_calls:
            raise ValueError(f"{label} call count mismatch")
        if int(validation.get("transport_error_records", -1)) != 0:
            raise ValueError(f"{label} contains transport errors")
        for relative, expected_hash in validation["artifacts"].items():
            artifact = root / relative
            if not artifact.is_file() or digest(artifact) != expected_hash:
                raise ValueError(f"{label} artifact hash mismatch: {relative}")
        validations[label] = validation
    return validations
