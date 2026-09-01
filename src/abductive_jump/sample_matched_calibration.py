from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .budget import BudgetAccount, EqualBudgetContract
from .conditions import Condition, ProposalSource, build_prompt
from .executable import evaluate_executable, freeze_theory, parse_theory
from .external_reasoning_calibration import _manifest, _prediction_table
from .llm import OpenAICompatibleClient, extract_json_object
from .proposals import apply_mutation_plan
from .realization import fit_representation
from .worlds import generate_world


def _table(rows: list[dict[str, Any]]) -> pa.Table:
    columns = sorted({key for row in rows for key in row})
    return pa.Table.from_pylist([{key: row.get(key) for key in columns} for row in rows])


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    manifest = _manifest(config)
    slots = int(config.get("candidate_slots", 9))
    contract = EqualBudgetContract(slots, 2, manifest.max_tokens)
    output_dir.mkdir(parents=True, exist_ok=True)
    client = OpenAICompatibleClient(base_url, manifest, output_dir / "llm_calls.jsonl")
    rows: list[dict[str, Any]] = []
    worlds: list[dict[str, Any]] = []
    for family_index, family in enumerate(config["families"]):
        for seed_index, world_seed in enumerate(config["world_seeds"]):
            world = generate_world(family, world_seed)
            public = world.public()
            translation = {
                public_name: internal for internal, public_name in world.variable_names
            }
            budget = BudgetAccount(contract.limit)
            successes = 0
            for slot in range(slots):
                base_seed = (
                    int(config["decoding_seed_base"])
                    + family_index * 10_000
                    + seed_index * 100
                    + slot * 2
                )
                row: dict[str, Any] = {
                    "world_id": world.world_id,
                    "family": family,
                    "world_seed": world_seed,
                    "slot": slot,
                    "proposal_parse_valid": False,
                    "reasoning_parse_valid": False,
                    "validated_jump": False,
                }
                try:
                    proposal_prompt = build_prompt(
                        public, Condition.B1_SAMPLE_MATCHED, ProposalSource.P0_LLM
                    )
                    proposal_output, proposal_call = client.generate(
                        proposal_prompt,
                        world_id=world.world_id,
                        world_seed=world_seed,
                        decoding_seed=base_seed,
                        candidate_parent=world.incumbent.structural_hash,
                    )
                    budget.charge(
                        llm_tokens=proposal_call.completion_tokens, llm_calls=1
                    )
                    row["proposal_completion_tokens"] = proposal_call.completion_tokens
                    row["proposal_prompt_hash"] = proposal_call.prompt_hash
                    proposal_payload = extract_json_object(proposal_output)
                    proposal = apply_mutation_plan(
                        world.incumbent,
                        proposal_payload["mutation_plan"],
                        base_seed,
                    )
                    row["proposal_parse_valid"] = True
                    row["representation_hash"] = proposal.representation.structural_hash
                    row["operators"] = list(proposal.operators)
                    fitted = fit_representation(public, proposal.representation)
                    separation_table = _prediction_table(world, fitted.expression)
                    reasoning_prompt = build_prompt(
                        public,
                        Condition.B4_REPRESENTATION_MUTATION,
                        ProposalSource.P0_LLM,
                        proposal.representation,
                        fitted.expression,
                        fitted.observational_loss,
                        separation_table,
                    )
                    output, call = client.generate(
                        reasoning_prompt,
                        world_id=world.world_id,
                        world_seed=world_seed,
                        decoding_seed=base_seed + 1,
                        candidate_parent=world.incumbent.structural_hash,
                        mutation_ancestry=proposal.operators,
                        representation_hash=proposal.representation.structural_hash,
                    )
                    budget.charge(
                        llm_tokens=call.completion_tokens,
                        llm_calls=1,
                        candidate_evaluations=1,
                        interventions=1,
                    )
                    row["reasoning_completion_tokens"] = call.completion_tokens
                    row["reasoning_prompt_hash"] = call.prompt_hash
                    payload = extract_json_object(output)
                    payload["representation"] = proposal.representation.canonical_dict()
                    payload["expression"] = fitted.expression.tree
                    theory = parse_theory(payload, translation)
                    row["reasoning_parse_valid"] = True
                    result = evaluate_executable(world, theory, freeze_theory(world, theory))
                    row.update(asdict(result))
                    row["validated_jump"] = result.validated_jump
                    successes += result.validated_jump
                except (KeyError, TypeError, ValueError, OverflowError) as exc:
                    row["error_type"] = type(exc).__name__
                    row["error"] = str(exc)
                rows.append(row)
            worlds.append(
                {
                    "world_id": world.world_id,
                    "family": family,
                    "world_seed": world_seed,
                    "condition_success": successes > 0,
                    "validated_candidates": successes,
                    "budget": json.dumps(budget.canonical_dict(), sort_keys=True),
                }
            )
    pq.write_table(_table(rows), output_dir / "candidate_results.parquet", compression="zstd")
    pq.write_table(_table(worlds), output_dir / "world_results.parquet", compression="zstd")
    summary = {
        "model_manifest": asdict(manifest),
        "budget_contract": contract.canonical_dict(),
        "worlds": len(worlds),
        "candidates": len(rows),
        "proposal_parse_rate": sum(row["proposal_parse_valid"] for row in rows) / len(rows),
        "reasoning_parse_rate": sum(row["reasoning_parse_valid"] for row in rows) / len(rows),
        "world_success_rate": sum(row["condition_success"] for row in worlds) / len(worlds),
        "candidate_success_rate": sum(row["validated_jump"] for row in rows) / len(rows),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output_dir, args.base_url), indent=2))


if __name__ == "__main__":
    main()
