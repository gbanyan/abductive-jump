from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .conditions import Condition, ProposalSource, build_prompt
from .executable import evaluate_executable, freeze_theory, parse_theory
from .llm import ModelManifest, OpenAICompatibleClient, extract_json_object
from .oracle import incumbent_oracle
from .realization import fit_representation
from .worlds import generate_world, predict


def run(config_path: Path, output_dir: Path, base_url: str) -> dict[str, Any]:
    config = json.loads(config_path.read_text())
    generation = config["generation"]
    manifest = ModelManifest(
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
    output_dir.mkdir(parents=True, exist_ok=True)
    client = OpenAICompatibleClient(base_url, manifest, output_dir / "llm_calls.jsonl")
    rows: list[dict[str, Any]] = []
    for family_index, family in enumerate(config["families"]):
        for seed_index, world_seed in enumerate(config["world_seeds"]):
            world = generate_world(family, world_seed)
            base_seed = config["decoding_seed_base"] + family_index * 100 + seed_index * 10
            row: dict[str, Any] = {
                "family": family,
                "world_id": world.world_id,
                "world_seed": world_seed,
                "proposal_parse_valid": False,
                "realization_valid": False,
                "reasoning_parse_valid": False,
                "validated_jump": False,
            }
            try:
                proposal_prompt = build_prompt(
                    world.public(), Condition.B0_DIRECT_LLM, ProposalSource.P0_LLM
                )
                proposal_output, proposal_call = client.generate(
                    proposal_prompt,
                    world_id=world.world_id,
                    world_seed=world_seed,
                    decoding_seed=base_seed,
                )
                translation = {public: internal for internal, public in world.variable_names}
                proposed = parse_theory(extract_json_object(proposal_output), translation)
                row["proposal_parse_valid"] = True
                row["proposal_prompt_hash"] = proposal_call.prompt_hash
                row["proposed_representation_hash"] = proposed.representation.structural_hash
                fitted_public = fit_representation(world.public(), proposed.representation)
                row["realization_valid"] = True
                row["realization_observational_loss_public"] = fitted_public.observational_loss
                oracle = incumbent_oracle(world)
                table = []
                for case, query in zip(world.interventions, world.public().intervention_queries):
                    candidate_prediction = fitted_public.expression.evaluate(
                        query["inputs"], query["intervention"]
                    )
                    oracle_prediction = predict(
                        oracle.program, dict(case.inputs), dict(case.intervention)
                    )
                    table.append(
                        {
                            "case_id": case.case_id,
                            "candidate_prediction": candidate_prediction,
                            "incumbent_oracle_prediction": oracle_prediction,
                            "absolute_separation": abs(candidate_prediction - oracle_prediction),
                        }
                    )
                reasoning_prompt = build_prompt(
                    world.public(),
                    Condition.B4_REPRESENTATION_MUTATION,
                    ProposalSource.P0_LLM,
                    proposed.representation,
                    fitted_public.expression,
                    fitted_public.observational_loss,
                    table,
                )
                reasoning_output, reasoning_call = client.generate(
                    reasoning_prompt,
                    world_id=world.world_id,
                    world_seed=world_seed,
                    decoding_seed=base_seed + 1,
                    candidate_parent=world.incumbent.structural_hash,
                    representation_hash=proposed.representation.structural_hash,
                )
                payload = extract_json_object(reasoning_output)
                payload["representation"] = proposed.representation.canonical_dict()
                payload["expression"] = fitted_public.expression.tree
                theory = parse_theory(payload, translation)
                row["reasoning_parse_valid"] = True
                gates = evaluate_executable(world, theory, freeze_theory(world, theory))
                row.update(asdict(gates))
                row["validated_jump"] = gates.validated_jump
                row["reasoning_prompt_hash"] = reasoning_call.prompt_hash
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                row["error_type"] = type(exc).__name__
                row["error"] = str(exc)
            rows.append(row)
            with (output_dir / "spontaneous_results.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
    summary = {
        "model_manifest": asdict(manifest),
        "n": len(rows),
        "proposal_parse_rate": sum(bool(row["proposal_parse_valid"]) for row in rows) / len(rows),
        "success_rate": sum(bool(row["validated_jump"]) for row in rows) / len(rows),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.output_dir, args.base_url), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
