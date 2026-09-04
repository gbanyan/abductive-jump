"""Run and replay one fixed-panel fair-interface DeepSeek sensitivity condition."""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .composition_search import SearchEvaluation
from .compositional_experiment import (
    _fit_for_condition,
    _fixed_candidates,
    _parse_self_plans,
    _prediction_table,
    _world,
)
from .compositional_worlds import HELD_OUT_FAMILY
from .conditions import Condition
from .executable import evaluate_executable, freeze_theory, parse_theory
from .fair_interface import (
    deliberation_prompt,
    operator_vocabulary,
    response_format,
    serialization_prompt,
)
from .llm import ModelManifest, OpenAICompatibleClient
from .primary_experiment import _thresholds
from .worlds import FAMILIES


def _arrow_table(rows: list[dict[str, Any]]) -> pa.Table:
    columns = sorted({key for row in rows for key in row})
    return pa.Table.from_pylist([{key: row.get(key) for key in columns} for row in rows])


def _manifest(config: dict[str, Any], stage: str) -> ModelManifest:
    generation = config[f"{stage}_generation"]
    return ModelManifest(
        config["model"],
        config["revision"],
        config["quantization"],
        config["engine"],
        config["engine_version"],
        int(config["context_limit"]),
        float(generation["temperature"]),
        float(generation["top_p"]),
        int(generation["max_tokens"]),
        str(generation["reasoning_effort"]),
        response_format() if stage == "serialization" else None,
        int(config.get("transport_retries", 0)),
    )


def _seeds(config: dict[str, Any], family: str, world_seed: int, slot: int) -> tuple[int, int]:
    family_index = [*FAMILIES, HELD_OUT_FAMILY].index(family)
    first = int(config["decoding_seed_base"]) + family_index * 100_000 + world_seed * 100 + slot * 2
    return first, first + 1


def evaluate_selected_science(
    world: Any,
    candidate: SearchEvaluation,
    *,
    gate_thresholds: dict[str, Any],
    proposal_executable: bool,
) -> dict[str, Any]:
    representation = candidate.candidate.representation
    expression, obs_loss, signature = _fit_for_condition(
        world, Condition.C_SELF_LLM_COMPOSITION, representation
    )
    table = _prediction_table(world, expression)
    exact_choice = max(
        table, key=lambda row: (float(row["absolute_separation"]), str(row["case_id"]))
    )
    payload = {
        "representation": representation.canonical_dict(),
        "expression": expression.tree,
        "explanation": "",
        "selected_intervention_ids": [exact_choice["case_id"]],
    }
    theory = parse_theory(
        payload,
        {public_name: internal for internal, public_name in world.variable_names},
    )
    result = evaluate_executable(
        world,
        theory,
        freeze_theory(world, theory),
        _thresholds({"gate_thresholds": gate_thresholds}),
    )
    row: dict[str, Any] = {
        "condition": "DEEPSEEK_FAIR_INTERFACE_CSELF",
        "family": world.family,
        "world_id": world.world_id,
        "world_seed": world.seed,
        "proposal_executable": proposal_executable,
        "representation_hash": representation.structural_hash,
        "ancestry_depth": candidate.candidate.depth,
        "mutation_ancestry": list(candidate.candidate.operators),
        "structural_signature": signature,
        "observational_loss": obs_loss,
        "search_prediction_separation": candidate.max_prediction_separation,
        "selected_intervention_id": exact_choice["case_id"],
    }
    row.update(asdict(result))
    row["validated_jump"] = bool(result.validated_jump and proposal_executable)
    return row


