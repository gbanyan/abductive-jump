"""Recompute gate attrition and an inference-free C3 component ablation."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from abductive_jump.compositional_worlds import HELD_OUT_FAMILY, generate_heldout_world
from abductive_jump.executable import evaluate_executable, freeze_theory, parse_theory
from abductive_jump.gates import GateThresholds
from abductive_jump.worlds import generate_world

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def _world(family: str, seed: int, no_jump: bool):
    if family == HELD_OUT_FAMILY:
        return generate_heldout_world(seed, no_jump=no_jump)
    return generate_world(family, seed, no_jump=no_jump)


def _gate_attrition() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for filename, study in (
        ("candidate_theories.parquet", "AJ5"),
        ("compositional_candidates.parquet", "CJ5"),
    ):
        source = pq.read_table(ARTIFACTS / filename).to_pylist()
        for condition in sorted({str(row["condition"]) for row in source}):
            for no_jump in (False, True):
                subset = [
                    row
                    for row in source
                    if row["condition"] == condition and bool(row["no_jump"]) is no_jump
                ]
                if not subset:
                    continue
                cumulative = [
                    sum(all(bool(row[f"j{i}"]) for i in range(gate + 1)) for row in subset)
                    for gate in range(6)
                ]
                rows.append(
                    {
                        "study": study,
                        "condition": condition,
                        "population": "control" if no_jump else "jump",
                        "candidates": len(subset),
                        "phase_one_valid": sum(bool(row["phase_one_valid"]) for row in subset),
                        "phase_two_valid": sum(bool(row["phase_two_valid"]) for row in subset),
                        **{f"through_j{i}": cumulative[i] for i in range(6)},
                    }
                )
    return rows


def _c3_without_llm() -> dict[str, object]:
    source = pq.read_table(ARTIFACTS / "compositional_candidates.parquet").to_pylist()
    source = [row for row in source if row["condition"] == "C3_GENERIC_COMPOSITION"]
    candidate_results: list[dict[str, object]] = []
    for row in source:
        world = _world(str(row["family"]), int(row["world_seed"]), bool(row["no_jump"]))
        payload = {
            "representation": json.loads(str(row["representation_json"])),
            "expression": json.loads(str(row["expression_json"])),
            "explanation": "",
            "selected_intervention_ids": [str(row["exact_designer_intervention_id"])],
        }
        theory = parse_theory(
            payload,
            {public: internal for internal, public in world.variable_names},
        )
        result = evaluate_executable(
            world,
            theory,
            freeze_theory(world, theory),
            GateThresholds(),
        )
        candidate_results.append(
            {
                "world_id": row["world_id"],
                "no_jump": bool(row["no_jump"]),
                "validated_jump": result.validated_jump,
                "matches_archived": result.validated_jump == bool(row["validated_jump"]),
            }
        )
    worlds: dict[tuple[str, bool], bool] = {}
    for row in candidate_results:
        key = (str(row["world_id"]), bool(row["no_jump"]))
        worlds[key] = worlds.get(key, False) or bool(row["validated_jump"])
    jump = [value for (world_id, no_jump), value in worlds.items() if not no_jump]
    control = [value for (world_id, no_jump), value in worlds.items() if no_jump]
    return {
        "analysis": "post-hoc deterministic component audit; no new model inference",
        "intervention": "replace both Phi-4 calls with a valid empty explanation while preserving the archived deterministic representation, fit and maximum-separation intervention",
        "scientific_fields_from_llm": [],
        "llm_field_retained": "explanation (not used by J0-J5)",
        "candidate_rows": len(candidate_results),
        "candidate_gate_matches": sum(bool(row["matches_archived"]) for row in candidate_results),
        "jump_worlds": len(jump),
        "jump_successes": sum(jump),
        "control_worlds": len(control),
        "false_jumps": sum(control),
    }


def _self_plan_audit() -> dict[str, object]:
    paths = sorted(ARTIFACTS.glob("compositional/confirmatory-*/llm_self_plans.parquet"))
    rows = [row for path in paths for row in pq.read_table(path).to_pylist()]
    errors = Counter(str(row.get("error", "")) for row in rows if not row.get("valid"))
    return {
        "confirmatory_plan_records": len(rows),
        "valid_plan_records": sum(bool(row.get("valid")) for row in rows),
        "error_counts": dict(errors),
        "interpretation": "C_self is an interface-validity result, not evidence of conceptual proposal failure.",
    }


def main() -> None:
    attrition = _gate_attrition()
    pq.write_table(
        pa.Table.from_pylist(attrition),
        ARTIFACTS / "nmi_gate_attrition.parquet",
        compression="zstd",
    )
    audit = {
        "c3_without_llm": _c3_without_llm(),
        "c_self": _self_plan_audit(),
    }
    (ARTIFACTS / "nmi_component_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
