import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from abductive_jump.compositional_experiment import _world
from abductive_jump.compositional_worlds import HELD_OUT_FAMILY
from abductive_jump.conditions import Condition, ProposalSource, build_prompt
from abductive_jump.executable import program_expression
from abductive_jump.minimal_sensitivity_replay import (
    compare_saved,
    normalized,
    p2_decoding_seed,
    replay_p2,
    require_exact_keys,
    require_exact_panel,
)
from abductive_jump.supplied_representation_experiment import evaluate_model_output
from abductive_jump.worlds import generate_world


def test_normalized_equates_arrow_lists_and_dataclass_tuples() -> None:
    assert normalized(("a", ("b",))) == normalized(["a", ["b"]])


def test_compare_saved_uses_float_tolerance() -> None:
    assert compare_saved("x", {"loss": 0.1 + 1e-12}, {"loss": 0.1}) == []
    assert compare_saved("x", {"loss": 0.2}, {"loss": 0.1}) == ["x:loss"]


def test_compare_saved_reports_missing_fields() -> None:
    assert compare_saved("x", {}, {"j1": True}) == ["x:missing:j1"]


def test_require_exact_keys_rejects_duplicates_and_panel_drift() -> None:
    expected = {("a", 1), ("b", 2)}
    require_exact_keys([("a", 1), ("b", 2)], expected, "toy")
    with pytest.raises(ValueError, match="duplicate"):
        require_exact_keys([("a", 1), ("a", 1)], expected, "toy")
    with pytest.raises(ValueError, match="panel mismatch"):
        require_exact_keys([("a", 1), ("c", 3)], expected, "toy")


def test_require_exact_panel_supports_the_registered_heldout_family(tmp_path: Path) -> None:
    config = {
        "families": [HELD_OUT_FAMILY],
        "world_seeds": [42000],
        "candidate_slots": 1,
        "decoding_seed_base": 320000001,
        "validator_repair_attempts": 0,
        "no_jump": False,
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    world = _world(config, HELD_OUT_FAMILY, 42000)
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "family": HELD_OUT_FAMILY,
                    "world_seed": 42000,
                    "world_id": world.world_id,
                }
            ]
        ),
        run_dir / "world_results.parquet",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "family": HELD_OUT_FAMILY,
                    "world_seed": 42000,
                    "world_id": world.world_id,
                    "slot": 0,
                }
            ]
        ),
        run_dir / "candidate_results.parquet",
    )
    seed = (
        config["decoding_seed_base"]
        + list(Condition).index(Condition.C_SELF_LLM_COMPOSITION) * 10_000_000
        + 8 * 100_000
        + 42000 * 100
    )
    calls = [
        {
            "condition": Condition.C_SELF_LLM_COMPOSITION.value,
            "proposal_source": source.value,
            "world_id": world.world_id,
            "decoding_seed": seed + offset,
        }
        for source, offset in (
            (ProposalSource.LLM_COMPOSITION, 0),
            (ProposalSource.COMPOSITION_SEARCH, 1),
        )
    ]
    (run_dir / "llm_calls.jsonl").write_text("".join(json.dumps(row) + "\n" for row in calls))
    require_exact_panel(config_path, run_dir, p2=False)


def test_p2_replay_reconstructs_a_saved_candidate(tmp_path: Path) -> None:
    source_config = Path("experiments/nmi_minimal_sensitivity_v1/configs/deepseek_p2.json")
    config = json.loads(source_config.read_text())
    config["families"] = ["unification"]
    config["world_seeds"] = [30014]
    config["candidate_slots"] = 1
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    world = generate_world("unification", 30014, no_jump=False)
    output = json.dumps(
        {
            "representation": "USE_SUPPLIED_REPRESENTATION",
            "expression": program_expression(world.truth.program).tree,
            "explanation": "deterministic replay fixture",
            "selected_intervention_ids": [world.interventions[0].case_id],
        }
    )
    result = evaluate_model_output(world, output)
    candidate = {
        "condition": "DEEPSEEK_P2_CAUSAL_POSITIVE_CONTROL",
        "proposal_source": ProposalSource.P2_ORACLE.value,
        "family": "unification",
        "world_id": world.world_id,
        "world_seed": 30014,
        "slot": 0,
        "parse_valid": True,
        "executable": True,
        "validated_jump": all(result[f"j{index}"] for index in range(6)),
        **result,
    }
    pq.write_table(pa.Table.from_pylist([candidate]), run_dir / "candidate_results.parquet")

    prompt = build_prompt(
        world.public(),
        Condition.C5_ORACLE_REPRESENTATION,
        ProposalSource.P2_ORACLE,
        supplied_representation=world.truth.representation,
    )
    messages = [
        {"role": "system", "content": prompt.system},
        {"role": "user", "content": prompt.user},
    ]
    prompt_json = json.dumps(messages, sort_keys=True, separators=(",", ":"))
    call = {
        "condition": Condition.C5_ORACLE_REPRESENTATION.value,
        "proposal_source": ProposalSource.P2_ORACLE.value,
        "world_id": world.world_id,
        "world_seed": 30014,
        "decoding_seed": p2_decoding_seed(config, "unification", 30014, 0),
        "prompt_template_version": prompt.template_version,
        "prompt_hash": hashlib.sha256(prompt_json.encode()).hexdigest(),
        "full_prompt_json": prompt_json,
        "representation_hash": world.truth.representation.structural_hash,
        "full_output": output,
    }
    (run_dir / "llm_calls.jsonl").write_text(json.dumps(call) + "\n")
    report = replay_p2(config_path, run_dir)
    assert report["candidate_rows"] == report["verified_rows"] == 1
    assert report["mismatches"] == 0
