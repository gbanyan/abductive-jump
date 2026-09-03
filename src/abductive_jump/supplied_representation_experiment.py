"""Causal positive control for using a supplied oracle representation."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .conditions import Condition, ProposalSource, build_prompt
from .executable import evaluate_executable, freeze_theory, parse_theory
from .external_reasoning_calibration import _arrow_table, _manifest
from .gates import GateThresholds
from .llm import OpenAICompatibleClient, extract_json_object
from .primary_experiment import _thresholds
from .worlds import FAMILIES, generate_world


def evaluate_model_output(
    world: Any, output: str, thresholds: GateThresholds | None = None
) -> dict[str, Any]:
    """Evaluate model-authored law and intervention while fixing only representation."""
    payload = extract_json_object(output)
    payload["representation"] = world.truth.representation.canonical_dict()
    theory = parse_theory(
        payload,
        {public_name: internal for internal, public_name in world.variable_names},
    )
    result = evaluate_executable(world, theory, freeze_theory(world, theory), thresholds)
    return asdict(result)


def _run_slot(
    *,
    config: dict[str, Any],
    family: str,
    world_seed: int,
    slot: int,
    base_url: str,
    log_path: Path,
) -> dict[str, Any]:
    world = generate_world(family, world_seed, no_jump=False)
    prompt = build_prompt(
        world.public(),
        Condition.C5_ORACLE_REPRESENTATION,
        ProposalSource.P2_ORACLE,
        supplied_representation=world.truth.representation,
    )
    client = OpenAICompatibleClient(base_url, _manifest(config), log_path)
    decoding_seed = (
        int(config["decoding_seed_base"])
        + list(Condition).index(Condition.C5_ORACLE_REPRESENTATION) * 10_000_000
        + FAMILIES.index(family) * 100_000
        + world_seed * 100
        + slot
    )
    output, call = client.generate(
        prompt,
        world_id=world.world_id,
        world_seed=world_seed,
        decoding_seed=decoding_seed,
        candidate_parent=world.incumbent.structural_hash,
        representation_hash=world.truth.representation.structural_hash,
    )
    row: dict[str, Any] = {
        "condition": "DEEPSEEK_P2_CAUSAL_POSITIVE_CONTROL",
        "proposal_source": ProposalSource.P2_ORACLE.value,
        "family": family,
        "world_id": world.world_id,
        "world_seed": world_seed,
        "slot": slot,
        "response_returned": bool(output.strip()),
        "parse_valid": False,
        "executable": False,
        "validated_jump": False,
        "prompt_tokens": call.prompt_tokens,
        "reasoning_tokens": int(call.reasoning_tokens or 0),
        "answer_tokens": int(call.answer_tokens or call.completion_tokens),
        "completion_tokens": call.completion_tokens,
        "total_tokens": int(call.total_tokens or call.prompt_tokens + call.completion_tokens),
        "latency_seconds": call.latency_seconds,
        "transport_attempt_count": call.attempt_count,
        "finish_reason": call.finish_reason,
        "representation_hash": world.truth.representation.structural_hash,
    }
    try:
        result = evaluate_model_output(world, output, _thresholds(config))
        row.update(result)
        row["parse_valid"] = True
        row["executable"] = True
        row["validated_jump"] = all(bool(row[f"j{index}"]) for index in range(6))
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        row["error_type"] = type(exc).__name__
        row["error"] = str(exc)
    return row


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    if config.get("conditions") != ["C5_ORACLE_REPRESENTATION"]:
        raise ValueError("positive-control runner accepts only C5_ORACLE_REPRESENTATION")
    if bool(config.get("no_jump", False)):
        raise ValueError("positive control is defined only for jump worlds")
    slots = int(config["candidate_slots"])
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        {
            "config": config,
            "family": family,
            "world_seed": int(seed),
            "slot": slot,
            "base_url": base_url,
            "log_path": output_dir / "llm_calls.jsonl",
        }
        for family in config["families"]
        for seed in config["world_seeds"]
        for slot in range(slots)
    ]
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=int(config.get("concurrency", 1))) as executor:
        futures = [executor.submit(_run_slot, **job) for job in jobs]
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: (row["family"], row["world_seed"], row["slot"]))

    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["world_id"])].append(row)
    worlds = [
        {
            "condition": "DEEPSEEK_P2_CAUSAL_POSITIVE_CONTROL",
            "world_id": world_id,
            "family": candidates[0]["family"],
            "world_seed": candidates[0]["world_seed"],
            "condition_success": any(bool(row["validated_jump"]) for row in candidates),
            "valid_candidates": sum(bool(row["parse_valid"]) for row in candidates),
            "validated_candidates": sum(bool(row["validated_jump"]) for row in candidates),
            "llm_calls_used": len(candidates),
            "interventions_committed": sum(bool(row["executable"]) for row in candidates),
        }
        for world_id, candidates in sorted(grouped.items())
    ]
    summary = {
        "model_manifest": asdict(_manifest(config)),
        "design": {
            "representation": "oracle representation supplied and fixed",
            "model_authored": ["expression", "explanation", "selected_intervention_ids"],
            "deterministic_overwrites": ["representation only"],
            "outcomes_visible_before_commitment": False,
            "calls_per_world": slots,
        },
        "candidate_rows": len(rows),
        "worlds": len(worlds),
        "jsr": sum(bool(row["condition_success"]) for row in worlds) / len(worlds),
    }
    pq.write_table(_arrow_table(rows), output_dir / "candidate_results.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pylist(worlds), output_dir / "world_results.parquet", compression="zstd")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output_dir, args.base_url), indent=2))


if __name__ == "__main__":
    main()