def _run_world(
    config: dict[str, Any], family: str, world_seed: int, base_url: str, log_path: Path
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    world = _world(config, family, world_seed)
    deliberation_client = OpenAICompatibleClient(
        base_url, _manifest(config, "deliberation"), log_path
    )
    serialization_client = OpenAICompatibleClient(
        base_url, _manifest(config, "serialization"), log_path
    )
    candidates: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for slot in range(int(config["candidate_slots"])):
        deliberation_seed, serialization_seed = _seeds(config, family, world_seed, slot)
        first_output, first_call = deliberation_client.generate(
            deliberation_prompt(world),
            world_id=world.world_id,
            world_seed=world_seed,
            decoding_seed=deliberation_seed,
            candidate_parent=world.incumbent.structural_hash,
        )
        deliberation = first_call.reasoning_output or first_output
        final_output, final_call = serialization_client.generate(
            serialization_prompt(world, deliberation),
            world_id=world.world_id,
            world_seed=world_seed,
            decoding_seed=serialization_seed,
            candidate_parent=world.incumbent.structural_hash,
        )
        search_seed = int(config["search_seed_base"]) + world_seed * 101 + slot * 1000
        evaluated, parsed = _parse_self_plans(
            world,
            final_output,
            search_seed,
            required_plans=int(config["self_plans_per_slot"]),
        )
        strict_json = False
        try:
            strict_json = isinstance(json.loads(final_output), dict)
        except json.JSONDecodeError:
            pass
        traces.extend(
            {
                "world_id": world.world_id,
                "family": family,
                "world_seed": world_seed,
                "slot": slot,
                "strict_whole_response_json": strict_json,
                "deliberation_returned": bool(deliberation),
                "serialization_returned": bool(final_output.strip()),
                **trace,
            }
            for trace in parsed
        )
        selected = max(
            evaluated,
            key=lambda item: (item.score, item.candidate.representation.structural_hash),
            default=_fixed_candidates(world, 1)[0],
        )
        row = evaluate_selected_science(
            world,
            selected,
            gate_thresholds=dict(config["gate_thresholds"]),
            proposal_executable=bool(evaluated),
        )
        row.update(
            {
                "slot": slot,
                "deliberation_tokens": first_call.completion_tokens,
                "deliberation_reasoning_tokens": int(first_call.reasoning_tokens or 0),
                "deliberation_answer_tokens": int(
                    first_call.answer_tokens or first_call.completion_tokens
                ),
                "serialization_tokens": final_call.completion_tokens,
                "serialization_reasoning_tokens": int(final_call.reasoning_tokens or 0),
                "serialization_answer_tokens": int(
                    final_call.answer_tokens or final_call.completion_tokens
                ),
            }
        )
        candidates.append(row)
    world_row = {
        "condition": "DEEPSEEK_FAIR_INTERFACE_CSELF",
        "family": family,
        "world_id": world.world_id,
        "world_seed": world_seed,
        "condition_success": any(bool(row["validated_jump"]) for row in candidates),
        "accepted_candidates": sum(bool(row["validated_jump"]) for row in candidates),
        "executable_slots": sum(bool(row["proposal_executable"]) for row in candidates),
        "llm_calls": 2 * int(config["candidate_slots"]),
    }
    return candidates, world_row, traces


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    operator_vocabulary()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        (config, family, int(seed), base_url, output_dir / "llm_calls.jsonl")
        for family in config["families"]
        for seed in config["world_seeds"]
    ]
    candidates: list[dict[str, Any]] = []
    worlds: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=int(config["concurrency"])) as executor:
        futures = [executor.submit(_run_world, *job) for job in jobs]
        for future in as_completed(futures):
            candidate_rows, world_row, trace_rows = future.result()
            candidates.extend(candidate_rows)
            worlds.append(world_row)
            traces.extend(trace_rows)
    candidates.sort(key=lambda row: (row["family"], row["world_seed"], row["slot"]))
    worlds.sort(key=lambda row: (row["family"], row["world_seed"]))
    traces.sort(key=lambda row: (row["family"], row["world_seed"], row["slot"], row["plan_index"]))
    pq.write_table(
        _arrow_table(candidates), output_dir / "candidate_results.parquet", compression="zstd"
    )
    pq.write_table(_arrow_table(worlds), output_dir / "world_results.parquet", compression="zstd")
    pq.write_table(_arrow_table(traces), output_dir / "llm_self_plans.parquet", compression="zstd")
    successes = sum(bool(row["condition_success"]) for row in worlds)
    summary = {
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "worlds": len(worlds),
        "candidate_slots": len(candidates),
        "plan_opportunities": len(traces),
        "llm_calls": 2 * len(candidates),
        "successes": successes,
        "jsr": successes / len(worlds),
        "executable_plan_opportunities": sum(bool(row["executable"]) for row in traces),
        "executable_slots": sum(bool(row["proposal_executable"]) for row in candidates),
        "validated_candidates": sum(bool(row["validated_jump"]) for row in candidates),
        "model_manifests": {
            "deliberation": asdict(_manifest(config, "deliberation")),
            "serialization": asdict(_manifest(config, "serialization")),
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="http://192.168.30.16:8888/v1")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output_dir, args.base_url), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
