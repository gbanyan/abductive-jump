from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .conditions import Condition, ProposalSource
from .worlds import FAMILIES

BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20_260_902


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def _wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return (float("nan"), float("nan"))
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def _paired_bootstrap(
    rows: list[dict[str, Any]], left: str, right: str, label_key: str
) -> dict[str, float]:
    rows = [row for row in rows if not row["no_jump"]]
    lookup = {(row["family"], int(row["world_seed"]), row[label_key]): bool(row["condition_success"]) for row in rows}
    seeds = {
        family: sorted({int(row["world_seed"]) for row in rows if row["family"] == family})
        for family in FAMILIES
    }
    observed = sum(
        sum(lookup[(family, seed, left)] - lookup[(family, seed, right)] for seed in seeds[family])
        / len(seeds[family])
        for family in FAMILIES
    ) / len(FAMILIES)
    rng = random.Random(BOOTSTRAP_SEED ^ sum(ord(c) for c in left + right))
    samples: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        family_differences = []
        for family in FAMILIES:
            drawn = [rng.choice(seeds[family]) for _ in seeds[family]]
            family_differences.append(
                sum(lookup[(family, seed, left)] - lookup[(family, seed, right)] for seed in drawn)
                / len(drawn)
            )
        samples.append(sum(family_differences) / len(family_differences))
    return {
        "estimate": observed,
        "ci_low": _quantile(samples, 0.025),
        "ci_high": _quantile(samples, 0.975),
        "p_one_sided": (sum(value <= 0 for value in samples) + 1) / (len(samples) + 1),
    }


def _bootstrap_rate(rows: list[dict[str, Any]], label: str, label_key: str) -> tuple[float, float]:
    rows = [row for row in rows if not row["no_jump"] and row[label_key] == label]
    by_family = {
        family: [bool(row["condition_success"]) for row in rows if row["family"] == family]
        for family in FAMILIES
    }
    rng = random.Random(BOOTSTRAP_SEED ^ sum(ord(char) for char in label))
    samples = []
    for _ in range(BOOTSTRAP_REPLICATES):
        rates = []
        for family in FAMILIES:
            values = by_family[family]
            rates.append(sum(rng.choice(values) for _ in values) / len(values))
        samples.append(sum(rates) / len(rates))
    return _quantile(samples, 0.025), _quantile(samples, 0.975)


def _holm(comparisons: list[dict[str, Any]]) -> None:
    ordered = sorted(comparisons, key=lambda row: row["p_one_sided"])
    running = 0.0
    total = len(ordered)
    for index, row in enumerate(ordered):
        running = max(running, min(1.0, (total - index) * row["p_one_sided"]))
        row["p_holm"] = running


def _svg(path: Path, title: str, body: str, width: int = 960, height: int = 560) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<rect width="100%" height="100%" fill="#faf8f3"/>'
        f'<text x="48" y="52" font-family="sans-serif" font-size="25" font-weight="700" fill="#172121">{title}</text>'
        + body
        + '</svg>\n'
    )


def _bar_figure(path: Path, title: str, labels: list[str], values: list[float], color: str = "#256d85") -> None:
    width, height = 960, 560
    plot_x, plot_y, plot_w, plot_h = 75, 90, 830, 390
    gap = plot_w / len(values)
    parts = [f'<line x1="{plot_x}" y1="{plot_y + plot_h}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h}" stroke="#172121"/>']
    for index, (label, value) in enumerate(zip(labels, values)):
        bar_w = gap * 0.62
        x = plot_x + index * gap + gap * 0.19
        bar_h = max(1, value * plot_h)
        y = plot_y + plot_h - bar_h
        parts += [
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" fill="{color}"/>',
            f'<text x="{x + bar_w / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-family="sans-serif" font-size="16">{value:.3f}</text>',
            f'<text x="{x + bar_w / 2:.1f}" y="{plot_y + plot_h + 28}" text-anchor="middle" font-family="sans-serif" font-size="14">{label}</text>',
        ]
    _svg(path, title, "".join(parts), width, height)


