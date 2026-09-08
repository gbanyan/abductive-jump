"""Version 1.0.0: adapt one frozen CJ5 trace into an explicitly post-hoc record.

No model calls and no search rerun. Requires the raw ledger from the evidence release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

import pyarrow.parquet as pq

from abductive_jump.compositional_realization import fit_composed_representation
from abductive_jump.compositional_worlds import generate_heldout_world
from abductive_jump.executable import evaluate_executable, freeze_theory, parse_theory
from abductive_jump.gates import GateThresholds
from abductive_jump.llm import extract_json_object

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
OUTPUT = ROOT / "manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json"
LEDGER = "artifacts/compositional/confirmatory-heldout/llm_calls.jsonl"
AGGREGATE = "artifacts/compositional_candidates.parquet"
RAW_RESULTS = "artifacts/compositional/confirmatory-heldout/candidate_results.parquet"
RUNNER = "src/abductive_jump/compositional_experiment.py"
EVALUATOR = "src/abductive_jump/executable.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(basis, value, source):
    return {"basis": basis, "value": value, "source": source}


def build_record(root=ROOT):
    rows = pq.read_table(root / AGGREGATE).to_pylist()
    row = next(r for r in rows if r["condition"] == "C3_GENERIC_COMPOSITION"
               and r["world_seed"] == 40000 and not r["no_jump"] and r["slot"] == 0)
    runtime = next(r for r in pq.read_table(root / RAW_RESULTS).to_pylist()
                   if r["condition"] == row["condition"] and r["world_id"] == row["world_id"]
                   and r["slot"] == row["slot"])
    calls = []
    with (root / LEDGER).open() as stream:
        for line, text in enumerate(stream, 1):
            call = json.loads(text)
            if (call["world_id"] == row["world_id"]
                    and call["condition"] == row["condition"]
                    and call["representation_hash"] == row["representation_hash"]):
                calls.append({"basis": "runtime_recorded", "ledger_path": LEDGER,
                              "line": line, "decoding_seed": call["decoding_seed"],
                              "prompt_hash": call["prompt_hash"], "output": call["full_output"],
                              "parsed": extract_json_object(call["full_output"])})
    calls.sort(key=lambda c: c["decoding_seed"])
    if len(calls) != 2:
        raise ValueError("Expected exactly the two archived calls for this candidate")
    world = generate_heldout_world(40000)
    payload = dict(calls[1]["parsed"])
    payload.update(representation=json.loads(row["representation_json"]),
                   expression=json.loads(row["expression_json"]),
                   selected_intervention_ids=[row["exact_designer_intervention_id"]])
    theory = parse_theory(payload, {v: k for k, v in world.variable_names})
    if theory.theory_hash != runtime["theory_hash"]:
        raise ValueError("Reconstructed theory does not match the runtime hash")
    fit = fit_composed_representation(world.public(), theory.representation)
    if fit.expression.tree != payload["expression"]:
        raise ValueError("Archived public expression does not match deterministic refit")
    commitment = freeze_theory(world, theory)
    result = evaluate_executable(world, theory, commitment, GateThresholds())
    gates = {f"j{i}": getattr(result, f"j{i}") for i in range(6)}
    if gates != {key: runtime[key] for key in gates}:
        raise ValueError("Reconstructed gates do not match runtime results")
    deleted = replace(theory, explanation="")
    replay_commitment = freeze_theory(world, deleted)
    replay_result = evaluate_executable(world, deleted, replay_commitment, GateThresholds())
    replay_gates = {key: getattr(replay_result, key) for key in gates}
    def commitment_value(c):
        value = asdict(c)
        value.pop("frozen_at_utc")  # Never present a new timestamp as an original event.
        return value
    def field(value, source, producer="deterministic_component", read=True,
              basis="posthoc_reconstruction"):
        return {"producer": producer, "basis": basis, "source": source,
                "value": value, "read_by_gate": read}
    steps = [
        ("Search and diversity-aware ranking retain three representations; realization and fitting also occur inside search", RUNNER + ":_condition_candidates"),
        ("Realize and refit retained graph, then compute public prediction table and maximum-separation action", RUNNER + ":run_world_condition candidate loop"),
        ("Call phase one and parse JSON only for a diagnostic validity flag", RUNNER + ":phase_one_output"),
        ("Call phase two with supplied representation, fitted expression and prediction table", RUNNER + ":phase_two_prompt"),
        ("Extract phase-two JSON; overwrite representation, expression and selected_intervention_ids", RUNNER + ":payload overwrites"),
        ("Parse graph and translate public expression variables to internal names; retain explanation", EVALUATOR + ":parse_theory"),
        ("Freeze theory and prediction before evaluate_executable computes hidden losses", RUNNER + ":evaluate_executable call"),
    ]
    sources = [AGGREGATE, RAW_RESULTS, LEDGER, RUNNER, EVALUATOR,
               "src/abductive_jump/compositional_realization.py",
               "src/abductive_jump/composition_search.py", "src/abductive_jump/realization.py",
               "src/abductive_jump/compositional_worlds.py", "src/abductive_jump/expressions.py",
               "src/abductive_jump/representation.py", "src/abductive_jump/gates.py",
               "schemas/aij-evidence-record-v1.schema.json", "scripts/build_aij_evidence_record.py",
               "scripts/validate_aij_evidence_record.py", "uv.lock"]
    sources = sorted(set(sources) | {
        str(path.relative_to(root)) for path in (root / "src/abductive_jump").glob("*.py")
    })
    return {
        "schema_version": VERSION, "record_kind": "mixed_archival_and_reconstructed_evidence",
        "candidate": {k: row[k] for k in ("world_id", "condition", "world_seed", "slot")},
        "sources": {p: sha(root / p) for p in sources}, "raw_calls": calls,
        "transformations": [{"order": i, "operation": op, "basis": "posthoc_code_inspection",
                             "source": src} for i, (op, src) in enumerate(steps, 1)],
        "fields": {
            "representation": field(theory.representation.canonical_dict(), AGGREGATE + ":representation_json"),
            "expression": field(theory.expression.tree, AGGREGATE + ":expression_json; parse_theory variable translation"),
            "parameters": field(list(fit.coefficients), "compositional_realization:fit_composed_representation"),
            "ranking": field({"slot": row["slot"], "policy": "diversity-aware deterministic selection",
                              "ancestry": row["mutation_ancestry"]}, RUNNER + ":_condition_candidates",
                             read=False, basis="posthoc_code_inspection"),
            "action": field(list(theory.selected_intervention_ids), RAW_RESULTS + ":exact_designer_intervention_id",
                            basis="runtime_recorded"),
            "prediction": field(list(commitment.intervention_predictions), EVALUATOR + ":freeze_theory"),
            "explanation": field(theory.explanation, LEDGER + ":line " + str(calls[1]["line"]),
                                 producer="model", read=False, basis="runtime_recorded"),
        },
        "commitment": {
            "archived_theory_hash": runtime["theory_hash"],
            "reconstructed": evidence("posthoc_reconstruction", commitment_value(commitment), EVALUATOR + ":freeze_theory"),
            "original_timestamp": evidence("unavailable", None, "Not persisted in the archived candidate result or call ledger"),
            "original_digest": evidence("unavailable", None, "Not persisted in the archived candidate result"),
            "ordering": evidence("posthoc_code_inspection", "fit -> calls -> overwrite -> parse -> freeze -> hidden losses",
                                 RUNNER + ":589; control flow, not an independently timestamped reveal event"),
        },
        "evaluation": evidence("runtime_recorded", {**gates, "validated_jump": runtime["validated_jump"]}, RAW_RESULTS),
        "replay": evidence("posthoc_reconstruction", {
            "replacement": "Remove both model responses; use an empty explanation and archived deterministic scientific fields",
            "fixed": ["representation", "expression", "parameters", "selected slot", "action", "world", "thresholds"],
            "recomputed": ["theory hash", "prediction", "commitment digest", "all six gates"],
            "refit_in_replay": False, "refit_as_separate_integrity_check": True,
            "rerank": False, "reselect_action": False, "adaptive_research": False, "model_calls": 0,
            "commitment": commitment_value(replay_commitment), "gates": replay_gates,
            "gates_unchanged": gates == replay_gates,
            "validated_jump": replay_result.validated_jump,
            "theory_hash_changed": deleted.theory_hash != theory.theory_hash,
            "interpretation": "Explanation participates in hashing but not gate content; hash equality is not verdict equality",
        }, "scripts/build_aij_evidence_record.py:build_record"),
        "supplied_knowledge": evidence("posthoc_reconstruction", {
            "signature": fit.structural_signature, "basis_names": list(fit.basis_names),
            "coefficients": list(fit.coefficients), "origin": "Hand-authored triadic-product basis triggered by a compositionally constructed graph",
            "novelty": "Origin records alone do not establish scientific novelty",
        }, "src/abductive_jump/compositional_realization.py:_motif and fit_composed_representation"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    record = build_record()
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(f"Record {VERSION}: {args.output}; no model inference")


if __name__ == "__main__":
    main()
