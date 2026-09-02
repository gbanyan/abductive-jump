from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .compositional_worlds import HELD_OUT_FAMILY
from .conditions import Condition
from .worlds import FAMILIES

BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20_260_902


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def _wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return float("nan"), float("nan")
    rate = successes / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(
        rate * (1 - rate) / total + z * z / (4 * total * total)
    ) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def _lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, int, str], int]:
    return {
        (str(row["family"]), int(row["world_seed"]), str(row["condition"])): int(
            bool(row["condition_success"])
        )
        for row in rows
    }


def _paired_effect(
    rows: list[dict[str, Any]], left: str, right: str, *, stratified: bool
) -> dict[str, float]:
    lookup = _lookup(rows)
    families = sorted({str(row["family"]) for row in rows})
    seeds = {
        family: sorted({int(row["world_seed"]) for row in rows if row["family"] == family})
        for family in families
    }

    def estimate(draws: dict[str, list[int]]) -> float:
        values = []
        for family in families:
            differences = [
                lookup[(family, seed, left)] - lookup[(family, seed, right)]
                for seed in draws[family]
            ]
            values.append(sum(differences) / len(differences))
        return sum(values) / len(values) if stratified else sum(
            lookup[(family, seed, left)] - lookup[(family, seed, right)]
            for family in families
            for seed in draws[family]
        ) / sum(len(draws[family]) for family in families)

    observed = estimate(seeds)
    rng = random.Random(BOOTSTRAP_SEED ^ sum(ord(char) for char in left + right))
    samples = []
    for _ in range(BOOTSTRAP_REPLICATES):
        draws = {
            family: [rng.choice(seeds[family]) for _ in seeds[family]]
            for family in families
        }
        samples.append(estimate(draws))

    paired_differences = [
        lookup[(family, seed, left)] - lookup[(family, seed, right)]
        for family in families
        for seed in seeds[family]
    ]
    nonzero = [value for value in paired_differences if value]
    permutation_rng = random.Random(BOOTSTRAP_SEED ^ sum(ord(char) for char in right + left))
    if not nonzero:
        p_value = 1.0
    elif len(nonzero) <= 20:
        extreme = 0
        for mask in range(1 << len(nonzero)):
            permuted = sum(
                value if mask & (1 << index) else -value
                for index, value in enumerate(nonzero)
            ) / len(paired_differences)
            extreme += permuted >= observed - 1e-15
        p_value = extreme / (1 << len(nonzero))
    else:
        extreme = 0
        for _ in range(BOOTSTRAP_REPLICATES):
            permuted = sum(
                value if permutation_rng.random() < 0.5 else -value
                for value in nonzero
            ) / len(paired_differences)
            extreme += permuted >= observed - 1e-15
        p_value = (extreme + 1) / (BOOTSTRAP_REPLICATES + 1)
    return {
        "estimate": observed,
        "ci_low": _quantile(samples, 0.025),
        "ci_high": _quantile(samples, 0.975),
        "p_one_sided": p_value,
    }


def _holm(rows: list[dict[str, Any]]) -> None:
    ordered = sorted(rows, key=lambda row: float(row["p_one_sided"]))
    running = 0.0
    for index, row in enumerate(ordered):
        running = max(
            running,
            min(1.0, (len(ordered) - index) * float(row["p_one_sided"])),
        )
        row["p_holm"] = running


def _rho_bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    lookup = _lookup(rows)
    families = list(FAMILIES)
    seeds = {
        family: sorted({int(row["world_seed"]) for row in rows if row["family"] == family})
        for family in families
    }

    def rate(condition: str, draws: dict[str, list[int]]) -> float:
        return sum(
            sum(lookup[(family, seed, condition)] for seed in draws[family])
            / len(draws[family])
            for family in families
        ) / len(families)

    c0 = rate(Condition.C0_FIXED_SPACE.value, seeds)
    c1 = rate(Condition.C1_ATOMIC_HIGH_LEVEL.value, seeds)
    c3 = rate(Condition.C3_GENERIC_COMPOSITION.value, seeds)
    observed = (c3 - c0) / (c1 - c0) if c1 > c0 else None
    rng = random.Random(BOOTSTRAP_SEED ^ 0xC3C1)
    samples = []
    for _ in range(BOOTSTRAP_REPLICATES):
        draws = {
            family: [rng.choice(seeds[family]) for _ in seeds[family]]
            for family in families
        }
        b0 = rate(Condition.C0_FIXED_SPACE.value, draws)
        b1 = rate(Condition.C1_ATOMIC_HIGH_LEVEL.value, draws)
        b3 = rate(Condition.C3_GENERIC_COMPOSITION.value, draws)
        if b1 > b0:
            samples.append((b3 - b0) / (b1 - b0))
    return {
        "rho_j": observed,
        "ci_low": _quantile(samples, 0.025) if samples else None,
        "ci_high": _quantile(samples, 0.975) if samples else None,
        "defined_bootstrap_replicates": len(samples),
    }


