"""Completion-locked deterministic replay for the minimal NMI sensitivity study."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .conditions import Condition, ProposalSource, build_prompt
from .extension_replay import replay_compositional
from .minimal_sensitivity_analysis import CSSELF_RUNS, require_finalized
from .primary_experiment import _thresholds
from .supplied_representation_experiment import evaluate_model_output
from .worlds import FAMILIES, generate_world


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value: Any) -> Any:
    if isinstance(value, tuple):
        return [normalized(item) for item in value]
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items()}
    return value


def compare_saved(prefix: str, saved: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    mismatches = []
    for field, value in expected.items():
        if field not in saved or saved[field] is None:
            mismatches.append(f"{prefix}:missing:{field}")
            continue
        stored = saved[field]
        if isinstance(value, float):
            if not isinstance(stored, (float, int)) or abs(float(stored) - value) > 1e-10:
                mismatches.append(f"{prefix}:{field}")
        elif normalized(stored) != normalized(value):
            mismatches.append(f"{prefix}:{field}")
    return mismatches


def p2_decoding_seed(config: dict[str, Any], family: str, world_seed: int, slot: int) -> int:
    return (
        int(config["decoding_seed_base"])
        + list(Condition).index(Condition.C5_ORACLE_REPRESENTATION) * 10_000_000
        + FAMILIES.index(family) * 100_000
        + world_seed * 100
        + slot
    )


def load_calls(path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    result = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            key = (str(row["world_id"]), int(row["decoding_seed"]))
            if key in result:
                raise ValueError(f"duplicate P2 raw call key: {key}")
            result[key] = row
    return result


def require_exact_keys(actual: list[tuple[Any, ...]], expected: set[tuple[Any, ...]], label: str) -> None:
    if len(actual) != len(set(actual)):
        raise ValueError(f"{label} contains duplicate logical keys")
    actual_set = set(actual)
    if actual_set != expected:
        missing = sorted(expected - actual_set)[:5]
        extra = sorted(actual_set - expected)[:5]
        raise ValueError(f"{label} panel mismatch; missing={missing}, extra={extra}")


def require_exact_panel(config_path: Path, run_dir: Path, *, p2: bool) -> None:
    config = json.loads(config_path.read_text())
    candidate_rows = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    world_rows = pq.read_table(run_dir / "world_results.parquet").to_pylist()
    expected_worlds = {}
    for family in config["families"]:
        for seed in config["world_seeds"]:
            world = (
                generate_world(str(family), int(seed), no_jump=False)
                if p2
                else generate_world(str(family), int(seed), no_jump=bool(config["no_jump"]))
            )
            expected_worlds[(str(family), int(seed))] = world.world_id
    expected_world_keys = {
        (family, seed, world_id) for (family, seed), world_id in expected_worlds.items()
    }
    actual_world_keys = [
        (str(row["family"]), int(row["world_seed"]), str(row["world_id"]))
        for row in world_rows
    ]
    require_exact_keys(actual_world_keys, expected_world_keys, f"{run_dir.name} worlds")
    expected_candidate_keys = {
        (family, seed, world_id, slot)
        for (family, seed), world_id in expected_worlds.items()
        for slot in range(int(config["candidate_slots"]))
    }
    actual_candidate_keys = [
        (
            str(row["family"]),
            int(row["world_seed"]),
            str(row["world_id"]),
            int(row["slot"]),
        )
        for row in candidate_rows
    ]
    require_exact_keys(actual_candidate_keys, expected_candidate_keys, f"{run_dir.name} candidates")
    if not p2:
        call_rows = [json.loads(line) for line in (run_dir / "llm_calls.jsonl").read_text().splitlines()]
        condition = Condition.C_SELF_LLM_COMPOSITION
        expected_call_keys = set()
        initial_seed_by_slot = {}
        for (family, seed), world_id in expected_worlds.items():
            family_index = FAMILIES.index(family)
            for slot in range(int(config["candidate_slots"])):
                initial_seed = (
                    int(config["decoding_seed_base"])
                    + list(Condition).index(condition) * 10_000_000
                    + family_index * 100_000
                    + seed * 100
                    + slot * 2
                )
                initial_seed_by_slot[(world_id, slot)] = initial_seed
                expected_call_keys.add(
                    (
                        condition.value,
                        ProposalSource.LLM_COMPOSITION.value,
                        world_id,
                        initial_seed,
                    )
                )
                expected_call_keys.add(
                    (
                        condition.value,
                        ProposalSource.COMPOSITION_SEARCH.value,
                        world_id,
                        initial_seed + 1,
                    )
                )
        if int(config.get("validator_repair_attempts", 0)) == 1:
            plan_rows = pq.read_table(run_dir / "llm_self_plans.parquet").to_pylist()
            repair_slots = {
                (str(row["world_id"]), int(row["slot"]))
                for row in plan_rows
                if row.get("repair_stage") == "repair"
            }
            for world_slot in repair_slots:
                expected_call_keys.add(
                    (
                        condition.value,
                        ProposalSource.LLM_COMPOSITION.value,
                        world_slot[0],
                        initial_seed_by_slot[world_slot] + 50_000_000,
                    )
                )
        actual_call_keys = [
            (
                str(row["condition"]),
                str(row["proposal_source"]),
                str(row["world_id"]),
                int(row["decoding_seed"]),
            )
            for row in call_rows
        ]
        require_exact_keys(actual_call_keys, expected_call_keys, f"{run_dir.name} calls")


def replay_p2(config_path: Path, run_dir: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    saved_rows = pq.read_table(run_dir / "candidate_results.parquet").to_pylist()
    calls = load_calls(run_dir / "llm_calls.jsonl")
    expected_rows = len(config["families"]) * len(config["world_seeds"]) * int(
        config["candidate_slots"]
    )
    if len(saved_rows) != expected_rows or len(calls) != expected_rows:
        raise ValueError("P2 replay cardinality mismatch")
    output_rows = []
    mismatches: list[str] = []
    for saved in saved_rows:
        family = str(saved["family"])
        world_seed = int(saved["world_seed"])
        slot = int(saved["slot"])
        world = generate_world(family, world_seed, no_jump=False)
        seed = p2_decoding_seed(config, family, world_seed, slot)
        call = calls[(world.world_id, seed)]
        prefix = f"deepseek_p2:{world.world_id}:{slot}"
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
        prompt_hash = hashlib.sha256(prompt_json.encode()).hexdigest()
        mismatches.extend(
            compare_saved(
                prefix,
                call,
                {
                    "condition": Condition.C5_ORACLE_REPRESENTATION.value,
                    "proposal_source": ProposalSource.P2_ORACLE.value,
                    "world_id": world.world_id,
                    "world_seed": world_seed,
                    "decoding_seed": seed,
                    "prompt_template_version": prompt.template_version,
                    "prompt_hash": prompt_hash,
                    "full_prompt_json": prompt_json,
                    "representation_hash": world.truth.representation.structural_hash,
                },
            )
        )
        replay_verified = False
        result_fields: dict[str, Any] = {}
        try:
            result_fields = evaluate_model_output(
                world, str(call["full_output"]), _thresholds(config)
            )
            result_fields["parse_valid"] = True
            result_fields["executable"] = True
            result_fields["validated_jump"] = all(
                bool(result_fields[f"j{index}"]) for index in range(6)
            )
            mismatches.extend(compare_saved(prefix, saved, result_fields))
            replay_verified = True
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            expected = {
                "parse_valid": False,
                "executable": False,
                "validated_jump": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            mismatches.extend(compare_saved(prefix, saved, expected))
            replay_verified = not any(item.startswith(prefix + ":") for item in mismatches)
        output_rows.append(
            {
                **saved,
                **result_fields,
                "raw_call_sha256": hashlib.sha256(
                    json.dumps(call, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
                "replay_verified": replay_verified,
            }
        )
    if mismatches:
        raise ValueError(f"P2 replay mismatches ({len(mismatches)}): {mismatches[:20]}")
    destination = run_dir / "replayed_candidates.parquet"
    pq.write_table(pa.Table.from_pylist(output_rows), destination, compression="zstd")
    return {
        "kind": "causal_supplied_representation_positive_control",
        "config_sha256": digest(config_path),
        "raw_calls_sha256": digest(run_dir / "llm_calls.jsonl"),
        "candidate_rows": len(output_rows),
        "verified_rows": sum(bool(row["replay_verified"]) for row in output_rows),
        "mismatches": 0,
        "replayed_candidates_sha256": digest(destination),
    }


def replay_all(root: Path) -> dict[str, Any]:
    base = root / "experiments" / "nmi_minimal_sensitivity_v1"
    results = base / "results"
    require_finalized(results)
    reports = {}
    for name in CSSELF_RUNS:
        config_path = base / "configs" / f"{name}.json"
        require_exact_panel(config_path, results / name, p2=False)
        report = replay_compositional(config_path, results / name)
        if int(report["verified_rows"]) != int(report["candidate_rows"]):
            raise ValueError(
                f"{name} replay incomplete: {report['verified_rows']}/{report['candidate_rows']} rows verified"
            )
        (results / name / "replay_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        reports[name] = report
    p2_config = base / "configs" / "deepseek_p2.json"
    require_exact_panel(p2_config, results / "deepseek_p2", p2=True)
    p2_report = replay_p2(p2_config, results / "deepseek_p2")
    if int(p2_report["verified_rows"]) != int(p2_report["candidate_rows"]):
        raise ValueError(
            "deepseek_p2 replay incomplete: "
            f"{p2_report['verified_rows']}/{p2_report['candidate_rows']} rows verified"
        )
    (results / "deepseek_p2" / "replay_report.json").write_text(
        json.dumps(p2_report, indent=2, sort_keys=True) + "\n"
    )
    reports["deepseek_p2"] = p2_report
    overall = {
        "status": "complete_verified",
        "model_calls_made": 0,
        "shards": reports,
        "candidate_rows": sum(int(report["candidate_rows"]) for report in reports.values()),
        "verified_rows": sum(int(report["verified_rows"]) for report in reports.values()),
        "mismatches": 0,
    }
    if overall["verified_rows"] != overall["candidate_rows"]:
        raise ValueError("overall minimal sensitivity replay did not verify every candidate row")
    analysis_dir = base / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "replay_report.json").write_text(
        json.dumps(overall, indent=2, sort_keys=True) + "\n"
    )
    return overall


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(replay_all(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
