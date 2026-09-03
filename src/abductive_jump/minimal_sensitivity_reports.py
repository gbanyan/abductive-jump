"""Completion-locked tables and figures for the minimal NMI sensitivity extension."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .minimal_sensitivity_analysis import ALL_RUNS, require_finalized
from .phi_budget_integration import BUDGET_SHARDS, require_phi_budget_finalized

ORDER = (
    "historical_phi4_4bit_cself",
    "phi4_4bit_budget_cself",
    "phi8_cself",
    "deepseek_matched_cself",
    "deepseek_native_cself",
    "phi8_cself_repair",
    "deepseek_p2",
)
LABELS = {
    "historical_phi4_4bit_cself": "Phi-4 4-bit\nhistorical slice",
    "phi4_4bit_budget_cself": "Phi-4 4-bit\n2,048-token budget",
    "phi8_cself": "Phi-4 8-bit\nC_self",
    "deepseek_matched_cself": "DeepSeek matched\nC_self",
    "deepseek_native_cself": "DeepSeek native\nC_self",
    "phi8_cself_repair": "Phi-4 8-bit\none repair",
    "deepseek_p2": "DeepSeek\nsupplied representation",
}
AXIS_LABELS = {
    "historical_phi4_4bit_cself": "Phi-4\n4b / 700*",
    "phi4_4bit_budget_cself": "Phi-4\n4b / 2,048",
    "phi8_cself": "Phi-4\n8b / 700",
    "deepseek_matched_cself": "DeepSeek\nmatched",
    "deepseek_native_cself": "DeepSeek\nnative",
    "phi8_cself_repair": "Phi-4 8b\none repair",
    "deepseek_p2": "DeepSeek P2\nn=40",
}
COLORS = {
    "historical_phi4_4bit_cself": "#7A7A7A",
    "phi4_4bit_budget_cself": "#E69F00",
    "phi8_cself": "#56B4E9",
    "deepseek_matched_cself": "#0072B2",
    "deepseek_native_cself": "#D55E00",
    "phi8_cself_repair": "#CC79A7",
    "deepseek_p2": "#009E73",
}
STAGES = (
    "response",
    "parse",
    "schema",
    "operation",
    "arguments/types",
    "executable",
    "J1",
    "J2",
    "J3",
    "J4",
    "J5",
)
STAGE_ALIASES = {
    "response_returned": "response",
    "request_returned": "response",
    "parse_valid": "parse",
    "json_parse_valid": "parse",
    "schema_valid": "schema",
    "plan_schema_valid": "schema",
    "operation_valid": "operation",
    "operation_names_valid": "operation",
    "argument_type_valid": "arguments/types",
    "argument_types_valid": "arguments/types",
    "executable": "executable",
    "j1": "J1",
    "j2": "J2",
    "j3": "J3",
    "j4": "J4",
    "j5": "J5",
    "J1": "J1",
    "J2": "J2",
    "J3": "J3",
    "J4": "J4",
    "J5": "J5",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_report_ready(base: Path) -> dict[str, Any]:
    require_finalized(base / "results")
    require_phi_budget_finalized(base.parents[1])
    replay_path = base / "analysis" / "replay_report.json"
    if not replay_path.is_file():
        raise ValueError(f"report locked: missing {replay_path}")
    replay = json.loads(replay_path.read_text())
    if replay.get("status") != "complete_verified" or int(replay.get("mismatches", -1)) != 0:
        raise ValueError("report locked: deterministic replay is not complete with zero mismatches")
    if set(replay.get("shards", {})) != set(ALL_RUNS) | set(BUDGET_SHARDS):
        raise ValueError("report locked: replay does not cover every sensitivity shard")
    analysis_path = base / "analysis" / "analysis.json"
    if not analysis_path.is_file():
        raise ValueError(f"report locked: missing {analysis_path}")
    return json.loads(analysis_path.read_text())


def format_count(row: dict[str, str]) -> str:
    return f"{int(row['successes'])}/{int(row['worlds'])}"


def percent(value: str | float, digits: int = 1) -> str:
    return f"{100 * float(value):.{digits}f}%"


def setup_plotting() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.fonttype": "none",
        }
    )


def save_figure(fig: plt.Figure, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.08)
    fig.savefig(destination.with_suffix(".png"), dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def interval_error_distances(
    values: np.ndarray, lows: np.ndarray, highs: np.ndarray
) -> np.ndarray:
    """Return plotting distances robust to endpoint round-off at zero and one."""
    return np.maximum(0.0, np.vstack([values - lows, highs - values]))


def plot_world_summary(rows: list[dict[str, str]], destination: Path) -> None:
    lookup = {row["condition"]: row for row in rows}
    ordered = [lookup[name] for name in ORDER]
    values = np.array([float(row["jsr"]) for row in ordered])
    lows = np.array([float(row["wilson_95_low"]) for row in ordered])
    highs = np.array([float(row["wilson_95_high"]) for row in ordered])
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    x = np.arange(len(ordered))
    ax.bar(x, values, color=[COLORS[row["condition"]] for row in ordered], width=0.68)
    ax.errorbar(
        x,
        values,
        yerr=interval_error_distances(values, lows, highs),
        fmt="none",
        ecolor="#202020",
        capsize=3,
    )
    for index, row in enumerate(ordered):
        ax.text(
            index,
            min(1.055, values[index] + 0.045),
            format_count(row),
            ha="center",
            va="bottom",
            fontsize=7,
        )
    ax.axvline(5.5, color="#A0A0A0", linestyle="--", linewidth=0.9)
    ax.text(5.55, 1.075, "n=40 control", fontsize=7, color="#555555", ha="left")
    ax.set_xticks(x, [AXIS_LABELS[row["condition"]] for row in ordered])
    ax.set_ylabel("World-level jump success rate")
    ax.set_ylim(0, 1.12)
    ax.set_yticks(np.linspace(0, 1, 6), [f"{int(value * 100)}%" for value in np.linspace(0, 1, 6)])
    ax.set_title(
        "Fixed-panel sensitivity and supplied-representation positive control",
        loc="left",
        weight="bold",
    )
    save_figure(fig, destination)


def normalized_attrition(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for row in rows:
        stage = STAGE_ALIASES.get(row["stage"])
        if stage is None:
            continue
        result.setdefault(row["condition"], {})[stage] = float(row["rate"])
    return result


def plot_attrition(rows: list[dict[str, str]], destination: Path) -> None:
    normalized = normalized_attrition(rows)
    conditions = [name for name in ORDER if name != "deepseek_p2" and name in normalized]
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    x = np.arange(len(STAGES))
    for name in conditions:
        values = [normalized[name].get(stage, np.nan) for stage in STAGES]
        ax.plot(
            x,
            values,
            marker="o",
            ms=3.5,
            lw=1.7,
            label=LABELS[name].replace("\n", " "),
            color=COLORS[name],
        )
    ax.set_xticks(x, STAGES, rotation=35, ha="right")
    ax.set_ylim(-0.03, 1.06)
    ax.set_yticks(np.linspace(0, 1, 6), [f"{int(value * 100)}%" for value in np.linspace(0, 1, 6)])
    ax.set_ylabel("Fraction passing stage")
    ax.set_title("C_self response-to-verdict attrition", loc="left", weight="bold")
    ax.legend(frameon=False, fontsize=6.7, ncol=2, loc="upper right")
    save_figure(fig, destination)


def plot_family_heatmap(rows: list[dict[str, str]], destination: Path) -> None:
    conditions = [name for name in ORDER if name in {row["condition"] for row in rows}]
    families = sorted({row["family"] for row in rows})
    lookup = {(row["condition"], row["family"]): float(row["jsr"]) for row in rows}
    matrix = np.array(
        [
            [lookup.get((condition, family), np.nan) for condition in conditions]
            for family in families
        ]
    )
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    image = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    ax.set_xticks(np.arange(len(conditions)), [AXIS_LABELS[name] for name in conditions])
    ax.set_yticks(np.arange(len(families)), [name.replace("_", " ") for name in families])
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            value = matrix[row_index, column_index]
            if not np.isnan(value):
                ax.text(
                    column_index,
                    row_index,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color="white" if value < 0.65 else "black",
                )
    fig.colorbar(image, ax=ax, label="JSR", fraction=0.025, pad=0.02)
    ax.set_title("Per-family descriptive sensitivity results", loc="left", weight="bold")
    save_figure(fig, destination)


def markdown_report(
    summaries: list[dict[str, str]],
    paired: list[dict[str, str]],
    ledgers: list[dict[str, str]],
    budget_summaries: list[dict[str, str]],
    budget_paired: list[dict[str, str]],
) -> str:
    lines = [
        "# Minimal targeted sensitivity extension",
        "",
        "This extension is a targeted sensitivity analysis. The original frozen Phi-4 4-bit n=400 confirmatory study remains unchanged. The matched comparisons below use the same fixed 96 historical worlds; the supplied-representation positive control uses a predeclared balanced n=40 subset. The 2,048-token Phi-4 condition was separately prospectively frozen and changes only the completion cap.",
        "",
        "## World-level results",
        "",
        "| Condition | Population | Successes | JSR | Wilson 95% interval |",
        "|---|---|---:|---:|---:|",
    ]
    lookup = {row["condition"]: row for row in summaries}
    for name in ORDER:
        row = lookup[name]
        interval = f"{percent(row['wilson_95_low'])}–{percent(row['wilson_95_high'])}"
        lines.append(
            f"| {LABELS[name].replace(chr(10), ' ')} | {row['population']} | {format_count(row)} | {percent(row['jsr'])} | {interval} |"
        )
    lines.extend(
        [
            "",
            "## Paired world-level differences",
            "",
            "| Reference | Comparison | Both fail | Both succeed | Comparison only | Reference only | Difference |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in paired:
        lines.append(
            f"| {LABELS[row['reference']].replace(chr(10), ' ')} | {LABELS[row['comparison']].replace(chr(10), ' ')} | "
            f"{row['both_fail']} | {row['both_succeed']} | {row['comparison_only_success']} | {row['reference_only_success']} | "
            f"{float(row['paired_jsr_difference']):+.3f} |"
        )
    lines.extend(
        [
            "",
            "## Full Phi-4 completion-budget sensitivity",
            "",
            "| Condition | Population | Successes | JSR | Wilson 95% interval |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in budget_summaries:
        interval = f"{percent(row['wilson_95_low'])}–{percent(row['wilson_95_high'])}"
        lines.append(
            f"| {row['condition']} | {row['population']} | {format_count(row)} | "
            f"{percent(row['jsr'])} | {interval} |"
        )
    lines.extend(
        [
            "",
            "| Reference | Comparison | Both fail | Both succeed | Comparison only | Reference only | Difference |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in budget_paired:
        lines.append(
            f"| {row['reference']} | {row['comparison']} | {row['both_fail']} | "
            f"{row['both_succeed']} | {row['comparison_only_success']} | "
            f"{row['reference_only_success']} | {float(row['paired_jsr_difference']):+.3f} |"
        )
    lines.extend(
        [
            "",
            "## Compute ledger",
            "",
            "| Condition | Calls | Prompt tokens | Completion tokens | Reasoning text calls | Latency (s) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    ledger_lookup = {row["condition"]: row for row in ledgers}
    for name in ORDER:
        if name not in ledger_lookup:
            continue
        row = ledger_lookup[name]
        lines.append(
            f"| {LABELS[name].replace(chr(10), ' ')} | {row['llm_calls']} | {row['prompt_tokens']} | "
            f"{row['completion_tokens']} | {row['reasoning_text_available_calls']} | {float(row['latency_seconds_sum']):.1f} |"
        )
    lines.extend(
        [
            "",
            "No candidate-level significance tests were performed. DeepSeek native and the 2,048-token Phi-4 condition are not compute-matched to historical Phi-4. Phi-4 8-bit differs from the historical run jointly in precision and serving engine. Historical `parse_valid` follows the registered legacy object-extraction parser; strict whole-response JSON validity was 0/1,200.",
            "",
        ]
    )
    return "\n".join(lines)


def build(root: Path) -> dict[str, str]:
    base = root / "experiments" / "nmi_minimal_sensitivity_v1"
    require_report_ready(base)
    analysis = base / "analysis"
    summaries = read_csv(analysis / "world_summary.csv")
    paired = read_csv(analysis / "paired_world_differences.csv")
    attrition = read_csv(analysis / "gate_attrition.csv")
    per_family = read_csv(analysis / "per_family.csv")
    ledgers = read_csv(analysis / "compute_ledger.csv")
    budget_summaries = read_csv(analysis / "phi_budget_world_summary.csv")
    budget_paired = read_csv(analysis / "phi_budget_paired_differences.csv")
    setup_plotting()
    figures = root / "reports" / "figures" / "minimal_sensitivity"
    plot_world_summary(summaries, figures / "figure1-world-jsr")
    plot_attrition(attrition, figures / "figure2-gate-attrition")
    plot_family_heatmap(per_family, figures / "figure3-per-family")
    report_path = analysis / "minimal_sensitivity_report.md"
    report_path.write_text(
        markdown_report(summaries, paired, ledgers, budget_summaries, budget_paired)
    )
    return {"report": str(report_path), "figures": str(figures)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(build(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