def _svg(path: Path, title: str, body: str, *, width: int = 1000, height: int = 580) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<rect width="100%" height="100%" fill="#faf8f3"/>'
        f'<text x="48" y="52" font-family="sans-serif" font-size="25" font-weight="700" fill="#172121">{title}</text>'
        + body
        + "</svg>\n"
    )


def _bars(path: Path, title: str, labels: list[str], values: list[float], color: str) -> None:
    plot_x, plot_y, plot_w, plot_h = 75, 95, 860, 390
    gap = plot_w / len(values)
    parts = [
        f'<line x1="{plot_x}" y1="{plot_y + plot_h}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h}" stroke="#172121"/>'
    ]
    maximum = max(values) or 1.0
    scale = max(1.0, maximum)
    for index, (label, value) in enumerate(zip(labels, values)):
        width = gap * 0.6
        x = plot_x + index * gap + gap * 0.2
        height = value / scale * plot_h
        y = plot_y + plot_h - height
        parts.extend(
            (
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{max(1, height):.1f}" rx="4" fill="{color}"/>',
                f'<text x="{x + width / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-family="sans-serif" font-size="15">{value:.3f}</text>',
                f'<text x="{x + width / 2:.1f}" y="{plot_y + plot_h + 28}" text-anchor="middle" font-family="sans-serif" font-size="13">{label}</text>',
            )
        )
    _svg(path, title, "".join(parts))


