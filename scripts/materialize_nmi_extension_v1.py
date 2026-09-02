#!/usr/bin/env python3
"""Materialize prospectively specified extension configs from frozen AJ5/CJ5 configs."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "nmi_extension_v1" / "configs"

AJ_SHARDS = {
    "factorial_jump": ROOT / "configs" / "confirmatory-factorial-jump.json",
    "factorial_control": ROOT / "configs" / "confirmatory-factorial-control.json",
}
CJ_SHARDS = {
    "known_jump": ROOT / "configs" / "compositional-confirmatory-existing.json",
    "known_control": ROOT / "configs" / "compositional-confirmatory-existing-control.json",
    "heldout_jump": ROOT / "configs" / "compositional-confirmatory-heldout.json",
    "heldout_control": ROOT / "configs" / "compositional-confirmatory-heldout-control.json",
}

SELF_PLAN_SCHEMA: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "generic_self_composition_v1",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["plans"],
            "properties": {
                "plans": {
                    "type": "array",
                    "minItems": 16,
                    "maxItems": 16,
                    "items": {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 4,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["operator", "arguments"],
                            "properties": {
                                "operator": {
                                    "type": "string",
                                    "enum": [
                                        "ADD_NODE",
                                        "REMOVE_NODE",
                                        "ADD_EDGE",
                                        "REMOVE_EDGE",
                                        "REVERSE_EDGE",
                                        "CHANGE_NODE_TYPE",
                                        "CHANGE_EDGE_TYPE",
                                        "CHANGE_OBSERVABILITY",
                                        "CHANGE_ARITY",
                                        "BIND_ARGUMENT",
                                        "UNBIND_ARGUMENT",
                                        "ADD_FUNCTION",
                                        "REMOVE_FUNCTION",
                                        "ADD_EQUATION",
                                        "REMOVE_EQUATION",
                                        "COMPOSE_FUNCTIONS",
                                        "DECOMPOSE_FUNCTION",
                                        "ADD_TEMPORAL_INDEX",
                                        "REMOVE_TEMPORAL_INDEX",
                                        "ADD_DEPENDENCY",
                                        "REMOVE_DEPENDENCY",
                                        "ADD_CONSTRAINT",
                                        "REMOVE_CONSTRAINT",
                                        "MERGE_NODES",
                                        "SPLIT_NODE",
                                        "REIFY_EDGE_AS_NODE",
                                        "REIFY_NODE_AS_EDGE",
                                        "SUBGRAPH_COPY",
                                    ],
                                },
                                "arguments": {
                                    "type": "object",
                                    "additionalProperties": {"type": "string"},
                                },
                            },
                        },
                    },
                }
            },
        },
    },
}

DEEPSEEK_BASE = {
    "model": "deepseek-v4-flash-vision-exp",
    "revision": "86f746b36186f0e567729a5c06a8c918caba82a9",
    "quantization": "fp8-weights+nvfp4-kv-cache",
    "engine": "patched-vllm-openai",
    "engine_version": "0.25.2.dev0+g752a3a504.d20260714",
    "context_limit": 1_048_576,
    "concurrency": 4,
    "transport_retries": 2,
}

PHI8_BASE = {
    "model": "microsoft/phi-4",
    "revision": "2db69c1c3e91a05d2c64a3185acfbaf36f744e25",
    "quantization": "bitsandbytes-8bit-runtime",
    "engine": "transformers-openai-compat-frozen-v1",
    "engine_version": "transformers-4.56.1+bitsandbytes-0.47.0",
    "context_limit": 4096,
    "concurrency": 1,
    "transport_retries": 2,
}


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _decorate(config: dict[str, Any], source: Path, treatment: str, shard: str) -> None:
    config["extension_experiment_id"] = f"NMI-EXT-V1::{treatment}::{shard}"
    config["treatment_id"] = treatment
    config["historical_source_config"] = str(source.relative_to(ROOT))
    config["historical_source_config_sha256"] = _sha(source)


def _write(treatment: str, shard: str, source: Path, config: dict[str, Any]) -> Path:
    _decorate(config, source, treatment, shard)
    path = OUT / treatment / f"{shard}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical(config))
    return path


def _aj_config(source: Path, treatment: str) -> dict[str, Any]:
    config = deepcopy(_load(source))
    if treatment.startswith("deepseek_"):
        config.update(DEEPSEEK_BASE)
        config["reasoning_effort"] = "none" if treatment == "deepseek_matched" else "max"
        config["generation"]["max_tokens"] = 700 if treatment == "deepseek_matched" else 4096
    elif treatment == "phi8_precision":
        config.update(PHI8_BASE)
    else:
        raise ValueError(treatment)
    return config


def _cj_config(source: Path, treatment: str) -> dict[str, Any]:
    historical = _load(source)
    config = deepcopy(historical)
    config["conditions"] = ["C_SELF_LLM_COMPOSITION"]
    config["validator_repair_attempts"] = 0
    if treatment.startswith("deepseek_"):
        config.update(DEEPSEEK_BASE)
        config["reasoning_effort"] = "none" if treatment == "deepseek_matched" else "max"
        config["generation"]["max_tokens"] = 700 if treatment == "deepseek_matched" else 4096
        if treatment == "deepseek_repair":
            config["validator_repair_attempts"] = 1
        if treatment == "deepseek_constrained":
            config["response_format"] = SELF_PLAN_SCHEMA
    elif treatment == "phi_budget":
        config["generation"]["max_tokens"] = 2048
        config["transport_retries"] = 2
    elif treatment == "phi_constrained":
        config["response_format"] = SELF_PLAN_SCHEMA
        config["transport_retries"] = 2
    elif treatment == "phi_repair":
        config["validator_repair_attempts"] = 1
        config["transport_retries"] = 2
    elif treatment == "phi8_precision":
        config.update(PHI8_BASE)
    else:
        raise ValueError(treatment)
    if treatment == "phi_budget":
        scientific_fields = (
            "candidate_slots",
            "context_limit",
            "docker_image",
            "docker_image_digest",
            "engine",
            "engine_version",
            "gate_thresholds",
            "max_depth",
            "model",
            "primitive_operation_budget",
            "prompt_template",
            "quantization",
            "revision",
            "search_breadth",
            "self_plans_per_slot",
            "decoding_seed_base",
            "search_seed_base",
            "families",
            "world_seeds",
            "no_jump",
            "phase",
        )
        assert all(config[field] == historical[field] for field in scientific_fields)
        assert config["generation"] == {
            **historical["generation"],
            "max_tokens": 2048,
        }
    return config


def main() -> None:
    generated: list[Path] = []
    for treatment in ("deepseek_matched", "deepseek_native", "phi8_precision"):
        for shard, source in AJ_SHARDS.items():
            generated.append(_write(treatment, shard, source, _aj_config(source, treatment)))
    for treatment in (
        "deepseek_matched",
        "deepseek_native",
        "deepseek_repair",
        "deepseek_constrained",
        "phi_budget",
        "phi_constrained",
        "phi_repair",
        "phi8_precision",
    ):
        for shard, source in CJ_SHARDS.items():
            generated.append(_write(treatment, shard, source, _cj_config(source, treatment)))
    manifest = {
        "schema_version": "nmi-extension-config-manifest-v1",
        "generator": str(Path(__file__).relative_to(ROOT)),
        "generator_sha256": _sha(Path(__file__)),
        "configs": {
            str(path.relative_to(ROOT)): _sha(path) for path in sorted(generated)
        },
    }
    manifest_path = OUT / "config_manifest.json"
    manifest_path.write_bytes(_canonical(manifest))
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
