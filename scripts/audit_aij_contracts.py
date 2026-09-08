"""Offline audit of B1's recorded interface and the public variable-name boundary.

Uses frozen AJ5/CJ5 worlds and existing call ledgers; never invokes a model.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

from abductive_jump.compositional_worlds import HELD_OUT_FAMILY, generate_heldout_world
from abductive_jump.conditions import Condition, _public_payload
from abductive_jump.executable import allowed_variables
from abductive_jump.llm import extract_json_object
from abductive_jump.proposals import apply_mutation_plan
from abductive_jump.realization import fit_representation
from abductive_jump.worlds import FAMILIES, generate_world

ROOT = Path(__file__).resolve().parents[1]
INPUTS = set()


def read_rows(path):
    INPUTS.add(path)
    return pq.read_table(ROOT / path).to_pylist()


def world_for(family, seed, no_jump):
    if family == HELD_OUT_FAMILY:
        return generate_heldout_world(seed, no_jump=no_jump)
    return generate_world(family, seed, no_jump=no_jump)


def public_name_check(world):
    payload = _public_payload(world.public())
    public_rows = payload["observations"] + list(payload["prospective_intervention_queries_without_outcomes"])
    visible = {name for case in public_rows for name in case["inputs"]}
    visible.update(name for case in public_rows for name in case["intervention"])
    observation_names = {name for case in payload["observations"] for name in case["inputs"]}
    aliases = dict(world.variable_names)
    allowed = {aliases.get(name, name) for name in allowed_variables(world)}
    hidden_only = allowed - visible
    assert not hidden_only, (world.world_id, sorted(hidden_only))
    assert all("outcome" not in case for case in payload["prospective_intervention_queries_without_outcomes"])
    assert "falsification" not in payload
    return {"allowlist_names": sorted(allowed), "public_input_action_names": sorted(visible),
            "names_not_in_observations": sorted(allowed - observation_names)}


def audit_names():
    result = []
    for source in ("artifacts/candidate_theories.parquet", "artifacts/compositional_candidates.parquet"):
        keys = sorted({(r["family"], r["world_seed"], r["no_jump"]) for r in read_rows(source)})
        only_action = []
        families = Counter()
        for family, seed, no_jump in keys:
            world = world_for(family, seed, no_jump)
            check = public_name_check(world)
            families[family] += 1
            if check["names_not_in_observations"]:
                only_action.append({"world_id": world.world_id, **check})
        result.append({"source": source, "worlds": len(keys), "families": dict(families),
                       "hidden_only_allowlist_names": 0,
                       "worlds_with_allowed_names_only_in_public_actions": only_action})
    return result


def audit_b1():
    summaries = []
    for population in ("jump", "control"):
        folder = f"artifacts/confirmatory/primary-{population}"
        result_path = folder + "/candidate_theories.parquet"
        ledger_path = folder + "/llm_calls.jsonl"
        INPUTS.add(ledger_path)
        config_path = f"configs/confirmatory-primary-{population}.json"
        INPUTS.add(config_path)
        config = json.loads((ROOT / config_path).read_text())
        rows = [r for r in read_rows(result_path) if r["condition"] == "B1_SAMPLE_MATCHED"]
        calls = {}
        with (ROOT / ledger_path).open() as stream:
            for line, raw in enumerate(stream, 1):
                call = json.loads(raw)
                if call["condition"] == "B1_SAMPLE_MATCHED" and not call["representation_hash"]:
                    key = (call["world_id"], call["prompt_hash"], call["decoding_seed"])
                    assert key not in calls, key
                    calls[key] = (line, call)
        assert len(calls) == len(rows)
        counts = Counter()
        example = None
        for row in rows:
            decoding_seed = (config["decoding_seed_base"]
                             + list(Condition).index(Condition.B1_SAMPLE_MATCHED) * 10_000_000
                             + FAMILIES.index(row["family"]) * 100_000
                             + row["world_seed"] * 100 + row["slot"] * 2)
            line, call = calls[(row["world_id"], row["phase_one_prompt_hash"], decoding_seed)]
            messages = json.loads(call["full_prompt_json"])
            user = next(m["content"] for m in messages if m["role"] == "user")
            contract = json.loads(next(s.removeprefix("Output schema: ") for s in user.splitlines()
                                       if s.startswith("Output schema: ")))
            assert "mutation_plan" in contract and "representation" not in contract
            counts["mutation_plan_prompt_contract"] += 1
            world = world_for(row["family"], row["world_seed"], row["no_jump"])
            representation = world.incumbent
            phase_one_valid = False
            parsed = None
            ancestry = ()
            try:
                parsed = extract_json_object(call["full_output"])
                counts["json_extractable"] += 1
                counts["has_mutation_plan"] += int("mutation_plan" in parsed)
                proposal = apply_mutation_plan(world.incumbent, parsed["mutation_plan"], call["decoding_seed"])
                representation = proposal.representation
                if representation.validate():
                    raise ValueError("invalid phase-one graph")
                phase_one_valid = True
                ancestry = proposal.operators
            except (KeyError, TypeError, ValueError, OverflowError):
                representation = world.incumbent
            assert phase_one_valid == row["phase_one_valid"], (row["world_id"], row["slot"])
            counts["phase_one_valid"] += int(phase_one_valid)
            try:
                fit_representation(world.public(), representation)
            except (KeyError, TypeError, ValueError, OverflowError):
                representation = world.incumbent
                ancestry = ()
            assert representation.structural_hash == row["representation_hash"], (row["world_id"], row["slot"])
            assert list(ancestry) == row["mutation_ancestry"]
            counts["final_representation_hash_matches"] += 1
            if example is None and phase_one_valid:
                example = {"ledger": ledger_path, "line": line, "world_id": row["world_id"],
                           "slot": row["slot"], "decoding_seed": call["decoding_seed"],
                           "prompt_hash": call["prompt_hash"], "raw_mutation_plan": parsed["mutation_plan"],
                           "representation_hash": representation.structural_hash}
        summaries.append({"population": population, "candidate_rows": len(rows),
                          "counts": dict(counts), "example": example})
    return summaries


def main():
    report = {"analysis": "post-hoc interface and metadata audit; no model calls",
              "b1": audit_b1(), "variable_names": audit_names()}
    INPUTS.update(str(p.relative_to(ROOT)) for p in (ROOT / "src/abductive_jump").glob("*.py"))
    INPUTS.update({"scripts/audit_aij_contracts.py", "configs/confirmatory-primary-jump.json",
                   "configs/confirmatory-primary-control.json"})
    report["source_sha256"] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sorted(INPUTS)}
    (ROOT / "reports/AIJ_CONTRACT_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "source_sha256"}, indent=2))


if __name__ == "__main__":
    main()