def _read_runs(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base = root / "artifacts" / "compositional"
    names = (
        "confirmatory-existing",
        "confirmatory-existing-control",
        "confirmatory-heldout",
        "confirmatory-heldout-control",
    )
    worlds = [
        row
        for name in names
        for row in pq.read_table(base / name / "world_results.parquet").to_pylist()
    ]
    candidates = pq.read_table(root / "artifacts" / "compositional_candidates.parquet").to_pylist()
    return worlds, candidates


def run(root: Path) -> dict[str, Any]:
    artifacts = root / "artifacts"
    figures = root / "reports" / "figures" / "compositional"
    worlds, candidates = _read_runs(root)
    existing_jump = [row for row in worlds if row["family"] in FAMILIES and not row["no_jump"]]
    existing_control = [row for row in worlds if row["family"] in FAMILIES and row["no_jump"]]
    heldout_jump = [row for row in worlds if row["family"] == HELD_OUT_FAMILY and not row["no_jump"]]
    heldout_control = [row for row in worlds if row["family"] == HELD_OUT_FAMILY and row["no_jump"]]
    conditions = (
        Condition.C0_FIXED_SPACE.value,
        Condition.C1_ATOMIC_HIGH_LEVEL.value,
        Condition.C2_GENERIC_DEPTH_1.value,
        Condition.C3_GENERIC_COMPOSITION.value,
        Condition.C_SELF_LLM_COMPOSITION.value,
        Condition.C_RAND_RANDOM_PRIMITIVES.value,
        Condition.C5_ORACLE_REPRESENTATION.value,
    )

    summaries = []
    for condition in conditions:
        jump_rows = [row for row in existing_jump if row["condition"] == condition]
        control_rows = [row for row in existing_control if row["condition"] == condition]
        held_rows = [row for row in heldout_jump if row["condition"] == condition]
        held_controls = [row for row in heldout_control if row["condition"] == condition]
        candidate_jump = [
            row
            for row in candidates
            if row["condition"] == condition and not row["no_jump"] and row["family"] in FAMILIES
        ]
        accepted = [
            row
            for row in candidate_jump
            if all(bool(row.get(gate)) for gate in ("j0", "j1", "j2", "j3"))
        ]
        validated = [row for row in candidate_jump if bool(row["validated_jump"])]
        control_successes = sum(bool(row["condition_success"]) for row in control_rows)
        held_control_successes = sum(bool(row["condition_success"]) for row in held_controls)
        jsr_successes = sum(bool(row["condition_success"]) for row in jump_rows)
        held_successes = sum(bool(row["condition_success"]) for row in held_rows)
        jsr_ci = _wilson(jsr_successes, len(jump_rows))
        fjr_ci = _wilson(control_successes, len(control_rows))
        held_ci = _wilson(held_successes, len(held_rows))
        held_fjr_ci = _wilson(held_control_successes, len(held_controls))
        summaries.append(
            {
                "condition": condition,
                "existing_worlds": len(jump_rows),
                "existing_successes": jsr_successes,
                "jsr": jsr_successes / len(jump_rows),
                "jsr_ci_low": jsr_ci[0],
                "jsr_ci_high": jsr_ci[1],
                "existing_control_worlds": len(control_rows),
                "false_jumps": control_successes,
                "fjr": control_successes / len(control_rows),
                "fjr_ci_low": fjr_ci[0],
                "fjr_ci_high": fjr_ci[1],
                "heldout_worlds": len(held_rows),
                "heldout_successes": held_successes,
                "heldout_jsr": held_successes / len(held_rows),
                "heldout_jsr_ci_low": held_ci[0],
                "heldout_jsr_ci_high": held_ci[1],
                "heldout_control_worlds": len(held_controls),
                "heldout_false_jumps": held_control_successes,
                "heldout_fjr": held_control_successes / len(held_controls),
                "heldout_fjr_ci_low": held_fjr_ci[0],
                "heldout_fjr_ci_high": held_fjr_ci[1],
                "abductive_precision": len(validated) / len(accepted) if accepted else None,
                "validated_candidates": len(validated),
                "accepted_candidates_j0_j3": len(accepted),
                "mean_counterfactual_gain": sum(
                    float(row.get("oracle_cf_loss", 0)) - float(row.get("candidate_cf_loss", 0))
                    for row in candidate_jump
                    if row["replay_verified"]
                )
                / len(candidate_jump),
                "mean_tokens_per_existing_world": sum(int(row["llm_tokens"]) for row in jump_rows)
                / len(jump_rows),
                "tokens_per_success": sum(int(row["llm_tokens"]) for row in jump_rows)
                / jsr_successes
                if jsr_successes
                else None,
                "primitive_operation_capacity": int(jump_rows[0]["primitive_operation_capacity"]),
            }
        )
    summary_by_condition = {row["condition"]: row for row in summaries}

    primary = []
    for right in (Condition.C0_FIXED_SPACE.value, Condition.C2_GENERIC_DEPTH_1.value):
        primary.append(
            {
                "comparison": f"{Condition.C3_GENERIC_COMPOSITION.value}-{right}",
                "family": "PRIMARY_EXISTING",
                **_paired_effect(
                    existing_jump,
                    Condition.C3_GENERIC_COMPOSITION.value,
                    right,
                    stratified=True,
                ),
            }
        )
    _holm(primary)
    secondary = []
    for right in (
        Condition.C1_ATOMIC_HIGH_LEVEL.value,
        Condition.C_RAND_RANDOM_PRIMITIVES.value,
        Condition.C_SELF_LLM_COMPOSITION.value,
    ):
        secondary.append(
            {
                "comparison": f"{Condition.C3_GENERIC_COMPOSITION.value}-{right}",
                "family": "SECONDARY_EXISTING",
                **_paired_effect(
                    existing_jump,
                    Condition.C3_GENERIC_COMPOSITION.value,
                    right,
                    stratified=True,
                ),
            }
        )
    _holm(secondary)
    heldout_comparisons = []
    for right in (
        Condition.C0_FIXED_SPACE.value,
        Condition.C2_GENERIC_DEPTH_1.value,
        Condition.C_RAND_RANDOM_PRIMITIVES.value,
        Condition.C_SELF_LLM_COMPOSITION.value,
    ):
        heldout_comparisons.append(
            {
                "comparison": f"{Condition.C3_GENERIC_COMPOSITION.value}-{right}",
                "family": "HELDOUT",
                **_paired_effect(
                    heldout_jump,
                    Condition.C3_GENERIC_COMPOSITION.value,
                    right,
                    stratified=False,
                ),
            }
        )
    # C3-C0 is the independently registered held-out primary; adjust the remaining three.
    heldout_comparisons[0]["p_holm"] = heldout_comparisons[0]["p_one_sided"]
    _holm(heldout_comparisons[1:])
    comparisons = primary + secondary + heldout_comparisons
    pq.write_table(
        pa.Table.from_pylist(comparisons),
        artifacts / "compositional_comparisons.parquet",
        compression="zstd",
    )

    rho = _rho_bootstrap(existing_jump)
    per_family = []
    for family in FAMILIES:
        rates = {}
        for condition in conditions:
            selected = [
                row
                for row in existing_jump
                if row["family"] == family and row["condition"] == condition
            ]
            rates[condition] = sum(bool(row["condition_success"]) for row in selected) / len(selected)
        denominator = rates[Condition.C1_ATOMIC_HIGH_LEVEL.value] - rates[Condition.C0_FIXED_SPACE.value]
        per_family.append(
            {
                "family": family,
                "c0_jsr": rates[Condition.C0_FIXED_SPACE.value],
                "c1_jsr": rates[Condition.C1_ATOMIC_HIGH_LEVEL.value],
                "c2_jsr": rates[Condition.C2_GENERIC_DEPTH_1.value],
                "c3_jsr": rates[Condition.C3_GENERIC_COMPOSITION.value],
                "rho_j": (
                    rates[Condition.C3_GENERIC_COMPOSITION.value]
                    - rates[Condition.C0_FIXED_SPACE.value]
                )
                / denominator
                if denominator > 0
                else None,
            }
        )
    pq.write_table(
        pa.Table.from_pylist(per_family),
        artifacts / "compositional_per_family.parquet",
        compression="zstd",
    )

    pq.write_table(
        pa.Table.from_pylist(worlds),
        artifacts / "compositional_jump_results.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist([row for row in worlds if row["family"] == HELD_OUT_FAMILY]),
        artifacts / "heldout_family_results.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [row for row in candidates if row["condition"] == Condition.C_RAND_RANDOM_PRIMITIVES.value]
        ),
        artifacts / "random_primitive_control.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [row for row in candidates if row["condition"] == Condition.C_SELF_LLM_COMPOSITION.value]
        ),
        artifacts / "llm_selected_composition.parquet",
        compression="zstd",
    )
    no_jump_depth = [
        {
            "condition": row["condition"],
            "family": row["family"],
            "world_id": row["world_id"],
            "world_seed": row["world_seed"],
            "slot": row["slot"],
            "depth": row["ancestry_depth"],
            "validated_jump": row["validated_jump"],
            "j0": row.get("j0"),
            "j1": row.get("j1"),
            "j2": row.get("j2"),
            "j3": row.get("j3"),
            "j4": row.get("j4"),
            "j5": row.get("j5"),
        }
        for row in candidates
        if row["no_jump"]
    ]
    pq.write_table(
        pa.Table.from_pylist(no_jump_depth),
        artifacts / "no_jump_depth_controls.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(summaries),
        artifacts / "compositional_cost_frontier.parquet",
        compression="zstd",
    )

    c3 = summary_by_condition[Condition.C3_GENERIC_COMPOSITION.value]
    c0 = summary_by_condition[Condition.C0_FIXED_SPACE.value]
    family_advantage = sum(row["c3_jsr"] > row["c0_jsr"] for row in per_family)
    primary_pass = all(row["estimate"] > 0 and row["p_holm"] < 0.05 for row in primary)
    retention_pass = bool(
        rho["rho_j"] is not None
        and rho["rho_j"] >= 0.25
        and rho["ci_low"] is not None
        and rho["ci_low"] > 0
    )
    combined_controls = [
        row
        for row in worlds
        if row["no_jump"] and row["condition"] == Condition.C3_GENERIC_COMPOSITION.value
    ]
    combined_false = sum(bool(row["condition_success"]) for row in combined_controls)
    combined_fjr = combined_false / len(combined_controls)
    combined_fjr_ci = _wilson(combined_false, len(combined_controls))
    depth_increase = c3["fjr"] - summary_by_condition[Condition.C2_GENERIC_DEPTH_1.value]["fjr"]
    fjr_pass = (
        combined_fjr <= 0.01
        and combined_fjr_ci[1] <= 0.02
        and depth_increase <= 0.02
    )
    replay_pass = all(bool(row["replay_verified"]) for row in candidates)
    depth_pass = all(
        int(row["ancestry_depth"]) >= 2
        for row in candidates
        if row["condition"] == Condition.C3_GENERIC_COMPOSITION.value
        and row["validated_jump"]
    )
    cj4 = (
        primary_pass
        and retention_pass
        and family_advantage >= 4
        and fjr_pass
        and replay_pass
        and depth_pass
    )
    heldout_primary = heldout_comparisons[0]
    heldout_material = (
        c3["heldout_jsr"] - c0["heldout_jsr"] >= 0.10
        and heldout_primary["p_one_sided"] < 0.05
        and heldout_primary["ci_low"] > 0
    )
    heldout_safety = c3["heldout_fjr"] <= 0.01 and c3["heldout_fjr_ci_high"] <= 0.05
    cj5 = cj4 and heldout_material and heldout_safety
    if cj5:
        verdict = "CJ5"
    elif cj4 or any(row["estimate"] > 0 for row in primary):
        verdict = "CJ3"
    else:
        verdict = "CJ2"

    sequence_counts = Counter(
        tuple(row["mutation_ancestry"])
        for row in candidates
        if row["condition"] == Condition.C3_GENERIC_COMPOSITION.value
        and row["validated_jump"]
    )
    claim_rows = [
        {"criterion": "C3 > C0 and C3 > C2 after primary Holm correction", "passed": primary_pass, "evidence": json.dumps(primary, sort_keys=True)},
        {"criterion": "rho_J >= 0.25 with positive lower bootstrap bound", "passed": retention_pass, "evidence": json.dumps(rho, sort_keys=True)},
        {"criterion": "C3 exceeds C0 in at least four known families", "passed": family_advantage >= 4, "evidence": str(family_advantage)},
        {"criterion": "C3 FJR controlled overall and by depth", "passed": fjr_pass, "evidence": f"overall={combined_fjr:.6f}; upper={combined_fjr_ci[1]:.6f}; depth_delta={depth_increase:.6f}"},
        {"criterion": "successful C3 ancestry is multi-step and replay valid", "passed": replay_pass and depth_pass, "evidence": f"replay={replay_pass}; depth={depth_pass}"},
        {"criterion": "held-out C3 materially exceeds C0", "passed": heldout_material, "evidence": json.dumps(heldout_primary, sort_keys=True)},
        {"criterion": "held-out-interface C3 FJR controlled", "passed": heldout_safety, "evidence": f"rate={c3['heldout_fjr']:.6f}; upper={c3['heldout_fjr_ci_high']:.6f}"},
    ]
    with (artifacts / "final_compositional_claim_matrix.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("criterion", "passed", "evidence"))
        writer.writeheader()
        writer.writerows(claim_rows)

    final = {
        "verdict_before_reviewer2": verdict,
        "aj5_frozen_and_retained": True,
        "aj6_candidate_available": cj5,
        "preregistration_commit": "65f2087",
        "implementation_correction_commit": "7ecb977",
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "condition_results": summaries,
        "comparisons": comparisons,
        "retained_jump_gain": rho,
        "known_family_advantage_count": family_advantage,
        "combined_c3_fjr": combined_fjr,
        "combined_c3_fjr_ci": combined_fjr_ci,
        "successful_sequence_counts": [
            {"sequence": list(sequence), "successful_candidates": count}
            for sequence, count in sequence_counts.most_common()
        ],
        "gates": {
            "primary_pass": primary_pass,
            "retention_pass": retention_pass,
            "family_coverage_pass": family_advantage >= 4,
            "fjr_pass": fjr_pass,
            "replay_pass": replay_pass,
            "multi_step_pass": depth_pass,
            "cj4": cj4,
            "heldout_material": heldout_material,
            "heldout_safety": heldout_safety,
            "cj5": cj5,
        },
        "claim_boundary": "At most compositional and held-out representation-space escape under the frozen procedural worlds; not general scientific or theory invention.",
    }
    (artifacts / "final_compositional_verdict.json").write_text(
        json.dumps(final, indent=2, sort_keys=True) + "\n"
    )

    short_labels = ["C0", "C1", "C2", "C3", "Cself", "Crand"]
    plot_conditions = conditions[:4] + conditions[4:6]
    _svg(
        figures / "figure1-atomic-vs-composition.svg",
        "Figure 1 — Atomic menu versus primitive composition",
        '<rect x="80" y="150" width="330" height="230" rx="18" fill="#f1d9ce" stroke="#9a4b3d"/>'
        '<text x="245" y="210" text-anchor="middle" font-family="sans-serif" font-size="21">C1 atomic high-level menu</text>'
        '<text x="245" y="270" text-anchor="middle" font-family="sans-serif" font-size="17">one family-aligned choice</text>'
        '<path d="M430 265 L560 265" stroke="#256d85" stroke-width="7"/>'
        '<rect x="580" y="110" width="340" height="310" rx="18" fill="#dce8e8" stroke="#365f64"/>'
        '<text x="750" y="175" text-anchor="middle" font-family="sans-serif" font-size="21">C3 generic composition</text>'
        '<text x="750" y="230" text-anchor="middle" font-family="sans-serif" font-size="17">R₀ → R₁ → R₂ → R₃ → R₄</text>'
        '<text x="750" y="285" text-anchor="middle" font-family="sans-serif" font-size="17">local typed rewrites</text>'
        '<text x="750" y="340" text-anchor="middle" font-family="sans-serif" font-size="17">outcome-blind ranking</text>',
    )
    _bars(
        figures / "figure2-jsr.svg",
        "Figure 2 — Existing-family jump success",
        short_labels,
        [summary_by_condition[condition]["jsr"] for condition in plot_conditions],
        "#256d85",
    )
    _bars(
        figures / "figure3-rho-by-family.svg",
        "Figure 3 — Retained jump gain by family",
        [family.replace("_", " ")[:12] for family in FAMILIES],
        [float(row["rho_j"] or 0.0) for row in per_family],
        "#7a4eab",
    )
    depth_counts: dict[int, list[bool]] = {}
    for row in candidates:
        if row["condition"] in {
            Condition.C2_GENERIC_DEPTH_1.value,
            Condition.C3_GENERIC_COMPOSITION.value,
            Condition.C_SELF_LLM_COMPOSITION.value,
            Condition.C_RAND_RANDOM_PRIMITIVES.value,
        } and not row["no_jump"]:
            depth_counts.setdefault(int(row["ancestry_depth"]), []).append(
                bool(row["validated_jump"])
            )
    _bars(
        figures / "figure4-success-vs-depth.svg",
        "Figure 4 — Candidate success by construction depth",
        [f"d={depth}" for depth in sorted(depth_counts)],
        [sum(depth_counts[depth]) / len(depth_counts[depth]) for depth in sorted(depth_counts)],
        "#c6533f",
    )
    _bars(
        figures / "figure5-heldout.svg",
        "Figure 5 — Held-out triadic relation family",
        short_labels,
        [summary_by_condition[condition]["heldout_jsr"] for condition in plot_conditions],
        "#b17b24",
    )
    scatter = []
    for index, condition in enumerate(plot_conditions):
        row = summary_by_condition[condition]
        x = 100 + row["fjr"] * 700
        y = 500 - row["jsr"] * 390
        scatter.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#256d85"/>'
            f'<text x="{x + 12:.1f}" y="{y + index % 2 * 17:.1f}" font-family="sans-serif" font-size="14">{short_labels[index]}</text>'
        )
    _svg(figures / "figure6-jsr-vs-fjr.svg", "Figure 6 — JSR versus FJR", "".join(scatter))
    finite_cost = [
        float(summary_by_condition[condition]["tokens_per_success"] or 0.0)
        for condition in plot_conditions
    ]
    _bars(
        figures / "figure7-cost-frontier.svg",
        "Figure 7 — Completion-token cost per successful world",
        short_labels,
        finite_cost,
        "#5a7d45",
    )
    return final


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
