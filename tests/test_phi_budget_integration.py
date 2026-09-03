import json
from pathlib import Path

import pytest

from abductive_jump.phi_budget_integration import _require_only_budget_changed


def historical_config() -> dict[str, object]:
    return {
        "model": "microsoft/phi-4",
        "revision": "revision",
        "quantization": "bitsandbytes-4bit",
        "engine": "vllm-openai",
        "engine_version": "0.10.2",
        "context_limit": 4096,
        "prompt_template": "template",
        "families": ["family"],
        "world_seeds": [1],
        "gate_thresholds": {"j": 1},
        "candidate_slots": 3,
        "max_depth": 4,
        "search_breadth": 48,
        "self_plans_per_slot": 16,
        "primitive_operation_budget": 192,
        "decoding_seed_base": 1,
        "search_seed_base": 2,
        "no_jump": False,
        "generation": {"max_tokens": 700, "temperature": 0.2, "top_p": 0.95},
    }


def test_phi_budget_changes_only_completion_cap(tmp_path: Path) -> None:
    historical = historical_config()
    config = {
        **historical,
        "historical_source_config": "historical.json",
        "generation": {**historical["generation"], "max_tokens": 2048},
        "validator_repair_attempts": 0,
    }
    (tmp_path / "historical.json").write_text(json.dumps(historical))
    _require_only_budget_changed(tmp_path, config)


def test_phi_budget_rejects_an_extra_scientific_change(tmp_path: Path) -> None:
    historical = historical_config()
    config = {
        **historical,
        "historical_source_config": "historical.json",
        "candidate_slots": 4,
        "generation": {**historical["generation"], "max_tokens": 2048},
        "validator_repair_attempts": 0,
    }
    (tmp_path / "historical.json").write_text(json.dumps(historical))
    with pytest.raises(ValueError, match="candidate_slots"):
        _require_only_budget_changed(tmp_path, config)
