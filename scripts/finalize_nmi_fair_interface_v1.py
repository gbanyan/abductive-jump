#!/usr/bin/env python3
"""Validate and replay the frozen fair-interface condition without model calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from abductive_jump.compositional_experiment import _fixed_candidates, _parse_self_plans, _world
from abductive_jump.fair_interface import deliberation_prompt, response_format, serialization_prompt
from abductive_jump.fair_interface_experiment import _seeds, evaluate_selected_science

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_messages(prompt: Any) -> tuple[str, str]:
    messages = [
        {"role": "system", "content": prompt.system},
        {"role": "user", "content": prompt.user},
    ]
    raw = json.dumps(messages, sort_keys=True, separators=(",", ":"))
    return raw, hashlib.sha256(raw.encode()).hexdigest()


def compare(saved: dict[str, Any], expected: dict[str, Any], prefix: str) -> list[str]:
    mismatches = []
    for key, value in expected.items():
        stored = saved.get(key)
        if isinstance(value, float):
            if stored is None or abs(float(stored) - value) > 1e-10:
                mismatches.append(f"{prefix}:{key}")
        elif stored != value:
            mismatches.append(f"{prefix}:{key}")
    return mismatches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        default=ROOT / "experiments" / "nmi_fair_interface_v1",
    )
    args = parser.parse_args()
    base = args.experiment_dir
    config_path = base / "configs" / "deepseek_fair_cself.json"
    protocol_path = base / "protocol.json"
    run_dir = base / "results" / "deepseek_fair_cself"
    config = json.loads(config_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    if protocol["status"] != "frozen_before_inference":
        raise ValueError("protocol is not frozen")
    if digest(config_path) != protocol["config_sha256"]:
        raise ValueError("config hash differs from frozen protocol")
    for relative, expected_hash in protocol["code_sha256"].items():
        if digest(ROOT / relative) != expected_hash:
            raise ValueError(f"code hash differs from frozen protocol: {relative}")

    calls = [json.loads(line) for line in (run_dir / "llm_calls.jsonl").read_text().splitlines()]
    candidates = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    worlds = pq.read_table(run_dir / "world_results.parquet").to_pylist()
    traces = pq.read_table(run_dir / "llm_self_plans.parquet").to_pylist()
    expected_worlds = len(config["families"]) * len(config["world_seeds"])
    expected_candidates = expected_worlds * int(config["candidate_slots"])
    expected_plans = expected_candidates * int(config["self_plans_per_slot"])
    if (len(worlds), len(candidates), len(traces), len(calls)) != (
        expected_worlds,
        expected_candidates,
        expected_plans,
        expected_candidates * 2,
    ):
        raise ValueError("output cardinality differs from frozen protocol")

    by_call: dict[tuple[str, int], dict[str, Any]] = {}
    for row in calls:
        key = (str(row["world_id"]), int(row["decoding_seed"]))
        if key in by_call:
            raise ValueError(f"duplicate call: {key}")
        by_call[key] = row

    saved_candidates = {
        (str(row["family"]), int(row["world_seed"]), int(row["slot"])): row for row in candidates
    }
    replayed = []
    mismatches: list[str] = []
    expected_world_keys = set()
    for family in config["families"]:
        for seed in config["world_seeds"]:
            world = _world(config, str(family), int(seed))
            expected_world_keys.add((str(family), int(seed), world.world_id))
            for slot in range(int(config["candidate_slots"])):
                first_seed, final_seed = _seeds(config, str(family), int(seed), slot)
                first = by_call[(world.world_id, first_seed)]
                final = by_call[(world.world_id, final_seed)]
                deliberation = str(first.get("reasoning_output") or first.get("full_output") or "")
                first_prompt = deliberation_prompt(world)
                final_prompt = serialization_prompt(world, deliberation)
                for call, prompt, stage, generation in (
                    (first, first_prompt, "deliberation", config["deliberation_generation"]),
                    (final, final_prompt, "serialization", config["serialization_generation"]),
                ):
                    prompt_json, prompt_hash = canonical_messages(prompt)
                    request = json.loads(call["request_json"])
                    expected_request_format = (
                        response_format() if stage == "serialization" else None
                    )
                    prefix = f"{world.world_id}:{slot}:{stage}"
                    mismatches.extend(
                        compare(
                            call,
                            {
                                "world_id": world.world_id,
                                "world_seed": int(seed),
                                "prompt_template_version": prompt.template_version,
                                "prompt_hash": prompt_hash,
                                "full_prompt_json": prompt_json,
                                "model": config["model"],
                                "revision": config["revision"],
                                "engine": config["engine"],
                            },
                            prefix,
                        )
                    )
                    mismatches.extend(
                        compare(
                            request,
                            {
                                "reasoning_effort": generation["reasoning_effort"],
                                "max_tokens": generation["max_tokens"],
                                "response_format": expected_request_format,
                            },
                            prefix + ":request",
                        )
                    )
                evaluated, _ = _parse_self_plans(
                    world,
                    str(final["full_output"]),
                    int(config["search_seed_base"]) + int(seed) * 101 + slot * 1000,
                    required_plans=int(config["self_plans_per_slot"]),
                )
                selected = max(
                    evaluated,
                    key=lambda item: (item.score, item.candidate.representation.structural_hash),
                    default=_fixed_candidates(world, 1)[0],
                )
                expected = evaluate_selected_science(
                    world,
                    selected,
                    gate_thresholds=dict(config["gate_thresholds"]),
                    proposal_executable=bool(evaluated),
                )
                saved = saved_candidates[(str(family), int(seed), slot)]
                fields = (
                    "proposal_executable",
                    "representation_hash",
                    "ancestry_depth",
                    "mutation_ancestry",
                    "structural_signature",
                    "observational_loss",
                    "search_prediction_separation",
                    "selected_intervention_id",
                    "j0",
                    "j1",
                    "j2",
                    "j3",
                    "j4",
                    "j5",
                    "validated_jump",
                    "candidate_obs_loss",
                    "oracle_cf_loss",
                    "candidate_cf_loss",
                    "oracle_falsification_loss",
                    "candidate_falsification_loss",
                )
                local = compare(
                    saved,
                    {field: expected[field] for field in fields},
                    f"{world.world_id}:{slot}:science",
                )
                mismatches.extend(local)
                replayed.append(
                    {
                        "family": family,
                        "world_seed": int(seed),
                        "world_id": world.world_id,
                        "slot": slot,
                        "replay_verified": not local,
                    }
                )

    actual_world_keys = {
        (str(row["family"]), int(row["world_seed"]), str(row["world_id"])) for row in worlds
    }
    if actual_world_keys != expected_world_keys:
        mismatches.append("world_panel")
    pq.write_table(
        pa.Table.from_pylist(replayed), run_dir / "replayed_candidates.parquet", compression="zstd"
    )
    report = {
        "status": "complete_verified" if not mismatches else "mismatch",
        "model_calls_made": 0,
        "candidate_rows": len(candidates),
        "replay_verified": sum(bool(row["replay_verified"]) for row in replayed),
        "replay_mismatches": len(mismatches),
        "mismatch_examples": mismatches[:20],
        "source_sha256": {
            name: digest(run_dir / name)
            for name in (
                "llm_calls.jsonl",
                "candidate_results.parquet",
                "world_results.parquet",
                "llm_self_plans.parquet",
                "summary.json",
            )
        },
    }
    (run_dir / "replay_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (run_dir / "validation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
