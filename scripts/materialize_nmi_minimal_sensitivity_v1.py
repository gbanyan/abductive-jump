"""Materialize the frozen minimal NMI sensitivity protocol and configs."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from abductive_jump.minimal_sensitivity import PANEL_SALT, select_panel_seeds

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "experiments" / "nmi_extension_v1"
DEST = ROOT / "experiments" / "nmi_minimal_sensitivity_v1"
HISTORICAL_CONFIG = ROOT / "configs" / "compositional-confirmatory-existing.json"
OFFLINE_REPORT = DEST / "offline" / "historical_cself_attrition.json"
HISTORICAL_PLANS = ROOT / "artifacts" / "compositional" / "confirmatory-existing" / "llm_self_plans.parquet"
FAMILIES = (
    "latent_common_cause",
    "unification",
    "hidden_regimes",
    "property_to_relation",
    "state_invention",
    "coordinate_transform",
    "causal_ambiguity",
    "meta_law",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def base_config(treatment: str) -> dict[str, Any]:
    source = {
        "phi8_cself": OLD / "configs" / "phi8_precision" / "known_jump.json",
        "phi8_cself_repair": OLD / "configs" / "phi8_precision" / "known_jump.json",
        "deepseek_matched_cself": OLD / "configs" / "deepseek_matched" / "known_jump.json",
        "deepseek_native_cself": OLD / "configs" / "deepseek_native" / "known_jump.json",
        "deepseek_p2": OLD / "configs" / "deepseek_native" / "known_jump.json",
    }[treatment]
    return deepcopy(read_json(source))


def materialize() -> dict[str, Any]:
    historical = read_json(HISTORICAL_CONFIG)
    source_seeds = [int(seed) for seed in historical["world_seeds"]]
    panel_seeds = select_panel_seeds(source_seeds, 12)
    p2_seeds = panel_seeds[:5]
    offline = read_json(OFFLINE_REPORT)
    if not offline["repair_trigger"]["triggered"]:
        raise ValueError("repair condition may not be materialized without the frozen trigger")

    historical_rows = pq.read_table(
        HISTORICAL_PLANS, columns=["family", "world_seed", "world_id"]
    ).to_pylist()
    historical_world_ids = {
        (str(row["family"]), int(row["world_seed"])): str(row["world_id"])
        for row in historical_rows
    }
    selected_worlds = [
        {
            "family": family,
            "world_seed": seed,
            "world_id": historical_world_ids[(family, seed)],
            "p2_positive_control": seed in p2_seeds,
        }
        for family in FAMILIES
        for seed in panel_seeds
    ]
    panel = {
        "schema_version": "nmi-minimal-sensitivity-panel-v1",
        "panel_id": "NMI-MIN-SENS-V1-PANEL-96",
        "selection_status": "frozen_before_new_model_calls",
        "selection_method": "12 lowest SHA-256 ranks over the 50 historical seeds",
        "selection_salt": PANEL_SALT,
        "outcome_fields_used": [],
        "source": {
            "historical_config": str(HISTORICAL_CONFIG.relative_to(ROOT)),
            "historical_config_sha256": digest(HISTORICAL_CONFIG),
            "eligible_seeds": source_seeds,
            "eligible_families": list(FAMILIES),
        },
        "selected_seeds": panel_seeds,
        "selected_worlds": selected_worlds,
        "families": list(FAMILIES),
        "worlds_per_family": 12,
        "total_worlds": 96,
        "p2_positive_control": {
            "selected_seeds": p2_seeds,
            "worlds_per_family": 5,
            "total_worlds": 40,
            "reason": (
                "DeepSeek max-reasoning calls are materially slower; 40 balanced worlds are the "
                "predeclared minimum positive control permitted by the targeted plan."
            ),
        },
    }
    write_json(DEST / "panel_manifest.json", panel)

    configs: dict[str, dict[str, Any]] = {}
    for treatment in (
        "phi8_cself",
        "deepseek_matched_cself",
        "deepseek_native_cself",
        "deepseek_p2",
        "phi8_cself_repair",
    ):
        config = base_config(treatment)
        config["families"] = list(FAMILIES)
        config["world_seeds"] = p2_seeds if treatment == "deepseek_p2" else panel_seeds
        config["extension_experiment_id"] = f"NMI-MIN-SENS-V1::{treatment}"
        config["sensitivity_panel_id"] = panel["panel_id"]
        config["historical_source_config_sha256"] = digest(HISTORICAL_CONFIG)
        config["transport_retries"] = 2
        config["candidate_slots"] = 3
        config["self_plans_per_slot"] = 16
        config["max_depth"] = 4
        config["validator_repair_attempts"] = 0
        config["conditions"] = ["C_SELF_LLM_COMPOSITION"]
        config["runner_module"] = "abductive_jump.compositional_experiment"
        config["generation"]["temperature"] = 0.2
        config["generation"]["top_p"] = 0.95
        if treatment.startswith("phi8"):
            config["generation"]["max_tokens"] = 700
            config.pop("reasoning_effort", None)
            config["sensitivity_role"] = "same-revision 8-bit precision-and-serving-engine sensitivity"
        elif treatment == "deepseek_matched_cself":
            config["generation"]["max_tokens"] = 700
            config["reasoning_effort"] = "none"
            config["sensitivity_role"] = "protocol-matched stronger-model substitution"
        else:
            config["generation"]["max_tokens"] = 4096
            config["reasoning_effort"] = "max"
            config["sensitivity_role"] = "model-native capability ceiling"
        if treatment == "deepseek_p2":
            config["conditions"] = ["C5_ORACLE_REPRESENTATION"]
            config["runner_module"] = "abductive_jump.supplied_representation_experiment"
            config["sensitivity_role"] = "balanced causal supplied-oracle-representation positive control"
            config["calls_per_world"] = 3
            config["model_authored_fields"] = [
                "expression",
                "explanation",
                "selected_intervention_ids",
            ]
            config["deterministic_overwrites"] = ["representation only"]
        if treatment == "phi8_cself_repair":
            config["validator_repair_attempts"] = 1
            config["sensitivity_role"] = "triggered one-structural-validator-repair sensitivity"
            config["repair_trigger_source_sha256"] = digest(OFFLINE_REPORT)
        configs[treatment] = config
        write_json(DEST / "configs" / f"{treatment}.json", config)

    config_hashes = {
        name: digest(DEST / "configs" / f"{name}.json") for name in sorted(configs)
    }
    code_paths = (
        ROOT / "src" / "abductive_jump" / "compositional_experiment.py",
        ROOT / "src" / "abductive_jump" / "llm.py",
        ROOT / "src" / "abductive_jump" / "historical_attrition.py",
        ROOT / "src" / "abductive_jump" / "minimal_sensitivity.py",
        ROOT / "src" / "abductive_jump" / "supplied_representation_experiment.py",
        ROOT / "scripts" / "analyze_historical_cself_attrition.py",
        ROOT / "scripts" / "materialize_nmi_minimal_sensitivity_v1.py",
        ROOT / "scripts" / "phi4_transformers_openai_server.py",
        ROOT / "scripts" / "verify_nmi_minimal_sensitivity_v1.py",
    )
    runtime_paths = (
        OLD / "runtime" / "deepseek_manifest.json",
        OLD / "runtime" / "phi4_manifest.json",
    )
    protocol = {
        "schema_version": "nmi-minimal-targeted-sensitivity-v1",
        "protocol_id": "NMI-MIN-SENS-V1",
        "authored_at_utc": "2026-09-03T04:42:15Z",
        "status": "prospective_freeze",
        "scope": "targeted sensitivity analysis; not a replacement confirmatory population",
        "historical_preservation": {
            "commit": "ae1ede683fdef09f2bf60f6e1052b60394ad6cf8",
            "tag": "nmi-phi4-frozen-2026-09",
            "branch": "nmi-phi4-frozen-archive-2026-09",
            "policy": "No historical result, prompt, seed, gate, or artifact may be overwritten.",
        },
        "panel_manifest_sha256": digest(DEST / "panel_manifest.json"),
        "config_sha256": config_hashes,
        "code_sha256": {str(path.relative_to(ROOT)): digest(path) for path in code_paths},
        "runtime_manifest_sha256": {
            str(path.relative_to(ROOT)): digest(path) for path in runtime_paths
        },
        "models": {
            "phi4_8bit": {
                "hf_repository": "microsoft/phi-4",
                "revision": "2db69c1c3e91a05d2c64a3185acfbaf36f744e25",
                "runtime": "Transformers 4.56.1 + bitsandbytes 0.47.0 load_in_8bit",
                "caveat": "precision and serving engine differ jointly from historical vLLM 4-bit",
            },
            "deepseek": {
                "hf_repository": "deepseek-ai/DeepSeek-V4-Flash-Vision-Exp",
                "revision": "86f746b36186f0e567729a5c06a8c918caba82a9",
                "api": "http://192.168.30.16:8888/v1",
                "model_alias": "deepseek-v4-flash-vision-exp",
                "reasoning_field": "message.reasoning",
                "supported_reasoning_effort": ["none", "low", "high", "max"],
                "identity_caveat": "not claimed identical to any other DeepSeek release",
            },
        },
        "offline_attrition": {
            "report": str(OFFLINE_REPORT.relative_to(ROOT)),
            "report_sha256": digest(OFFLINE_REPORT),
            "model_calls": 0,
            "repair_trigger_threshold": 0.25,
            "observed_pre_executable_failure_rate": offline["repair_trigger"][
                "pre_executable_failure_rate"
            ],
            "repair_triggered": True,
        },
        "core_runs": [
            "phi8_cself: 96 worlds, C_self, no repair, 700 completion tokens",
            "deepseek_matched_cself: same 96 worlds, reasoning_effort=none, 700 completion tokens",
            "deepseek_native_cself: same 96 worlds, reasoning_effort=max, 4096 completion tokens",
            (
                "deepseek_p2: balanced 40-world causal oracle-representation positive control, "
                "reasoning_effort=max, one model-authored law/intervention call per slot"
            ),
        ],
        "conditional_run": (
            "phi8_cself_repair: same 96 worlds, exactly one structural-only replacement repair; "
            "enabled prospectively because frozen historical pre-executable failure was 100%"
        ),
        "invariants": {
            "candidate_slots": 3,
            "self_plans_per_slot": 16,
            "steps_per_plan": 4,
            "representation_opportunities_per_world": 48,
            "interventions_per_retained_candidate": 1,
            "gates": "historical J0-J5 definitions and thresholds unchanged",
            "primitives": "historical generic primitive vocabulary unchanged",
            "hidden_information": "no outcome revealed before intervention commitment",
            "quality_reruns": "forbidden",
        },
        "repair_feedback": {
            "attempts": 1,
            "replacement_not_augmentation": True,
            "allowed": [
                "JSON/schema error",
                "unknown operation",
                "invalid argument",
                "invalid reference",
                "type error",
                "arity error",
                "non-executable plan syntax",
            ],
            "forbidden": [
                "hidden truth",
                "target distance",
                "J3 direction",
                "intervention outcome",
                "J4",
                "J5",
                "simulator-derived semantic hints",
            ],
        },
        "statistics": {
            "replicate": "world",
            "primary": [
                "exact counts",
                "world-level JSR",
                "Wilson 95% intervals",
                "paired world-level differences",
                "per-family descriptive results",
                "gate attrition",
            ],
            "candidate_level_significance_tests": False,
            "distinction": "original n=400 confirmatory versus new n=96 sensitivity panel",
        },
        "interpretation_constraints": [
            "Phi-4 8-bit differs jointly in numerical precision and serving engine.",
            "DeepSeek native is not compute-matched to Phi-4 or DeepSeek matched.",
            "The served checkpoint is identified only as deepseek-ai/DeepSeek-V4-Flash-Vision-Exp at the recorded local revision.",
            "No result is invalidated for weakening the original narrative.",
            "Stop after the listed core and triggered repair conditions; do not expand automatically.",
        ],
        "unlock_rule": (
            "No new benchmark model call until protocol, panel, configs, code and tests are committed, "
            "pushed, tagged, and the remote tag is verified."
        ),
    }
    write_json(DEST / "protocol.json", protocol)
    return {"panel": panel, "protocol": protocol}


if __name__ == "__main__":
    result = materialize()
    print(json.dumps({"selected_seeds": result["panel"]["selected_seeds"]}, sort_keys=True))
