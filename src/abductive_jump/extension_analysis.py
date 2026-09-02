from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .compositional_experiment import _parse_self_plans, _world
from .conditions import Condition, ProposalSource
from .extension_replay import _calls, _seed, _sha

BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 730_000_001

CJ_HISTORICAL = {
    "known_jump": ("configs/compositional-confirmatory-existing.json", "artifacts/compositional/confirmatory-existing"),
    "known_control": (
        "configs/compositional-confirmatory-existing-control.json",
        "artifacts/compositional/confirmatory-existing-control",
    ),
    "heldout_jump": (
        "configs/compositional-confirmatory-heldout.json",
        "artifacts/compositional/confirmatory-heldout",
    ),
    "heldout_control": (
        "configs/compositional-confirmatory-heldout-control.json",
        "artifacts/compositional/confirmatory-heldout-control",
    ),
}
AJ_HISTORICAL = {
    "factorial_jump": ("configs/confirmatory-factorial-jump.json", "artifacts/confirmatory/factorial-jump"),
    "factorial_control": (
        "configs/confirmatory-factorial-control.json",
        "artifacts/confirmatory/factorial-control",
    ),
}


def _quantile(values: list[float], probability: float) -> float:
    values = sorted(values)
    position = (len(values) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return values[lower]
    return values[lower] * (upper - position) + values[upper] * (position - lower)


def _stable_seed(label: str) -> int:
    return BOOTSTRAP_SEED ^ int(hashlib.sha256(label.encode()).hexdigest()[:8], 16)


def _paired(left: list[dict[str, Any]], right: list[dict[str, Any]], label: str) -> dict[str, Any]:
    left_lookup = {
        (str(row["family"]), int(row["world_seed"])): bool(row["condition_success"])
        for row in left
    }
    right_lookup = {
        (str(row["family"]), int(row["world_seed"])): bool(row["condition_success"])
        for row in right
    }
    if set(left_lookup) != set(right_lookup):
        raise ValueError(f"unpaired world sets for {label}")
    by_family: dict[str, list[tuple[bool, bool]]] = defaultdict(list)
    for key in sorted(left_lookup):
        by_family[key[0]].append((left_lookup[key], right_lookup[key]))
    family_effects = {
        family: sum(int(a) - int(b) for a, b in pairs) / len(pairs)
        for family, pairs in by_family.items()
    }
    estimate = sum(family_effects.values()) / len(family_effects)
    rng = random.Random(_stable_seed(label))
    samples = []
    for _ in range(BOOTSTRAP_REPLICATES):
        effects = []
        for pairs in by_family.values():
            drawn = [rng.choice(pairs) for _ in pairs]
            effects.append(sum(int(a) - int(b) for a, b in drawn) / len(drawn))
        samples.append(sum(effects) / len(effects))
    discordant_left = sum(a and not b for pairs in by_family.values() for a, b in pairs)
    discordant_right = sum(b and not a for pairs in by_family.values() for a, b in pairs)
    discordant = discordant_left + discordant_right
    if discordant:
        tail = sum(
            math.comb(discordant, value)
            for value in range(min(discordant_left, discordant_right) + 1)
        ) / (2**discordant)
        p_two_sided = min(1.0, 2 * tail)
    else:
        p_two_sided = 1.0
    return {
        "estimate": estimate,
        "ci_low": _quantile(samples, 0.025),
        "ci_high": _quantile(samples, 0.975),
        "discordant_left_wins": discordant_left,
        "discordant_right_wins": discordant_right,
        "mcnemar_exact_p_two_sided": p_two_sided,
        "family_effects_json": json.dumps(family_effects, sort_keys=True),
        "paired_worlds": len(left_lookup),
    }


def _holm(rows: list[dict[str, Any]]) -> None:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_family[str(row["multiplicity_family"])].append(row)
    for values in by_family.values():
        running = 0.0
        for index, row in enumerate(sorted(values, key=lambda x: x["mcnemar_exact_p_two_sided"])):
            running = max(
                running,
                min(1.0, (len(values) - index) * float(row["mcnemar_exact_p_two_sided"])),
            )
            row["mcnemar_holm_p"] = running


def _read_rows(path: Path, name: str) -> list[dict[str, Any]]:
    return pq.read_table(path / name).to_pylist()


def _historical_plan_rows(root: Path, split: str, config_rel: str, run_rel: str) -> list[dict[str, Any]]:
    config = json.loads((root / config_rel).read_text())
    run = root / run_rel
    calls = _calls(run / "llm_calls.jsonl")
    rows: list[dict[str, Any]] = []
    condition = Condition.C_SELF_LLM_COMPOSITION
    for family in config["families"]:
        for world_seed in config["world_seeds"]:
            world = _world(config, family, int(world_seed))
            search_seed = int(config["search_seed_base"]) + world.seed * 101 + list(Condition).index(condition)
            for slot in range(int(config["candidate_slots"])):
                decoding_seed = _seed(config, condition, world.family, world.seed, slot)
                call = calls[
                    (
                        condition.value,
                        ProposalSource.LLM_COMPOSITION.value,
                        world.world_id,
                        decoding_seed,
                    )
                ]
                _, trace = _parse_self_plans(
                    world,
                    str(call["full_output"]),
                    search_seed + slot * 1000,
                    required_plans=int(config["self_plans_per_slot"]),
                )
                rows.extend(
                    {
                        "treatment_id": "phi4_historical",
                        "split": split,
                        "family": family,
                        "world_id": world.world_id,
                        "world_seed": world.seed,
                        "slot": slot,
                        "repair_stage": "initial",
                        "request_returned": True,
                        **item,
                    }
                    for item in trace
                )
    return rows


def _add_identity(
    rows: list[dict[str, Any]], treatment: str, study: str, split: str
) -> list[dict[str, Any]]:
    return [
        {"treatment_id": treatment, "study": study, "split": split, **row}
        for row in rows
    ]


def _aggregate_boolean_stages(
    rows: list[dict[str, Any]], stages: tuple[str, ...], grain: str
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    keys = ("treatment_id", "study", "split", "family", "source", "repair_stage")
    for row in rows:
        normalized = {
            **row,
            "source": row.get("proposal_source", "C_SELF"),
            "repair_stage": row.get("repair_stage", ""),
        }
        grouped[tuple(str(normalized.get(key, "")) for key in keys)].append(normalized)
    output = []
    for group, values in sorted(grouped.items()):
        for stage in stages:
            applicable = [row for row in values if row.get(stage) is not None]
            output.append(
                {
                    **dict(zip(keys, group, strict=True)),
                    "grain": grain,
                    "stage": stage,
                    "successes": sum(bool(row.get(stage)) for row in applicable),
                    "total": len(applicable),
                    "rate": (
                        sum(bool(row.get(stage)) for row in applicable) / len(applicable)
                        if applicable
                        else None
                    ),
                }
            )
    return output


def _call_ledger(
    treatment: str, study: str, split: str, config_path: Path, run_dir: Path
) -> list[dict[str, Any]]:
    config = json.loads(config_path.read_text())
    cap = int(config["generation"]["max_tokens"])
    rows = [json.loads(line) for line in (run_dir / "llm_calls.jsonl").read_text().splitlines()]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["condition"]), str(row["proposal_source"]))].append(row)
    result = []
    for (condition, source), values in sorted(grouped.items()):
        unquantified_reasoning = any(
            bool(row.get("reasoning_output")) and row.get("reasoning_tokens") is None
            for row in values
        )
        reasoning_split_available = not unquantified_reasoning
        result.append(
            {
                "treatment_id": treatment,
                "study": study,
                "split": split,
                "condition": condition,
                "proposal_source": source,
                "model": config["model"],
                "reasoning_effort": config.get("reasoning_effort"),
                "max_tokens": cap,
                "llm_calls": len(values),
                "transport_attempts": sum(int(row.get("attempt_count", 1)) for row in values),
                "prompt_tokens": sum(int(row.get("prompt_tokens", 0)) for row in values),
                "completion_tokens": sum(int(row.get("completion_tokens", 0)) for row in values),
                "total_tokens": sum(
                    int(
                        row.get("total_tokens")
                        or int(row.get("prompt_tokens", 0)) + int(row.get("completion_tokens", 0))
                    )
                    for row in values
                ),
                "reasoning_token_split_available": reasoning_split_available,
                "reasoning_tokens": (
                    sum(int(row.get("reasoning_tokens") or 0) for row in values)
                    if reasoning_split_available
                    else None
                ),
                "answer_tokens": (
                    sum(
                        int(row.get("answer_tokens") or row.get("completion_tokens", 0))
                        for row in values
                    )
                    if reasoning_split_available
                    else None
                ),
                "nonempty_reasoning_responses": sum(bool(row.get("reasoning_output")) for row in values),
                "completion_cap_hits": sum(int(row.get("completion_tokens", 0)) == cap for row in values),
                "latency_seconds_sum": sum(float(row.get("latency_seconds", 0.0)) for row in values),
                "latency_seconds_mean": sum(float(row.get("latency_seconds", 0.0)) for row in values)
                / len(values),
            }
        )
    return result