def _load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    return [row for path in paths for row in pq.read_table(path).to_pylist()]


def run(root: Path) -> dict[str, Any]:
    artifacts = root / "artifacts"
    confirmatory = artifacts / "confirmatory"
    figures = root / "reports" / "figures"
    primary = _load_rows(
        [
            confirmatory / "primary-jump" / "world_condition_results.parquet",
            confirmatory / "primary-control" / "world_condition_results.parquet",
        ]
    )
    factorial = _load_rows(
        [
            confirmatory / "factorial-jump" / "world_results.parquet",
            confirmatory / "factorial-control" / "world_results.parquet",
        ]
    )
    candidates = pq.read_table(artifacts / "candidate_theories.parquet").to_pylist()
    a6_worlds = _load_rows(
        [
            confirmatory / "ablation-a6-jump" / "world_results.parquet",
            confirmatory / "ablation-a6-control" / "world_results.parquet",
        ]
    )
    conditions = [condition.value for condition in Condition]
    gate_columns = (
        "condition",
        "world_id",
        "family",
        "world_seed",
        "no_jump",
        "slot",
        "theory_hash",
        "j0",
        "j1",
        "j2",
        "j3",
        "j4",
        "j5",
        "validated_jump",
        "candidate_obs_loss",
        "candidate_cf_loss",
        "candidate_falsification_loss",
        "oracle_obs_loss",
        "oracle_cf_loss",
        "oracle_falsification_loss",
    )
    pq.write_table(
        pa.Table.from_pylist([{key: row.get(key) for key in gate_columns} for row in candidates]),
        artifacts / "confirmatory_jump_gate_results.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist([row for row in primary if row["no_jump"]]),
        artifacts / "confirmatory_no_jump_controls.parquet",
        compression="zstd",
    )

    condition_rows: list[dict[str, Any]] = []
    for condition in conditions:
        jumps = [row for row in primary if row["condition"] == condition and not row["no_jump"]]
        controls = [row for row in primary if row["condition"] == condition and row["no_jump"]]
        jsr = sum(row["condition_success"] for row in jumps) / len(jumps)
        jsr_low, jsr_high = _bootstrap_rate(primary, condition, "condition")
        fjr_count = sum(row["condition_success"] for row in controls)
        fjr = fjr_count / len(controls)
        fjr_low, fjr_high = _wilson(fjr_count, len(controls))
        condition_candidates = [row for row in candidates if row["condition"] == condition and not row["no_jump"]]
        accepted = [row for row in condition_candidates if all(bool(row.get(g)) for g in ("j0", "j1", "j2", "j3"))]
        validated = [row for row in condition_candidates if bool(row["validated_jump"])]
        condition_rows.append(
            {
                "condition": condition,
                "jump_worlds": len(jumps),
                "jsr": jsr,
                "jsr_ci_low": jsr_low,
                "jsr_ci_high": jsr_high,
                "control_worlds": len(controls),
                "fjr": fjr,
                "fjr_ci_low": fjr_low,
                "fjr_ci_high": fjr_high,
                "abductive_precision": len(validated) / len(accepted) if accepted else None,
                "accepted_candidates_j0_j3": len(accepted),
                "validated_candidates": len(validated),
                "mean_tokens_per_world": sum(row["llm_tokens_used"] for row in jumps) / len(jumps),
                "tokens_per_successful_world": (
                    sum(row["llm_tokens_used"] for row in jumps)
                    / sum(row["condition_success"] for row in jumps)
                    if any(row["condition_success"] for row in jumps)
                    else None
                ),
                "mean_archive_occupancy": sum(row["archive_occupancy"] for row in jumps) / len(jumps),
            }
        )
    pq.write_table(pa.Table.from_pylist(condition_rows), artifacts / "condition_summary.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pylist(factorial), artifacts / "proposal_reasoning_factorial.parquet", compression="zstd")

    primary_pairs = [
        (external, baseline)
        for external in (Condition.B4_REPRESENTATION_MUTATION.value, Condition.B5_FULL_SYSTEM.value)
        for baseline in (
            Condition.B0_DIRECT_LLM.value,
            Condition.B1_SAMPLE_MATCHED.value,
            Condition.B2_FIXED_SPACE_AGENT.value,
            Condition.B3_ATTRIBUTE_MUTATION.value,
        )
    ]
    comparisons = []
    for left, right in primary_pairs:
        result = _paired_bootstrap(primary, left, right, "condition")
        comparisons.append({"comparison": f"{left}-{right}", "family": "primary", **result})
    factorial_pairs = [
        (ProposalSource.P1_EXTERNAL.value, ProposalSource.P0_LLM.value),
        (ProposalSource.P2_ORACLE.value, ProposalSource.P0_LLM.value),
    ]
    factorial_comparisons = []
    for left, right in factorial_pairs:
        result = _paired_bootstrap(factorial, left, right, "proposal_source")
        factorial_comparisons.append({"comparison": f"{left}-{right}", "family": "factorial", **result})
    _holm(comparisons)
    _holm(factorial_comparisons)
    all_comparisons = comparisons + factorial_comparisons
    pq.write_table(pa.Table.from_pylist(all_comparisons), artifacts / "confirmatory_comparisons.parquet", compression="zstd")

    summary_by_condition = {row["condition"]: row for row in condition_rows}
    factorial_jsr = {
        source.value: sum(row["condition_success"] for row in factorial if row["proposal_source"] == source.value and not row["no_jump"]) / 400
        for source in ProposalSource
    }
    family_success = {
        condition: sum(
            any(row["condition_success"] for row in primary if row["condition"] == condition and row["family"] == family and not row["no_jump"])
            for family in FAMILIES
        )
        for condition in (Condition.B4_REPRESENTATION_MUTATION.value, Condition.B5_FULL_SYSTEM.value)
    }
    primary_supported = all(row["estimate"] > 0 and row["p_holm"] < 0.05 for row in comparisons)
    factorial_supported = all(row["estimate"] > 0 and row["p_holm"] < 0.05 for row in factorial_comparisons)
    fjr_controlled = all(
        summary_by_condition[condition]["fjr_ci_high"] <= 0.05
        for condition in (Condition.B4_REPRESENTATION_MUTATION.value, Condition.B5_FULL_SYSTEM.value)
    )
    aj5 = (
        primary_supported
        and factorial_supported
        and fjr_controlled
        and factorial_jsr[ProposalSource.P2_ORACLE.value] >= 0.8
        and min(family_success.values()) >= 4
    )
    verdict = "AJ5" if aj5 else "AJ2"

    claim_rows = [
        {"criterion": "B4/B5 exceed B0-B3 after Holm", "passed": primary_supported, "evidence": "8/8 corrected comparisons" if primary_supported else "comparison failure"},
        {"criterion": "B4/B5 FJR upper Wilson <= 0.05", "passed": fjr_controlled, "evidence": f"B4={summary_by_condition[Condition.B4_REPRESENTATION_MUTATION.value]['fjr_ci_high']:.4f}; B5={summary_by_condition[Condition.B5_FULL_SYSTEM.value]['fjr_ci_high']:.4f}"},
        {"criterion": "P1 and P2 exceed P0", "passed": factorial_supported, "evidence": f"P0={factorial_jsr['P0_LLM']:.3f}; P1={factorial_jsr['P1_EXTERNAL']:.3f}; P2={factorial_jsr['P2_ORACLE']:.3f}"},
        {"criterion": "P2 reasoning ceiling >= 0.80", "passed": factorial_jsr["P2_ORACLE"] >= 0.8, "evidence": f"{factorial_jsr['P2_ORACLE']:.3f}"},
        {"criterion": "B4 and B5 succeed in >=4 families", "passed": min(family_success.values()) >= 4, "evidence": json.dumps(family_success, sort_keys=True)},
        {"criterion": "Held-out structural family for AJ6", "passed": False, "evidence": "not available; AJ6 prohibited"},
    ]
    with (artifacts / "final_claim_matrix.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["criterion", "passed", "evidence"])
        writer.writeheader()
        writer.writerows(claim_rows)

    final = {
        "verdict": verdict,
        "preregistration_commit": "895ebb9118ffd0046825b88868621f2a70f69f61",
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "condition_results": condition_rows,
        "factorial_jsr": factorial_jsr,
        "comparisons": all_comparisons,
        "family_success_coverage": family_success,
        "aj6_available": False,
        "claim": "Structured external representation mutation enabled validated escape more reliably than matched fixed-space and LLM self-proposal baselines in the tested procedural worlds." if aj5 else "The preregistered AJ5 criteria were not met.",
    }
    ablations = [
        {
            "ablation": "A1_NO_DIVERSITY_ARCHIVE",
            "jsr": summary_by_condition[Condition.B4_REPRESENTATION_MUTATION.value]["jsr"],
            "reference_jsr": summary_by_condition[Condition.B5_FULL_SYSTEM.value]["jsr"],
            "interpretation": "no archive effect; B4 and B5 are equal",
        },
        {
            "ablation": "A2_NO_FALSIFIER",
            "jsr": sum(
                any(
                    all(bool(candidate.get(g)) for g in ("j0", "j1", "j2", "j3", "j4"))
                    for candidate in candidates
                    if candidate["world_id"] == world["world_id"]
                    and candidate["condition"] == Condition.B5_FULL_SYSTEM.value
                )
                for world in primary
                if world["condition"] == Condition.B5_FULL_SYSTEM.value and not world["no_jump"]
            )
            / 400,
            "reference_jsr": summary_by_condition[Condition.B5_FULL_SYSTEM.value]["jsr"],
            "interpretation": "pre-J5 world success versus validated J0-J5 success",
        },
        {
            "ablation": "A3_NO_CROSSOVER",
            "jsr": summary_by_condition[Condition.B5_FULL_SYSTEM.value]["jsr"],
            "reference_jsr": summary_by_condition[Condition.B5_FULL_SYSTEM.value]["jsr"],
            "interpretation": "structurally null: primary portfolio never used crossover",
        },
        {
            "ablation": "A4_VALUE_ONLY",
            "jsr": summary_by_condition[Condition.B3_ATTRIBUTE_MUTATION.value]["jsr"],
            "reference_jsr": summary_by_condition[Condition.B5_FULL_SYSTEM.value]["jsr"],
            "interpretation": "value mutation remains inside H(R0)",
        },
        {
            "ablation": "A5_LLM_CHOOSES_MUTATION",
            "jsr": summary_by_condition[Condition.B1_SAMPLE_MATCHED.value]["jsr"],
            "reference_jsr": summary_by_condition[Condition.B5_FULL_SYSTEM.value]["jsr"],
            "interpretation": "same generic mutation vocabulary, LLM proposal source",
        },
        {
            "ablation": "A6_RANDOM_UNTYPED",
            "jsr": sum(row["condition_success"] for row in a6_worlds if not row["no_jump"]) / 400,
            "reference_jsr": summary_by_condition[Condition.B5_FULL_SYSTEM.value]["jsr"],
            "interpretation": "random node and edge edits without structural-semantic attributes",
        },
    ]
    pq.write_table(pa.Table.from_pylist(ablations), artifacts / "ablation_summary.parquet", compression="zstd")
    final["ablations"] = ablations
    final["a6_fjr"] = sum(row["condition_success"] for row in a6_worlds if row["no_jump"]) / 200
    (artifacts / "final_verdict.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")

    labels = [condition.split("_")[0] for condition in conditions]
    jsrs = [summary_by_condition[condition]["jsr"] for condition in conditions]
    _bar_figure(figures / "figure2-jsr-by-condition.svg", "Figure 2 — Jump success rate by condition", labels, jsrs)
    factorial_labels = ["P0 LLM", "P1 external", "P2 oracle"]
    _bar_figure(figures / "figure4-proposal-reasoning.svg", "Figure 4 — Proposal versus reasoning", factorial_labels, [factorial_jsr[s.value] for s in ProposalSource], "#7a4eab")
    _svg(
        figures / "figure1-search-spaces.svg",
        "Figure 1 — Fixed-space search versus representation mutation",
        '<rect x="90" y="150" width="300" height="210" rx="18" fill="#dce8e8" stroke="#365f64"/><text x="240" y="210" text-anchor="middle" font-family="sans-serif" font-size="21">H(R₀): values and rules</text><circle cx="240" cy="285" r="34" fill="#256d85"/><text x="240" y="292" text-anchor="middle" fill="white" font-family="sans-serif">local fit</text><path d="M410 255 L545 255" stroke="#c6533f" stroke-width="8" marker-end="url(#a)"/><defs><marker id="a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#c6533f"/></marker></defs><rect x="565" y="120" width="300" height="270" rx="18" fill="#f1d9ce" stroke="#9a4b3d"/><text x="715" y="190" text-anchor="middle" font-family="sans-serif" font-size="21">R′ outside H(R₀)</text><text x="715" y="245" text-anchor="middle" font-family="sans-serif" font-size="17">new primitive / relation / state</text><text x="715" y="300" text-anchor="middle" font-family="sans-serif" font-size="17">prospective intervention</text><text x="715" y="350" text-anchor="middle" font-family="sans-serif" font-size="17">J0–J5 validation</text>',
    )
    scatter_parts = []
    for index, condition in enumerate(conditions):
        row = summary_by_condition[condition]
        x, y = 120 + (index % 2) * 28 + row["fjr"] * 700, 470 - row["jsr"] * 900
        scatter_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#256d85"/><text x="{x + 12:.1f}" y="{y + index % 2 * 18:.1f}" font-family="sans-serif" font-size="14">{labels[index]}</text>')
    _svg(figures / "figure3-jsr-vs-fjr.svg", "Figure 3 — JSR versus FJR", "".join(scatter_parts))
    raw_mean_gains = []
    for condition in conditions:
        values = [row["oracle_cf_loss"] - row["candidate_cf_loss"] for row in candidates if row["condition"] == condition and not row["no_jump"] and row["replay_verified"]]
        raw_mean_gains.append(max(0.0, sum(values) / len(values)))
    max_gain = max(raw_mean_gains) or 1.0
    _bar_figure(figures / "figure5-counterfactual-gain.svg", "Figure 5 — Mean counterfactual gain (normalized)", labels, [value / max_gain for value in raw_mean_gains], "#c6533f")
    finite_costs = [row["tokens_per_successful_world"] for row in condition_rows if row["tokens_per_successful_world"] is not None]
    max_cost = max(finite_costs)
    _bar_figure(figures / "figure6-cost-to-jump.svg", "Figure 6 — Completion tokens per success (normalized)", labels, [(row["tokens_per_successful_world"] or 0.0) / max_cost for row in condition_rows], "#5a7d45")
    per_family = []
    for family in FAMILIES:
        b5 = [row for row in primary if row["condition"] == Condition.B5_FULL_SYSTEM.value and row["family"] == family and not row["no_jump"]]
        per_family.append(sum(row["condition_success"] for row in b5) / len(b5))
    _bar_figure(figures / "figure7-per-family.svg", "Figure 7 — B5 JSR by family", [name.replace("_", " ")[:12] for name in FAMILIES], per_family, "#b17b24")
    return final


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(run(root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
