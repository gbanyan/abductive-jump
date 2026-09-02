#!/usr/bin/env python3
"""Verify completeness and hash every NMI extension v1 raw result shard."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from abductive_jump.compositional_experiment import _world
from abductive_jump.compositional_worlds import HELD_OUT_FAMILY
from abductive_jump.conditions import Condition, ProposalSource
from abductive_jump.worlds import FAMILIES, generate_world

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "experiments" / "nmi_extension_v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


SOURCE_CONDITIONS = {
    ProposalSource.P0_LLM.value: Condition.B1_SAMPLE_MATCHED.value,
    ProposalSource.P1_EXTERNAL.value: Condition.B4_REPRESENTATION_MUTATION.value,
    ProposalSource.P2_ORACLE.value: Condition.B4_REPRESENTATION_MUTATION.value,
}


def verify_shard(config_path: Path, run_dir: Path) -> dict[str, Any]:
    config_path = config_path.resolve()
    run_dir = run_dir.resolve()
    config = load(config_path)
    factorial = run_dir.name.startswith("factorial_")
    families = len(config["families"])
    seeds = (
        int(config["world_seed_range"]["stop_exclusive"])
        - int(config["world_seed_range"]["start"])
        if factorial
        else len(config["world_seeds"])
    )
    sources = len(config["proposal_sources"]) if factorial else 1
    expected_world_rows = families * seeds * sources
    expected_candidate_rows = expected_world_rows * int(config["candidate_slots"])
    worlds = pq.read_table(run_dir / "world_results.parquet").to_pylist()
    candidates = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    calls = _lines(run_dir / "llm_calls.jsonl")
    require(len(worlds) == expected_world_rows, f"{run_dir}: world rows")
    require(len(candidates) == expected_candidate_rows, f"{run_dir}: candidate rows")
    if factorial:
        require(len(calls) == expected_candidate_rows * 2, f"{run_dir}: calls")
    else:
        phase_one = [
            row
            for row in calls
            if row["proposal_source"] == "LLM_COMPOSITION"
        ]
        phase_two = [
            row
            for row in calls
            if row["proposal_source"] == "COMPOSITION_SEARCH"
        ]
        require(len(phase_two) == expected_candidate_rows, f"{run_dir}: phase-two calls")
        repairs = len(phase_one) - expected_candidate_rows
        require(0 <= repairs <= expected_candidate_rows, f"{run_dir}: repair calls")
        if int(config.get("validator_repair_attempts", 0)) == 0:
            require(repairs == 0, f"{run_dir}: unexpected repair")
        traces = pq.read_table(run_dir / "llm_self_plans.parquet").to_pylist()
        require(
            len(traces) == len(phase_one) * int(config["self_plans_per_slot"]),
            f"{run_dir}: plan traces",
        )
    call_keys = {
        (
            row["condition"],
            row["proposal_source"],
            row["world_id"],
            int(row["decoding_seed"]),
        )
        for row in calls
    }
    require(len(call_keys) == len(calls), f"{run_dir}: duplicate calls")
    expected_seeds = (
        set(range(int(config["world_seed_range"]["start"]), int(config["world_seed_range"]["stop_exclusive"])))
        if factorial
        else {int(seed) for seed in config["world_seeds"]}
    )
    require(
        {int(row["world_seed"]) for row in worlds} == expected_seeds,
        f"{run_dir}: world seed set",
    )

    expected_world_keys = set()
    expected_candidate_keys = set()
    if factorial:
        expected_call_keys = set()
        for source in config["proposal_sources"]:
            condition = SOURCE_CONDITIONS[source]
            for family in config["families"]:
                for seed in expected_seeds:
                    world = generate_world(family, seed, no_jump=bool(config["no_jump"]))
                    expected_world_keys.add((source, condition, family, seed, world.world_id))
                    for slot in range(int(config["candidate_slots"])):
                        expected_candidate_keys.add(
                            (source, condition, family, seed, world.world_id, slot)
                        )
                        decoding_seed = (
                            int(config["decoding_seed_base"])
                            + list(Condition).index(Condition(condition)) * 10_000_000
                            + FAMILIES.index(family) * 100_000
                            + seed * 100
                            + slot * 2
                        )
                        expected_call_keys.add((condition, source, world.world_id, decoding_seed))
                        expected_call_keys.add((condition, source, world.world_id, decoding_seed + 1))
        actual_world_keys = {
            (
                str(row["proposal_source"]),
                str(row["condition"]),
                str(row["family"]),
                int(row["world_seed"]),
                str(row["world_id"]),
            )
            for row in worlds
        }
        actual_candidate_keys = {
            (
                str(row["proposal_source"]),
                str(row["condition"]),
                str(row["family"]),
                int(row["world_seed"]),
                str(row["world_id"]),
                int(row["slot"]),
            )
            for row in candidates
        }
        require(call_keys == expected_call_keys, f"{run_dir}: exact call identities")
    else:
        require(
            config["conditions"] == [Condition.C_SELF_LLM_COMPOSITION.value],
            f"{run_dir}: unexpected condition config",
        )
        for family in config["families"]:
            for seed in expected_seeds:
                world = _world(config, family, seed)
                expected_world_keys.add(
                    (Condition.C_SELF_LLM_COMPOSITION.value, family, seed, world.world_id)
                )
                for slot in range(int(config["candidate_slots"])):
                    expected_candidate_keys.add(
                        (
                            Condition.C_SELF_LLM_COMPOSITION.value,
                            family,
                            seed,
                            world.world_id,
                            slot,
                        )
                    )
        actual_world_keys = {
            (
                str(row["condition"]),
                str(row["family"]),
                int(row["world_seed"]),
                str(row["world_id"]),
            )
            for row in worlds
        }
        actual_candidate_keys = {
            (
                str(row["condition"]),
                str(row["family"]),
                int(row["world_seed"]),
                str(row["world_id"]),
                int(row["slot"]),
            )
            for row in candidates
        }
    require(actual_world_keys == expected_world_keys, f"{run_dir}: exact world identities")
    require(
        actual_candidate_keys == expected_candidate_keys,
        f"{run_dir}: exact candidate identities",
    )
    require(
        all(bool(row["no_jump"]) == bool(config["no_jump"]) for row in worlds + candidates),
        f"{run_dir}: no_jump identity",
    )

    for row in calls:
        require(row["model"] == config["model"], f"{run_dir}: call model")
        require(row["revision"] == config["revision"], f"{run_dir}: call revision")
        require(row["quantization"] == config["quantization"], f"{run_dir}: call quantization")
        require(
            hashlib.sha256(str(row["full_prompt_json"]).encode()).hexdigest()
            == row["prompt_hash"],
            f"{run_dir}: prompt hash",
        )
        request = json.loads(row["request_json"])
        require(request["model"] == config["model"], f"{run_dir}: request model")
        require(
            int(request["max_tokens"]) == int(config["generation"]["max_tokens"]),
            f"{run_dir}: request max_tokens",
        )
        expected_temperature = (
            float(config["sample_temperature"])
            if row["condition"] == Condition.B1_SAMPLE_MATCHED.value
            else float(config["generation"]["temperature"])
        )
        require(float(request["temperature"]) == expected_temperature, f"{run_dir}: temperature")
        require(float(request["top_p"]) == float(config["generation"]["top_p"]), f"{run_dir}: top_p")
        require(int(request["seed"]) == int(row["decoding_seed"]), f"{run_dir}: seed")
        require(request.get("reasoning_effort") == config.get("reasoning_effort"), f"{run_dir}: reasoning")
        require(request.get("response_format") == config.get("response_format"), f"{run_dir}: response format")
        response = json.loads(row["raw_response_json"])
        message = response["choices"][0]["message"]
        require(str(message.get("content") or "") == row["full_output"], f"{run_dir}: answer capture")
        require(
            str(message.get("reasoning") or message.get("reasoning_content") or "")
            == str(row.get("reasoning_output") or ""),
            f"{run_dir}: reasoning capture",
        )

    summary = load(run_dir / "summary.json")
    manifest = summary["model_manifest"]
    for key in (
        "model",
        "revision",
        "quantization",
        "engine",
        "engine_version",
        "context_limit",
        "reasoning_effort",
        "response_format",
        "transport_retries",
    ):
        require(manifest.get(key) == config.get(key), f"{run_dir}: summary manifest {key}")
    require(
        manifest["max_tokens"] == config["generation"]["max_tokens"],
        f"{run_dir}: summary max_tokens",
    )
    if not factorial:
        require(summary["config"] == config, f"{run_dir}: embedded config")
        call_lookup = {
            (
                row["proposal_source"],
                row["world_id"],
                int(row["decoding_seed"]),
            ): row
            for row in calls
        }
        trace_groups: dict[tuple[str, int, str], list[dict[str, Any]]] = {}
        for row in traces:
            trace_groups.setdefault(
                (str(row["world_id"]), int(row["slot"]), str(row["repair_stage"])), []
            ).append(row)
        for candidate in candidates:
            family = str(candidate["family"])
            seed = int(candidate["world_seed"])
            slot = int(candidate["slot"])
            family_index = [*FAMILIES, HELD_OUT_FAMILY].index(family)
            initial_seed = (
                int(config["decoding_seed_base"])
                + list(Condition).index(Condition.C_SELF_LLM_COMPOSITION) * 10_000_000
                + family_index * 100_000
                + seed * 100
                + slot * 2
            )
            world_id = str(candidate["world_id"])
            require(
                (ProposalSource.LLM_COMPOSITION.value, world_id, initial_seed) in call_lookup,
                f"{run_dir}: missing initial C_self call",
            )
            require(
                (ProposalSource.COMPOSITION_SEARCH.value, world_id, initial_seed + 1)
                in call_lookup,
                f"{run_dir}: missing phase-two call",
            )
            initial_traces = trace_groups.get((world_id, slot, "initial"), [])
            repair_traces = trace_groups.get((world_id, slot, "repair"), [])
            require(len(initial_traces) == int(config["self_plans_per_slot"]), f"{run_dir}: initial traces")
            repair_call = (
                ProposalSource.LLM_COMPOSITION.value,
                world_id,
                initial_seed + 50_000_000,
            ) in call_lookup
            require(repair_call == bool(repair_traces), f"{run_dir}: repair call/trace pairing")
            if repair_call:
                require(
                    int(config.get("validator_repair_attempts", 0)) == 1
                    and len(repair_traces) == int(config["self_plans_per_slot"])
                    and not all(bool(row.get("valid")) for row in initial_traces),
                    f"{run_dir}: invalid repair trigger",
                )
            elif int(config.get("validator_repair_attempts", 0)) == 1:
                require(
                    all(bool(row.get("valid")) for row in initial_traces),
                    f"{run_dir}: omitted required repair",
                )
    error_path = run_dir / "llm_calls.jsonl.transport-errors"
    artifacts = {
        str(path.relative_to(ROOT)): sha(path)
        for path in sorted(run_dir.iterdir())
        if path.is_file()
    }
    return {
        "experiment_id": config["extension_experiment_id"],
        "treatment_id": config["treatment_id"],
        "config": str(config_path.relative_to(ROOT)),
        "config_sha256": sha(config_path),
        "run_dir": str(run_dir.relative_to(ROOT)),
        "world_rows": len(worlds),
        "candidate_rows": len(candidates),
        "llm_calls": len(calls),
        "transport_error_records": len(error_path.read_text().splitlines()) if error_path.is_file() else 0,
        "artifacts": artifacts,
        "status": "complete_verified",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path)
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()
    if bool(args.config) != bool(args.run_dir):
        raise ValueError("--config and --run-dir must be supplied together")
    if args.config and args.run_dir:
        report = verify_shard(args.config, args.run_dir)
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    config_manifest = load(EXT / "configs" / "config_manifest.json")
    shards = []
    missing = []
    for relative, expected_hash in sorted(config_manifest["configs"].items()):
        config_path = ROOT / relative
        require(sha(config_path) == expected_hash, f"config hash: {config_path}")
        config = load(config_path)
        run_dir = EXT / "results" / config["treatment_id"] / config_path.stem
        if not (run_dir / "summary.json").is_file():
            missing.append(str(run_dir.relative_to(ROOT)))
            continue
        shards.append(verify_shard(config_path, run_dir))
    if missing:
        raise RuntimeError(f"missing {len(missing)} result shards: {missing}")
    manifest = {
        "schema_version": "nmi-extension-result-manifest-v1",
        "protocol_freeze_commit": "4606413539c908171293f2a47f834fd4d7f8fe30",
        "protocol_amendment_commit": "4ebc679b6dfdec053dc77fe6dd68caa78a2cb4da",
        "shards": shards,
        "shard_count": len(shards),
        "status": "all_raw_shards_complete_and_verified",
    }
    destination = EXT / "result_manifest.json"
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": manifest["status"], "shards": len(shards)}, sort_keys=True))


if __name__ == "__main__":
    main()
