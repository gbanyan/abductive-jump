"""Regression checks for the documented proposal and schema-metadata boundaries."""
import importlib.util
import json
from dataclasses import replace
from pathlib import Path

import pytest

from abductive_jump.conditions import Condition, ProposalSource, build_prompt
from abductive_jump.worlds import generate_world

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aij_contracts", ROOT / "scripts/audit_aij_contracts.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_b0_and_b1_have_different_output_contracts():
    world = generate_world("latent_common_cause", 10000)
    schemas = []
    for condition in (Condition.B0_DIRECT_LLM, Condition.B1_SAMPLE_MATCHED):
        prompt = build_prompt(world.public(), condition, ProposalSource.P0_LLM)
        schemas.append(json.loads(next(s.removeprefix("Output schema: ")
                                       for s in prompt.user.splitlines() if s.startswith("Output schema: "))))
    assert "representation" in schemas[0] and "mutation_plan" not in schemas[0]
    assert "mutation_plan" in schemas[1] and "representation" not in schemas[1]


def test_hidden_only_name_is_detected():
    world = generate_world("latent_common_cause", 10000)
    first = replace(world.falsification[0], inputs=world.falsification[0].inputs + (("hidden_only_name", 2.0),))
    changed = replace(world, falsification=(first, *world.falsification[1:]))
    with pytest.raises(AssertionError):
        audit.public_name_check(changed)


def test_private_input_is_not_added_to_allowlist():
    world = generate_world("latent_common_cause", 10000)
    first = replace(world.falsification[0], inputs=world.falsification[0].inputs + (("_private", 2.0),))
    changed = replace(world, falsification=(first, *world.falsification[1:]))
    assert audit.public_name_check(changed) == audit.public_name_check(world)


def test_all_archived_world_name_schemas():
    report = audit.audit_names()
    assert [row["worlds"] for row in report] == [600, 800]
    assert all(row["hidden_only_allowlist_names"] == 0 for row in report)
    assert all(not row["worlds_with_allowed_names_only_in_public_actions"] for row in report)


def test_all_b1_raw_contracts_and_final_hashes():
    if not (ROOT / "artifacts/confirmatory/primary-jump/llm_calls.jsonl").exists():
        pytest.skip("Raw evidence-release ledgers not installed")
    report = audit.audit_b1()
    assert [row["candidate_rows"] for row in report] == [1200, 600]
    for row in report:
        assert row["counts"]["mutation_plan_prompt_contract"] == row["candidate_rows"]
        assert row["counts"]["final_representation_hash_matches"] == row["candidate_rows"]
