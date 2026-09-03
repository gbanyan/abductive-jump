"""Fail-closed pre-run verifier for NMI-MIN-SENS-V1."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "nmi_minimal_sensitivity_v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(*, require_prerun_empty: bool = True) -> dict[str, Any]:
    protocol = read_json(BASE / "protocol.json")
    panel = read_json(BASE / "panel_manifest.json")
    require(protocol["protocol_id"] == "NMI-MIN-SENS-V1", "wrong protocol id")
    require(protocol["status"] == "prospective_freeze", "protocol is not frozen")
    require(digest(BASE / "panel_manifest.json") == protocol["panel_manifest_sha256"], "panel hash mismatch")

    worlds = panel["selected_worlds"]
    require(len(worlds) == 96, "panel must contain 96 worlds")
    require(len({(row["family"], row["world_seed"], row["world_id"]) for row in worlds}) == 96, "panel worlds must be unique")
    family_counts = Counter(str(row["family"]) for row in worlds)
    require(set(family_counts.values()) == {12}, "panel must contain 12 worlds per family")
    require(sum(bool(row["p2_positive_control"]) for row in worlds) == 40, "P2 panel must contain 40 worlds")

    for name, expected in protocol["config_sha256"].items():
        path = BASE / "configs" / f"{name}.json"
        require(digest(path) == expected, f"config hash mismatch: {name}")
    for name, expected in protocol["code_sha256"].items():
        require(digest(ROOT / name) == expected, f"code hash mismatch: {name}")
    for name, expected in protocol["runtime_manifest_sha256"].items():
        require(digest(ROOT / name) == expected, f"runtime hash mismatch: {name}")

    configs = {
        name: read_json(BASE / "configs" / f"{name}.json")
        for name in protocol["config_sha256"]
    }
    panel_seeds = panel["selected_seeds"]
    p2_seeds = panel["p2_positive_control"]["selected_seeds"]
    for name, config in configs.items():
        require(config["candidate_slots"] == 3, f"candidate slots changed: {name}")
        require(config["max_depth"] == 4, f"plan depth changed: {name}")
        require(config["families"] == panel["families"], f"families changed: {name}")
        expected_seeds = p2_seeds if name == "deepseek_p2" else panel_seeds
        require(config["world_seeds"] == expected_seeds, f"seed panel mismatch: {name}")
        require(config["gate_thresholds"] == configs["phi8_cself"]["gate_thresholds"], f"gate thresholds changed: {name}")

    phi = configs["phi8_cself"]
    require(phi["revision"] == "2db69c1c3e91a05d2c64a3185acfbaf36f744e25", "wrong Phi revision")
    require(phi["quantization"] == "bitsandbytes-8bit-runtime", "wrong Phi quantization")
    require(phi["generation"]["max_tokens"] == 700, "Phi completion budget changed")
    require(phi["validator_repair_attempts"] == 0, "Phi no-repair condition changed")
    require("reasoning_effort" not in phi, "Phi must not declare unsupported reasoning effort")

    matched = configs["deepseek_matched_cself"]
    require(matched["reasoning_effort"] == "none", "matched DeepSeek reasoning must be none")
    require(matched["generation"]["max_tokens"] == 700, "matched budget must be 700")
    native = configs["deepseek_native_cself"]
    require(native["reasoning_effort"] == "max", "native DeepSeek reasoning must be max")
    require(native["generation"]["max_tokens"] == 4096, "native budget must be 4096")

    repair = configs["phi8_cself_repair"]
    require(repair["validator_repair_attempts"] == 1, "repair must permit exactly one attempt")
    for key in ("world_seeds", "families", "candidate_slots", "self_plans_per_slot", "max_depth", "gate_thresholds"):
        require(repair[key] == phi[key], f"repair changed invariant: {key}")
    require(protocol["offline_attrition"]["repair_triggered"] is True, "repair trigger absent")
    require(protocol["offline_attrition"]["observed_pre_executable_failure_rate"] > 0.25, "repair trigger below threshold")

    p2 = configs["deepseek_p2"]
    require(p2["runner_module"] == "abductive_jump.supplied_representation_experiment", "wrong P2 runner")
    require(p2["conditions"] == ["C5_ORACLE_REPRESENTATION"], "wrong P2 condition")
    require(p2["calls_per_world"] == 3, "P2 must use one call per candidate slot")
    require(p2["deterministic_overwrites"] == ["representation only"], "P2 may overwrite only representation")

    if require_prerun_empty:
        results = BASE / "results"
        require(not results.exists() or not any(results.iterdir()), "new model results exist before unlock")
    return {
        "verified": True,
        "panel_worlds": len(worlds),
        "p2_worlds": sum(bool(row["p2_positive_control"]) for row in worlds),
        "configs": len(configs),
        "repair_triggered": True,
        "prerun_empty": require_prerun_empty,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