def run(root: Path) -> dict[str, Any]:
    extension = root / "experiments" / "nmi_extension_v1"
    results_root = extension / "results"
    analysis_dir = extension / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    world_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    plan_rows: list[dict[str, Any]] = []
    ledgers: list[dict[str, Any]] = []
    source_artifacts: dict[str, str] = {}

    for split, (config_rel, run_rel) in CJ_HISTORICAL.items():
        run_dir = root / run_rel
        config_path = root / config_rel
        worlds = [
            row
            for row in _read_rows(run_dir, "world_results.parquet")
            if row["condition"] == Condition.C_SELF_LLM_COMPOSITION.value
        ]
        candidates = [
            row
            for row in _read_rows(run_dir, "candidate_results.parquet")
            if row["condition"] == Condition.C_SELF_LLM_COMPOSITION.value
        ]
        world_rows.extend(_add_identity(worlds, "phi4_historical", "CJ_CSELF", split))
        candidate_rows.extend(_add_identity(candidates, "phi4_historical", "CJ_CSELF", split))
        historical_plans = _historical_plan_rows(root, split, config_rel, run_rel)
        plan_rows.extend({"study": "CJ_CSELF", **row} for row in historical_plans)
        ledgers.extend(_call_ledger("phi4_historical", "CJ_CSELF", split, config_path, run_dir))
        source_artifacts[str(run_dir.relative_to(root))] = _sha(run_dir / "llm_calls.jsonl")

    for split, (config_rel, run_rel) in AJ_HISTORICAL.items():
        run_dir = root / run_rel
        config_path = root / config_rel
        world_rows.extend(
            _add_identity(_read_rows(run_dir, "world_results.parquet"), "phi4_historical", "AJ_FACTORIAL", split)
        )
        candidate_rows.extend(
            _add_identity(_read_rows(run_dir, "candidate_results.parquet"), "phi4_historical", "AJ_FACTORIAL", split)
        )
        ledgers.extend(_call_ledger("phi4_historical", "AJ_FACTORIAL", split, config_path, run_dir))
        source_artifacts[str(run_dir.relative_to(root))] = _sha(run_dir / "llm_calls.jsonl")

    if results_root.exists():
        for treatment_dir in sorted(path for path in results_root.iterdir() if path.is_dir()):
            treatment = treatment_dir.name
            for run_dir in sorted(path for path in treatment_dir.iterdir() if path.is_dir()):
                if not (run_dir / "summary.json").is_file():
                    continue
                split = run_dir.name
                config_path = extension / "configs" / treatment / f"{split}.json"
                study = "AJ_FACTORIAL" if split.startswith("factorial_") else "CJ_CSELF"
                world_rows.extend(
                    _add_identity(_read_rows(run_dir, "world_results.parquet"), treatment, study, split)
                )
                candidate_rows.extend(
                    _add_identity(_read_rows(run_dir, "candidate_results.parquet"), treatment, study, split)
                )
                trace_path = run_dir / "llm_self_plans.parquet"
                if trace_path.is_file():
                    plan_rows.extend(
                        _add_identity(pq.read_table(trace_path).to_pylist(), treatment, study, split)
                    )
                ledgers.extend(_call_ledger(treatment, study, split, config_path, run_dir))
                source_artifacts[str(run_dir.relative_to(root))] = _sha(run_dir / "llm_calls.jsonl")

    comparisons = []
    indexed: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in world_rows:
        source = str(row.get("proposal_source", "C_SELF"))
        indexed[(str(row["treatment_id"]), str(row["study"]), str(row["split"]), source)].append(row)
    contrast_pairs = (
        ("deepseek_matched", "phi4_historical"),
        ("deepseek_native", "deepseek_matched"),
        ("deepseek_repair", "deepseek_native"),
        ("deepseek_constrained", "deepseek_native"),
        ("phi_budget", "phi4_historical"),
        ("phi_constrained", "phi4_historical"),
        ("phi_repair", "phi4_historical"),
        ("phi8_precision", "phi4_historical"),
    )
    for study in ("CJ_CSELF", "AJ_FACTORIAL"):
        sources = ("C_SELF",) if study == "CJ_CSELF" else (ProposalSource.P0_LLM.value,)
        splits = sorted({str(row["split"]) for row in world_rows if row["study"] == study})
        for split in splits:
            for source in sources:
                for left, right in contrast_pairs:
                    left_rows = indexed.get((left, study, split, source), [])
                    right_rows = indexed.get((right, study, split, source), [])
                    if not left_rows or not right_rows:
                        continue
                    label = f"{study}:{split}:{source}:{left}:{right}"
                    comparison = _paired(left_rows, right_rows, label)
                    comparison.update(
                        {
                            "study": study,
                            "split": split,
                            "source": source,
                            "left": left,
                            "right": right,
                            "multiplicity_family": f"{study}:{source}",
                        }
                    )
                    comparisons.append(comparison)
    _holm(comparisons)

    plan_stages = (
        "request_returned",
        "non_empty_answer",
        "json_parse_valid",
        "plan_schema_valid",
        "operation_names_valid",
        "argument_types_valid",
        "executable",
        "representation_constructed",
        "valid",
    )
    gate_stages = ("phase_one_valid", "phase_two_valid", "j0", "j1", "j2", "j3", "j4", "j5", "validated_jump")
    attrition = _aggregate_boolean_stages(plan_rows, plan_stages, "plan_attempt")
    attrition.extend(_aggregate_boolean_stages(candidate_rows, gate_stages, "retained_candidate"))

    repaired_slots = {
        (
            str(row["treatment_id"]),
            str(row["split"]),
            str(row["world_id"]),
            int(row["slot"]),
        )
        for row in plan_rows
        if row.get("repair_stage") == "repair"
    }
    final_plan_rows = [
        row
        for row in plan_rows
        if row.get("repair_stage") == "repair"
        or (
            row.get("repair_stage") == "initial"
            and (
                str(row["treatment_id"]),
                str(row["split"]),
                str(row["world_id"]),
                int(row["slot"]),
            )
            not in repaired_slots
        )
    ]
    for ledger in ledgers:
        treatment = str(ledger["treatment_id"])
        study = str(ledger["study"])
        split = str(ledger["split"])
        source = str(ledger["proposal_source"])
        selected_candidates = [
            row
            for row in candidate_rows
            if row["treatment_id"] == treatment
            and row["study"] == study
            and row["split"] == split
            and str(row.get("proposal_source", "C_SELF")) == (
                source if study == "AJ_FACTORIAL" else "C_SELF"
            )
        ]
        selected_worlds = [
            row
            for row in world_rows
            if row["treatment_id"] == treatment
            and row["study"] == study
            and row["split"] == split
            and str(row.get("proposal_source", "C_SELF")) == (
                source if study == "AJ_FACTORIAL" else "C_SELF"
            )
        ]
        if study == "CJ_CSELF":
            raw_plans = [
                row
                for row in plan_rows
                if row["treatment_id"] == treatment and row["split"] == split
            ]
            final_plans = [
                row
                for row in final_plan_rows
                if row["treatment_id"] == treatment and row["split"] == split
            ]
            ledger["raw_plan_outputs_attempted"] = len(raw_plans)
            ledger["final_representation_attempts"] = len(final_plans)
            ledger["valid_final_plans"] = sum(bool(row.get("valid")) for row in final_plans)
            ledger["constructed_final_representations"] = sum(
                bool(row.get("representation_constructed")) for row in final_plans
            )
        else:
            ledger["raw_plan_outputs_attempted"] = None
            ledger["final_representation_attempts"] = len(selected_candidates)
            ledger["valid_final_plans"] = None
            ledger["constructed_final_representations"] = sum(
                bool(row.get("phase_one_valid")) and not bool(row.get("fallback_to_incumbent"))
                for row in selected_candidates
            )
        ledger["worlds"] = len(selected_worlds)
        ledger["final_candidate_slots"] = len(selected_candidates)
        ledger["committed_interventions"] = sum(
            bool(row.get("phase_two_valid")) for row in selected_candidates
        )
        ledger["generic_operations_evaluated"] = sum(
            int(row.get("primitive_operations_used", 0)) for row in selected_worlds
        )
        ledger["declared_candidate_evaluations"] = sum(
            int(row.get("candidate_evaluations", 0)) for row in selected_worlds
        )
        ledger["deterministic_fitter_calls_derived"] = (
            sum(bool(row.get("valid")) for row in final_plans) + len(selected_candidates)
            if study == "CJ_CSELF"
            else len(selected_candidates)
            + sum(bool(row.get("realization_error_type")) for row in selected_candidates)
        )
        ledger["simulator_calls"] = None
        ledger["simulator_accounting_note"] = (
            "Not instrumented in the frozen runner; exact deterministic replay is reported, "
            "but a post hoc scalar simulator-call count would depend on counting convention."
        )

    outputs = {
        "world_results.parquet": world_rows,
        "candidate_results.parquet": candidate_rows,
        "plan_attempts.parquet": plan_rows,
        "gate_attrition.parquet": attrition,
        "compute_ledger.parquet": ledgers,
        "paired_comparisons.parquet": comparisons,
    }
    hashes = {}
    for name, rows in outputs.items():
        path = analysis_dir / name
        pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")
        hashes[name] = _sha(path)
    report = {
        "schema_version": "nmi-extension-analysis-v1",
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "completed_extension_shards": sum(
            (path / "summary.json").is_file()
            for treatment in results_root.iterdir()
            if treatment.is_dir()
            for path in treatment.iterdir()
            if path.is_dir()
        )
        if results_root.exists()
        else 0,
        "row_counts": {name: len(rows) for name, rows in outputs.items()},
        "output_sha256": hashes,
        "source_llm_call_sha256": source_artifacts,
        "candidate_independence_warning": "Plan and candidate attrition are descriptive; the inferential replicate is the world.",
        "reasoning_accounting_warning": "DeepSeek exposes reasoning text but not separate reasoning-token counts; answer/reasoning token splits are therefore null when unavailable.",
    }
    (analysis_dir / "analysis_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    run(args.root)


if __name__ == "__main__":
    main()
