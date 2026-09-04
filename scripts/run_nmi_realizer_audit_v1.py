#!/usr/bin/env python3
"""Run the frozen, inference-free motif-realizer dependency audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from abductive_jump.compositional_experiment import (
    _fixed_candidates,
    _parse_self_plans,
    _world,
)
from abductive_jump.compositional_worlds import (
    HELD_OUT_FAMILY,
    generate_heldout_world,
)
from abductive_jump.fair_interface_experiment import _seeds
from abductive_jump.realizer_audit import (
    ALIGNED,
    MASK_PREFIX,
    MOTIF_DISABLED,
    REALIZER_SIGNATURES,
    ROLE_BLIND,
    evaluate_counterfactual,
    representation_from_json,
)
from abductive_jump.worlds import generate_world

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arrow_table(rows: list[dict[str, Any]]) -> pa.Table:
    columns = sorted({key for row in rows for key in row})
    return pa.Table.from_pylist([{key: row.get(key) for key in columns} for row in rows])


def load_protocol(path: Path) -> dict[str, Any]:
    protocol = json.loads(path.read_text())
    if protocol["status"] != "frozen_before_replay":
        raise ValueError("realizer audit protocol is not frozen")
    for relative, expected in protocol["input_sha256"].items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"input differs from frozen protocol: {relative}")
    for relative, expected in protocol["code_sha256"].items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"code differs from frozen protocol: {relative}")
    return protocol


def world_for(family: str, seed: int) -> Any:
    if family == HELD_OUT_FAMILY:
        return generate_heldout_world(seed)
    return generate_world(family, seed)


def historical_candidates(path: Path) -> list[dict[str, Any]]:
    rows = pq.read_table(path).to_pylist()
    accepted_conditions = {
        "C3_GENERIC_COMPOSITION": "C3",
        "C_RAND_RANDOM_PRIMITIVES": "C_rand",
    }
    candidates = []
    for row in rows:
        if bool(row["no_jump"]) or row["condition"] not in accepted_conditions:
            continue
        candidates.append(
            {
                "source": accepted_conditions[str(row["condition"])],
                "family": str(row["family"]),
                "world_seed": int(row["world_seed"]),
                "world_id": str(row["world_id"]),
                "slot": int(row["slot"]),
                "proposal_executable": True,
                "representation": representation_from_json(str(row["representation_json"])),
                "archived": row,
            }
        )
    return candidates


def fair_candidates(
    config_path: Path, calls_path: Path, candidate_path: Path
) -> list[dict[str, Any]]:
    config = json.loads(config_path.read_text())
    calls = [json.loads(line) for line in calls_path.read_text().splitlines()]
    by_call = {(str(row["world_id"]), int(row["decoding_seed"])): row for row in calls}
    if len(by_call) != len(calls):
        raise ValueError("duplicate fair-interface call records")
    archived = {
        (str(row["family"]), int(row["world_seed"]), int(row["slot"])): row
        for row in pq.read_table(candidate_path).to_pylist()
    }
    candidates = []
    for family in config["families"]:
        for seed in config["world_seeds"]:
            world = _world(config, str(family), int(seed))
            for slot in range(int(config["candidate_slots"])):
                _, final_seed = _seeds(config, str(family), int(seed), slot)
                final = by_call[(world.world_id, final_seed)]
                evaluated, _ = _parse_self_plans(
                    world,
                    str(final["full_output"]),
                    int(config["search_seed_base"]) + int(seed) * 101 + slot * 1000,
                    required_plans=int(config["self_plans_per_slot"]),
                )
                selected = max(
                    evaluated,
                    key=lambda item: (
                        item.score,
                        item.candidate.representation.structural_hash,
                    ),
                    default=_fixed_candidates(world, 1)[0],
                )
                candidates.append(
                    {
                        "source": "DeepSeek_grammar",
                        "family": str(family),
                        "world_seed": int(seed),
                        "world_id": world.world_id,
                        "slot": slot,
                        "proposal_executable": bool(evaluated),
                        "representation": selected.candidate.representation,
                        "archived": archived[(str(family), int(seed), slot)],
                        "gate_thresholds": dict(config["gate_thresholds"]),
                    }
                )
    return candidates


def verify_aligned(row: dict[str, Any], evaluated: dict[str, Any]) -> list[str]:
    archived = row["archived"]
    prefix = f"{row['source']}:{row['world_id']}:{row['slot']}"
    mismatches = []
    fields = (
        "j0",
        "j1",
        "j2",
        "j3",
        "j4",
        "j5",
        "candidate_obs_loss",
        "oracle_cf_loss",
        "candidate_cf_loss",
        "oracle_falsification_loss",
        "candidate_falsification_loss",
    )
    for field in fields:
        expected = archived[field]
        actual = evaluated[field]
        if isinstance(expected, float):
            if abs(float(expected) - float(actual)) > 1e-10:
                mismatches.append(f"{prefix}:{field}")
        elif expected != actual:
            mismatches.append(f"{prefix}:{field}")
    archived_jump = bool(archived["validated_jump"])
    if archived_jump != bool(evaluated["counterfactual_validated_jump"]):
        mismatches.append(f"{prefix}:validated_jump")
    return mismatches


def run(protocol_path: Path, output_dir: Path) -> dict[str, Any]:
    protocol = load_protocol(protocol_path)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = protocol["inputs"]
    candidates = historical_candidates(ROOT / inputs["historical_candidates"])
    candidates.extend(
        fair_candidates(
            ROOT / inputs["fair_config"],
            ROOT / inputs["fair_calls"],
            ROOT / inputs["fair_candidates"],
        )
    )
    policies = [ALIGNED, MOTIF_DISABLED, ROLE_BLIND]
    policies.extend(f"{MASK_PREFIX}{signature}" for signature in REALIZER_SIGNATURES)
    if policies != protocol["policies"]:
        raise ValueError("implemented policy order differs from frozen protocol")

    result_rows: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for candidate in candidates:
        world = world_for(candidate["family"], candidate["world_seed"])
        if world.world_id != candidate["world_id"]:
            raise ValueError(
                f"world reconstruction mismatch: {candidate['source']}:{candidate['world_id']}"
            )
        for policy in policies:
            evaluated = evaluate_counterfactual(
                world,
                candidate["representation"],
                policy,
                proposal_executable=bool(candidate["proposal_executable"]),
                gate_thresholds=candidate.get("gate_thresholds"),
            )
            evaluated.update(
                {
                    "source": candidate["source"],
                    "family": candidate["family"],
                    "world_seed": candidate["world_seed"],
                    "world_id": candidate["world_id"],
                    "slot": candidate["slot"],
                }
            )
            result_rows.append(evaluated)
            if policy == ALIGNED:
                mismatches.extend(verify_aligned(candidate, evaluated))

    grouped: dict[tuple[str, str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in result_rows:
        grouped[
            (
                str(row["source"]),
                str(row["policy"]),
                str(row["family"]),
                int(row["world_seed"]),
            )
        ].append(row)
    world_rows = []
    for (source, policy, family, seed), rows in sorted(grouped.items()):
        world_rows.append(
            {
                "source": source,
                "policy": policy,
                "family": family,
                "world_seed": seed,
                "world_id": str(rows[0]["world_id"]),
                "successful": any(bool(row["counterfactual_validated_jump"]) for row in rows),
                "validated_candidates": sum(
                    bool(row["counterfactual_validated_jump"]) for row in rows
                ),
            }
        )

    pq.write_table(
        arrow_table(result_rows), output_dir / "candidate_results.parquet", compression="zstd"
    )
    pq.write_table(
        arrow_table(world_rows), output_dir / "world_results.parquet", compression="zstd"
    )
    counts: dict[str, dict[str, dict[str, float | int]]] = defaultdict(dict)
    for source in sorted({str(row["source"]) for row in world_rows}):
        for policy in policies:
            selected = [
                row for row in world_rows if row["source"] == source and row["policy"] == policy
            ]
            success = sum(bool(row["successful"]) for row in selected)
            counts[source][policy] = {
                "worlds": len(selected),
                "successes": success,
                "jsr": success / len(selected),
            }
    summary = {
        "schema_version": "nmi-realizer-audit-summary-v1",
        "analysis": "counterfactual replay of archived candidates; zero model calls",
        "protocol_sha256": digest(protocol_path),
        "candidate_policy_rows": len(result_rows),
        "world_policy_rows": len(world_rows),
        "aligned_replay_mismatches": len(mismatches),
        "counts": counts,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    validation = {
        "status": "complete_verified" if not mismatches else "mismatch",
        "zero_model_calls": True,
        "aligned_replay_mismatch_count": len(mismatches),
        "aligned_replay_mismatches": mismatches,
        "candidate_results_sha256": digest(output_dir / "candidate_results.parquet"),
        "world_results_sha256": digest(output_dir / "world_results.parquet"),
        "summary_sha256": digest(output_dir / "summary.json"),
    }
    (output_dir / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n"
    )
    if mismatches:
        raise ValueError(f"aligned replay produced {len(mismatches)} mismatches")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=ROOT / "experiments" / "nmi_realizer_audit_v1" / "protocol.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments" / "nmi_realizer_audit_v1" / "results",
    )
    args = parser.parse_args()
    print(json.dumps(run(args.protocol, args.output_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
