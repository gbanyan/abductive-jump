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
from .llm import ModelManifest, OpenAICompatibleClient, extract_json_object
from .oracle import incumbent_oracle
from .proposals import external_representation_proposals
from .realization import fit_representation
from .worlds import generate_world, predict


def _prediction_table(world: Any, expression: Any) -> list[dict[str, object]]:
    oracle = incumbent_oracle(world)
    return [
        {
            "case_id": case.case_id,
            "candidate_prediction": expression.evaluate(
                query["inputs"], query["intervention"]
            ),
            "incumbent_oracle_prediction": predict(
                oracle.program, dict(case.inputs), dict(case.intervention)
            ),
            "absolute_separation": abs(
                expression.evaluate(query["inputs"], query["intervention"])
                - predict(oracle.program, dict(case.inputs), dict(case.intervention))
            ),
        }
        for case, query in zip(world.interventions, world.public().intervention_queries)
    ]


def _manifest(config: dict[str, Any]) -> ModelManifest:
    generation = config["generation"]
    return ModelManifest(
        config["model"],
        config["revision"],
        config["quantization"],
        config["engine"],
        config["engine_version"],
        config["context_limit"],
        generation["temperature"],
        generation["top_p"],
        generation["max_tokens"],
    )


def _arrow_table(rows: list[dict[str, Any]]) -> pa.Table:
    """Preserve sparse error/result fields regardless of which row comes first."""
    columns = sorted({key for row in rows for key in row})
    return pa.Table.from_pylist(
        [{key: row.get(key) for key in columns} for row in rows]
    )


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    manifest = _manifest(config)
    candidate_slots = int(config.get("candidate_slots", 9))
    contract = EqualBudgetContract(
        candidate_slots=candidate_slots,
        calls_per_slot=1,
        max_completion_tokens_per_call=manifest.max_tokens,
    )
    if candidate_slots > 9:
        raise ValueError("the frozen external portfolio has exactly nine candidates")
    output_dir.mkdir(parents=True, exist_ok=True)
    client = OpenAICompatibleClient(base_url, manifest, output_dir / "llm_calls.jsonl")
    candidate_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    for family_index, family in enumerate(config["families"]):
        for seed_index, world_seed in enumerate(config["world_seeds"]):
            world = generate_world(family, world_seed)
            public = world.public()
            proposals = external_representation_proposals(
                public, world_seed ^ 0x5151
            )[:candidate_slots]
            budget = BudgetAccount(contract.limit)
            world_successes = 0
            for proposal_index, proposal in enumerate(proposals):
                row: dict[str, Any] = {
                    "world_id": world.world_id,
                    "family": family,
                    "world_seed": world_seed,
                    "proposal_index": proposal_index,
                    "representation_hash": proposal.representation.structural_hash,
                    "operators": list(proposal.operators),
                    "parse_valid": False,
                    "validated_jump": False,
                }
                try:
                    fitted = fit_representation(public, proposal.representation)
                    table = _prediction_table(world, fitted.expression)
                    prompt = build_prompt(
                        public,
                        Condition.B4_REPRESENTATION_MUTATION,
                        ProposalSource.P1_EXTERNAL,
                        proposal.representation,
                        fitted.expression,
                        fitted.observational_loss,
                        table,
                    )
                    output, call = client.generate(
                        prompt,
                        world_id=world.world_id,
                        world_seed=world_seed,
                        decoding_seed=(
                            int(config["decoding_seed_base"])
                            + family_index * 10_000
                            + seed_index * 100
                            + proposal_index
                        ),
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
                    row["prompt_hash"] = call.prompt_hash
                    row["completion_tokens"] = call.completion_tokens
                    row["latency_seconds"] = call.latency_seconds
                    payload = extract_json_object(output)
                    # The representation and fitted hypothesis genome are frozen inputs
                    # in P1; the model may interpret and choose an experiment, not replace them.
                    payload["representation"] = proposal.representation.canonical_dict()
                    payload["expression"] = fitted.expression.tree
                    theory = parse_theory(
                        payload,
                        {public_name: internal for internal, public_name in world.variable_names},
                    )
                    row["parse_valid"] = True
                    result = evaluate_executable(world, theory, freeze_theory(world, theory))
                    row.update(asdict(result))
                    row["validated_jump"] = result.validated_jump
                    row["selected_intervention_ids"] = list(
                        theory.selected_intervention_ids
                    )
                    row["prediction_table"] = json.dumps(table, sort_keys=True)
                    world_successes += result.validated_jump
                except (KeyError, TypeError, ValueError, OverflowError) as exc:
                    row["error_type"] = type(exc).__name__
                    row["error"] = str(exc)
                candidate_rows.append(row)
            world_rows.append(
                {
                    "world_id": world.world_id,
                    "family": family,
                    "world_seed": world_seed,
                    "condition_success": world_successes > 0,
                    "validated_candidates": world_successes,
                    "budget": json.dumps(budget.canonical_dict(), sort_keys=True),
                }
            )
    pq.write_table(
        _arrow_table(candidate_rows),
        output_dir / "candidate_results.parquet",
        compression="zstd",
    )
    pq.write_table(
        _arrow_table(world_rows),
        output_dir / "world_results.parquet",
        compression="zstd",
    )
    summary = {
        "model_manifest": asdict(manifest),
        "budget_contract": contract.canonical_dict(),
        "worlds": len(world_rows),
        "candidates": len(candidate_rows),
        "parse_rate": (
            sum(bool(row["parse_valid"]) for row in candidate_rows)
            / len(candidate_rows)
        ),
        "world_success_rate": (
            sum(bool(row["condition_success"]) for row in world_rows) / len(world_rows)
        ),
        "candidate_success_rate": (
            sum(bool(row["validated_jump"]) for row in candidate_rows)
            / len(candidate_rows)
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
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
