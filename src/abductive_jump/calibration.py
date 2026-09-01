from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
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
    if config["revision"].startswith("RESOLVE_"):
        raise ValueError("model revision must be resolved and recorded before calibration")
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
    result_path = output_dir / "calibration_results.jsonl"
    rows: list[dict[str, Any]] = []
    sources = tuple(
        ProposalSource(value)
        for value in config.get("proposal_sources", ["P0_LLM", "P2_ORACLE"])
    )
    for family_index, family in enumerate(config["families"]):
        for seed_index, world_seed in enumerate(config["world_seeds"]):
            world = generate_world(family, world_seed)
            for source in sources:
                supplied = world.truth.representation if source is ProposalSource.P2_ORACLE else None
                fitted = (
                    fit_representation(world.public(), supplied)
                    if supplied is not None and config.get("realization_mode") == "deterministic_fit"
                    else None
                )
                separation_table = None
                if fitted is not None:
                    oracle = incumbent_oracle(world)
                    public_queries = world.public().intervention_queries
                    separation_table = []
                    for case, query in zip(world.interventions, public_queries):
                        candidate_prediction = fitted.expression.evaluate(
                            query["inputs"], query["intervention"]
                        )
                        oracle_prediction = predict(
                            oracle.program, dict(case.inputs), dict(case.intervention)
                        )
                        separation_table.append(
                            {
                                "case_id": case.case_id,
                                "candidate_prediction": candidate_prediction,
                                "incumbent_oracle_prediction": oracle_prediction,
                                "absolute_separation": abs(
                                    candidate_prediction - oracle_prediction
                                ),
                            }
                        )
                condition = Condition.B4_REPRESENTATION_MUTATION if supplied else Condition.B0_DIRECT_LLM
                prompt = build_prompt(
                    world.public(),
                    condition,
                    source,
                    supplied,
                    fitted.expression if fitted else None,
                    separation_table,
                )
                decoding_seed = config["decoding_seed_base"] + 100 * family_index + 10 * seed_index + (2 if supplied else 0)
                output, call = client.generate(
                    prompt,
                    world_id=world.world_id,
                    world_seed=world_seed,
                    decoding_seed=decoding_seed,
                    representation_hash=supplied.structural_hash if supplied else "",
                )
                row: dict[str, Any] = {
                    "family": family,
                    "world_id": world.world_id,
                    "world_seed": world_seed,
                    "decoding_seed": decoding_seed,
                    "proposal_source": source.value,
                    "prompt_hash": call.prompt_hash,
                    "prompt_tokens": call.prompt_tokens,
                    "completion_tokens": call.completion_tokens,
                    "latency_seconds": call.latency_seconds,
                    "parse_valid": False,
                    "parser_version": "theory-json-parser-v2",
                    "validated_jump": False,
                }
                try:
                    public_to_internal = {public: internal for internal, public in world.variable_names}
                    payload = extract_json_object(output)
                    if supplied is not None:
                        payload["representation"] = supplied.canonical_dict()
                    if fitted is not None:
                        payload["expression"] = fitted.expression.tree
                    theory = parse_theory(payload, public_to_internal)
                    row["parse_valid"] = True
                    if supplied is not None:
                        theory = replace(theory, representation=supplied)
                    commitment = freeze_theory(world, theory)
                    gates = evaluate_executable(world, theory, commitment)
                    row.update(asdict(gates))
                    row["validated_jump"] = gates.validated_jump
                    row["representation_hash"] = theory.representation.structural_hash
                    row["expression_json"] = theory.expression.canonical_json
                    row["selected_intervention_ids"] = list(theory.selected_intervention_ids)
                except (KeyError, TypeError, ValueError, OverflowError) as exc:
                    row["error_type"] = type(exc).__name__
                    row["error"] = str(exc)
                rows.append(row)
                with result_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, sort_keys=True) + "\n")

    by_source: dict[str, dict[str, float | int]] = {}
    for source in sources:
        subset = [row for row in rows if row["proposal_source"] == source.value]
        by_source[source.value] = {
            "n": len(subset),
            "parse_rate": sum(bool(row["parse_valid"]) for row in subset) / len(subset),
            "success_rate": sum(bool(row["validated_jump"]) for row in subset) / len(subset),
            "mean_tokens": sum(int(row["prompt_tokens"]) + int(row["completion_tokens"]) for row in subset) / len(subset),
        }
    summary = {"model_manifest": asdict(manifest), "by_source": by_source}
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
