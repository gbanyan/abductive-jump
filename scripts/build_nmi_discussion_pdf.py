"""Build a discussion-ready NMI manuscript PDF from frozen publication artifacts."""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
TMP = ROOT / "tmp" / "pdfs"
OUTPUT = ROOT / "output" / "pdf" / "NMI_complete_discussion_manuscript.pdf"

NAVY = "#17324D"
BLUE = "#2978A0"
CYAN = "#55B5B1"
ORANGE = "#E6863B"
GOLD = "#E3B341"
RED = "#C5524A"
PURPLE = "#7B61A8"
GREY = "#68737D"
LIGHT = "#EEF3F6"
INK = "#182026"


def _font_paths() -> tuple[str, str]:
    import matplotlib.font_manager as fm

    return fm.findfont("DejaVu Sans"), fm.findfont(
        fm.FontProperties(family="DejaVu Sans", weight="bold")
    )


def register_fonts() -> None:
    regular, bold = _font_paths()
    pdfmetrics.registerFont(TTFont("DejaVu", regular))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold))


def clean_text(value: str) -> str:
    replacements = {
        "–": "-",
        "—": "-",
        "−": "-",
        "“": '"',
        "”": '"',
        "’": "'",
        "≤": "<=",
        "≥": ">=",
        "×": "x",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def inline_markup(value: str) -> str:
    value = clean_text(value)
    saved: list[str] = []

    def keep(match: re.Match[str]) -> str:
        saved.append(match.group(0))
        return f"@@HTML{len(saved) - 1}@@"

    value = re.sub(r"<sup>.*?</sup>", keep, value)
    value = html.escape(value)
    value = re.sub(r"`([^`]+)`", r'<font name="DejaVu">\1</font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", value)
    for index, snippet in enumerate(saved):
        value = value.replace(f"@@HTML{index}@@", clean_text(snippet))
    return value


def setup_plot() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = z * ((p * (1 - p) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return centre - half, centre + half


def panel_label(ax, label: str) -> None:
    ax.text(-0.11, 1.12, label, transform=ax.transAxes, weight="bold", fontsize=12)


def save_figure(fig, name: str) -> Path:
    path = TMP / name
    fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return path


def figure_1() -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 6.7))
    ax = axes[0, 0]
    x_obs = np.array([-2, -1, 0, 1, 2])
    y = x_obs**2
    ax.scatter(x_obs, y, color=NAVY, s=35, zorder=4, label="observations")
    x = np.linspace(-2.3, 3.2, 200)
    incumbent = x**2
    escaped = np.where(x <= 2, x**2, x**2 + 3 * (x - 2))
    ax.plot(x, incumbent, color=GREY, lw=2, label="incumbent oracle")
    ax.plot(x, escaped, color=ORANGE, lw=2, label="escaped candidate")
    ax.axvline(3, color=CYAN, ls="--", lw=1.5, label="committed action")
    ax.scatter([3], [escaped[np.argmin(abs(x - 3))]], color=ORANGE, s=45)
    ax.set_title("Observations do not reveal the representation")
    ax.set_xlabel("public input / committed intervention")
    ax.set_ylabel("outcome")
    ax.legend(frameon=False, fontsize=8)
    panel_label(ax, "a")

    ax = axes[0, 1]
    ax.axis("off")
    boxes = [
        (0.02, 0.42, 0.25, 0.28, "Frozen incumbent\ngrammar", GREY),
        (0.38, 0.42, 0.25, 0.28, "Typed generic\nrewrites", BLUE),
        (0.74, 0.42, 0.24, 0.28, "Executable escaped\nrepresentation", ORANGE),
    ]
    for x0, y0, w, h, text, colour in boxes:
        ax.add_patch(
            FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0.02", fc="white", ec=colour, lw=2)
        )
        ax.text(x0 + w / 2, y0 + h / 2, text, ha="center", va="center", color=INK)
    for x0 in (0.28, 0.64):
        ax.add_patch(
            FancyArrowPatch(
                (x0, 0.56), (x0 + 0.09, 0.56), arrowstyle="-|>", mutation_scale=15, color=NAVY
            )
        )
    ax.text(
        0.5,
        0.19,
        "Canonical membership failure proves R is outside A0",
        ha="center",
        color=NAVY,
        weight="bold",
    )
    ax.set_title("Structural escape is checked, not judged")
    panel_label(ax, "b")

    ax = axes[1, 0]
    ax.axis("off")
    steps = ["propose", "fit", "freeze", "intervene", "falsify", "replay"]
    xs = np.linspace(0.07, 0.93, len(steps))
    for i, (x0, step) in enumerate(zip(xs, steps, strict=True)):
        ax.add_patch(Circle((x0, 0.55), 0.055, color=BLUE if i < 3 else ORANGE))
        ax.text(x0, 0.55, str(i + 1), ha="center", va="center", color="white", weight="bold")
        ax.text(x0, 0.37, step, ha="center", va="top", fontsize=8)
        if i < len(steps) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x0 + 0.06, 0.55), (xs[i + 1] - 0.06, 0.55), arrowstyle="->", color=GREY
                )
            )
    ax.text(
        0.5,
        0.76,
        "Outcome remains hidden until after commitment",
        ha="center",
        color=RED,
        weight="bold",
    )
    ax.set_title("Prospective evaluation sequence")
    panel_label(ax, "c")

    ax = axes[1, 1]
    ax.axis("off")
    gates = [
        ("J0", "incumbent fits"),
        ("J1", "outside grammar"),
        ("J2", "candidate fits"),
        ("J3", "predictions differ"),
        ("J4", "intervention wins"),
        ("J5", "falsification wins"),
    ]
    for i, (key, label) in enumerate(gates):
        row, col = divmod(i, 3)
        x0, y0 = 0.03 + col * 0.33, 0.61 - row * 0.31
        ax.add_patch(
            FancyBboxPatch(
                (x0, y0), 0.28, 0.2, boxstyle="round,pad=0.015", fc=LIGHT, ec=NAVY, lw=1.2
            )
        )
        ax.text(x0 + 0.04, y0 + 0.1, key, ha="center", va="center", color=ORANGE, weight="bold")
        ax.text(x0 + 0.17, y0 + 0.1, label, ha="center", va="center", fontsize=8)
    ax.text(
        0.5,
        0.05,
        "Validated jump = J0 AND J1 AND J2 AND J3 AND J4 AND J5",
        ha="center",
        color=NAVY,
        weight="bold",
    )
    ax.set_title("All deterministic gates are required")
    panel_label(ax, "d")
    fig.suptitle(
        "Figure 1 | A prospective assay for hypothesis-space expansion",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95), h_pad=2.0, w_pad=1.4)
    return save_figure(fig, "figure_1_assay.png")


def figure_2() -> Path:
    table = pq.read_table(ARTIFACTS / "condition_summary.parquet").to_pylist()
    lookup = {row["condition"]: row for row in table}
    order = [
        "B0_DIRECT_LLM",
        "B1_SAMPLE_MATCHED",
        "B2_FIXED_SPACE_AGENT",
        "B3_ATTRIBUTE_MUTATION",
        "B4_REPRESENTATION_MUTATION",
        "B5_FULL_SYSTEM",
    ]
    labels = [
        "Direct\nmodel",
        "More\nsamples",
        "Fixed\nsearch",
        "Local\nmutation",
        "Typed\nproposal",
        "Typed +\nattributes",
    ]
    vals = np.array([lookup[k]["jsr"] for k in order])
    lows = np.array([lookup[k]["jsr_ci_low"] for k in order])
    highs = np.array([lookup[k]["jsr_ci_high"] for k in order])
    colours = [GREY, GREY, GREY, GREY, BLUE, ORANGE]
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 6.8))

    ax = axes[0, 0]
    ax.bar(np.arange(6), vals * 100, color=colours, width=0.72)
    ax.errorbar(
        np.arange(6),
        vals * 100,
        yerr=[np.maximum(0, (vals - lows) * 100), np.maximum(0, (highs - vals) * 100)],
        fmt="none",
        ecolor=INK,
        capsize=3,
        lw=1,
    )
    counts = [1, 1, 0, 0, 142, 142]
    for i, (v, upper, count) in enumerate(zip(vals, highs, counts, strict=True)):
        ax.text(i, max(3.5, upper * 100 + 1.6), f"{count}/400", ha="center", fontsize=7.2)
    ax.set_xticks(np.arange(6), labels, fontsize=6.5)
    ax.set_ylabel("Jump success rate (%)")
    ax.set_ylim(0, 46)
    ax.set_title("World-level AJ5 success", pad=9)
    panel_label(ax, "a")

    ax = axes[0, 1]
    fact_labels = ["Model\nproposal", "External typed\nproposal", "Oracle\nrepresentation"]
    fact = [0, 35.5, 100]
    bars = ax.bar(np.arange(3), fact, color=[GREY, BLUE, GOLD], width=0.65)
    for bar, text in zip(bars, ["0/400", "142/400", "400/400"], strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 3, text, ha="center", fontsize=8
        )
    ax.set_xticks(np.arange(3), fact_labels)
    ax.set_ylim(0, 112)
    ax.set_ylabel("Jump success rate (%)")
    ax.set_title("Proposal-source factorial", pad=9)
    panel_label(ax, "b")

    ax = axes[1, 0]
    slots = [1, 2, 3]
    ax.plot(
        slots,
        np.array([53, 101, 142]) / 4,
        marker="o",
        lw=2.5,
        color=BLUE,
        label="External typed",
    )
    ax.plot(
        slots,
        np.array([58, 96, 142]) / 4,
        marker="o",
        lw=2.5,
        color=ORANGE,
        label="Full typed",
    )
    for x0, a, b in zip(slots, [53, 101, 142], [58, 96, 142], strict=True):
        ax.text(x0 - 0.05, a / 4 + 2.2, f"{a}/400", color=BLUE, fontsize=7, ha="right")
        ax.text(x0 + 0.05, b / 4 - 3.8, f"{b}/400", color=ORANGE, fontsize=7, ha="left")
    ax.set_xticks(slots)
    ax.set_xlabel("Candidate slots used")
    ax.set_ylabel("Jump success rate (%)")
    ax.set_ylim(0, 43)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("World success by candidate slots", pad=9)
    panel_label(ax, "c")

    ax = axes[1, 1]
    gates = ["J0", "J1", "J2", "J3", "J4", "J5"]
    b4 = [1200, 823, 573, 270, 154, 154]
    b5 = [1200, 838, 562, 262, 145, 145]
    x = np.arange(len(gates))
    ax.plot(x, np.array(b4) / 12, marker="o", lw=2.2, color=BLUE, label="External typed")
    ax.plot(x, np.array(b5) / 12, marker="o", lw=2.2, color=ORANGE, label="Full typed")
    for i, (a, b) in enumerate(zip(b4, b5, strict=True)):
        if i in {0, 3, 5}:
            ax.text(i - 0.05, a / 12 + 4, str(a), color=BLUE, fontsize=7, ha="right")
            ax.text(i + 0.05, b / 12 - 7, str(b), color=ORANGE, fontsize=7, ha="left")
    ax.set_xticks(x, gates)
    ax.set_ylim(0, 112)
    ax.set_ylabel("Candidates retained (%)")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Cumulative gate attrition (n=1,200)", pad=9)
    panel_label(ax, "d")
    fig.suptitle(
        "Figure 2 | Typed proposals and their gate attrition",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=2.2, w_pad=1.8)
    return save_figure(fig, "figure_2_aj5.png")


def figure_3() -> Path:
    rows = pq.read_table(ARTIFACTS / "compositional_cost_frontier.parquet").to_pylist()
    lookup = {r["condition"]: r for r in rows}
    order = [
        "C0_FIXED_SPACE",
        "C1_ATOMIC_HIGH_LEVEL",
        "C2_GENERIC_DEPTH_1",
        "C3_GENERIC_COMPOSITION",
        "C_SELF_LLM_COMPOSITION",
        "C_RAND_RANDOM_PRIMITIVES",
        "C5_ORACLE_REPRESENTATION",
    ]
    labels = [
        "Fixed\nlanguage",
        "Atomic\nreference*",
        "One-step\nedits",
        "Deterministic\nsearch",
        "Legacy model\nedits [L]",
        "Random\ncomposition",
        "Oracle\nreference*",
    ]
    values = np.array([lookup[k]["jsr"] for k in order]) * 100
    low = np.array([lookup[k]["jsr_ci_low"] for k in order]) * 100
    high = np.array([lookup[k]["jsr_ci_high"] for k in order]) * 100
    fig = plt.figure(figsize=(10.4, 6.6))
    grid = fig.add_gridspec(
        2, 2, height_ratios=[0.8, 1.2], width_ratios=[0.38, 0.62], hspace=0.55, wspace=0.32
    )

    ax = fig.add_subplot(grid[0, 0])
    ax.axis("off")
    nodes = [(0.1, "Primitive"), (0.36, "Type"), (0.62, "Arity"), (0.88, "Bind")]
    for i, (x0, name) in enumerate(nodes):
        colour = BLUE if i < 3 else ORANGE
        ax.add_patch(Circle((x0, 0.52), 0.085, color=colour))
        ax.text(x0, 0.52, str(i + 1), ha="center", va="center", color="white", weight="bold")
        ax.text(x0, 0.28, name, ha="center", fontsize=8)
        if i < 3:
            ax.add_patch(
                FancyArrowPatch(
                    (x0 + 0.09, 0.52), (nodes[i + 1][0] - 0.09, 0.52), arrowstyle="->", color=GREY
                )
            )
    ax.text(0.5, 0.82, "No one-step family operator", ha="center", weight="bold", color=NAVY)
    ax.set_title("Four local rewrites form one ancestry")
    panel_label(ax, "a")

    ax = fig.add_subplot(grid[0, 1])
    colours = [GREY, GOLD, GREY, ORANGE, GREY, CYAN, GOLD]
    ax.bar(np.arange(7), values, color=colours, width=0.7)
    ax.errorbar(
        np.arange(7),
        values,
        yerr=[np.maximum(0, values - low), np.maximum(0, high - values)],
        fmt="none",
        ecolor=INK,
        capsize=2.5,
        lw=1,
    )
    counts = [0, 131, 0, 400, 0, 52, 400]
    for i, (v, upper, count) in enumerate(zip(values, high, counts, strict=True)):
        ax.text(i, max(4, upper + 1.8), f"{count}/400", ha="center", fontsize=7.2)
    ax.set_xticks(np.arange(7), labels, fontsize=6.2)
    ax.set_ylabel("Jump success rate (%)")
    ax.set_ylim(0, 116)
    ax.set_title("Search plus motif realization reaches every world")
    ax.text(
        0.02,
        -0.29,
        "*Reference condition; operation semantics differ",
        transform=ax.transAxes,
        fontsize=7,
        color=GREY,
    )
    panel_label(ax, "b")

    ax = fig.add_subplot(grid[1, :])
    fam = pq.read_table(ARTIFACTS / "compositional_per_family.parquet").to_pylist()
    aliases = {
        "latent_common_cause": "latent cause",
        "unification": "unification",
        "hidden_regimes": "regimes",
        "property_to_relation": "relation",
        "state_invention": "state",
        "coordinate_transform": "coordinate",
        "causal_ambiguity": "causal",
        "meta_law": "meta-law",
    }
    names = [aliases[r["family"]] for r in fam]
    c1 = np.array([r["c1_jsr"] for r in fam]) * 100
    c3 = np.array([r["c3_jsr"] for r in fam]) * 100
    x = np.arange(len(names))
    w = 0.36
    ax.bar(x - w / 2, c1, w, color=GOLD, label="Atomic reference")
    ax.bar(x + w / 2, c3, w, color=ORANGE, label="Deterministic composition")
    ax.set_xticks(x, names, fontsize=7.3, rotation=24, ha="right")
    ax.set_ylim(0, 112)
    ax.set_ylabel("Jump success rate (%)")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.set_title("Deterministic search plus realizer saturates all generators", pad=10)
    panel_label(ax, "c")
    fig.suptitle(
        "Figure 3 | Generic search with fixed motif realization",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    return save_figure(fig, "figure_3_cj5.png")


def figure_4() -> Path:
    rows = pq.read_table(ARTIFACTS / "compositional_cost_frontier.parquet").to_pylist()
    lookup = {r["condition"]: r for r in rows}
    order = [
        "C0_FIXED_SPACE",
        "C1_ATOMIC_HIGH_LEVEL",
        "C2_GENERIC_DEPTH_1",
        "C3_GENERIC_COMPOSITION",
        "C_SELF_LLM_COMPOSITION",
        "C_RAND_RANDOM_PRIMITIVES",
        "C5_ORACLE_REPRESENTATION",
    ]
    labels = ["C0", "C1", "C2", "C3", "Cself", "Crand", "C5"]
    values = np.array([lookup[k]["heldout_jsr"] for k in order]) * 100
    low = np.array([lookup[k]["heldout_jsr_ci_low"] for k in order]) * 100
    high = np.array([lookup[k]["heldout_jsr_ci_high"] for k in order]) * 100
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 6.4))

    ax = axes[0, 0]
    ax.axis("off")
    for x0, title, detail, colour in [
        (0.04, "Archived C3", "2,400 candidates\n500/500 jump worlds\n0/300 controls", BLUE),
        (
            0.57,
            "No-model replay",
            "2,400 identical verdicts\n500/500 jump worlds\n0/300 controls",
            ORANGE,
        ),
    ]:
        ax.add_patch(
            FancyBboxPatch(
                (x0, 0.30), 0.38, 0.42, boxstyle="round,pad=0.025", fc="white", ec=colour, lw=2
            )
        )
        ax.text(x0 + 0.19, 0.61, title, ha="center", weight="bold", color=NAVY)
        ax.text(x0 + 0.19, 0.45, detail, ha="center", va="center", fontsize=8)
    ax.add_patch(FancyArrowPatch((0.43, 0.51), (0.56, 0.51), arrowstyle="<->", color=NAVY))
    ax.text(
        0.5,
        0.16,
        "Model output was not semantically necessary",
        ha="center",
        color=RED,
        weight="bold",
    )
    ax.set_title("Component audit reproduces every C3 verdict")
    panel_label(ax, "a")

    ax = axes[0, 1]
    colours = [GREY, GOLD, GREY, ORANGE, GREY, CYAN, GOLD]
    ax.bar(np.arange(7), values, color=colours, width=0.7)
    ax.errorbar(
        np.arange(7),
        values,
        yerr=[np.maximum(0, values - low), np.maximum(0, high - values)],
        fmt="none",
        ecolor=INK,
        capsize=2.5,
        lw=1,
    )
    counts = [0, 0, 0, 100, 0, 13, 100]
    for i, (v, count) in enumerate(zip(values, counts, strict=True)):
        ax.text(i, v + 4, f"{count}/100", ha="center", fontsize=7.3)
    ax.set_xticks(np.arange(7), labels)
    ax.set_ylim(0, 116)
    ax.set_ylabel("Held-out JSR (%)")
    ax.set_title("Search-side held-out result with fixed realizer")
    panel_label(ax, "b")

    analysis = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "analysis"
    with (analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summary_rows = list(csv.DictReader(handle))
    fair_analysis = ROOT / "experiments" / "nmi_fair_interface_v1" / "analysis"
    with (fair_analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summary_rows.extend(csv.DictReader(handle))
    crand_low, crand_high = wilson_interval(16, 96)
    c3_low, c3_high = wilson_interval(96, 96)
    summary_rows.extend(
        [
            {
                "condition": "crand_panel",
                "jsr": str(16 / 96),
                "wilson_95_low": str(crand_low),
                "wilson_95_high": str(crand_high),
                "successes": "16",
                "worlds": "96",
            },
            {
                "condition": "c3_panel",
                "jsr": "1.0",
                "wilson_95_low": str(c3_low),
                "wilson_95_high": str(c3_high),
                "successes": "96",
                "worlds": "96",
            },
        ]
    )
    sensitivity_order = [
        "historical_phi4_4bit_cself",
        "phi4_4bit_budget_cself",
        "phi8_cself",
        "deepseek_matched_cself",
        "deepseek_native_cself",
        "deepseek_fair_interface_cself",
        "crand_panel",
        "c3_panel",
        "phi8_cself_repair",
        "deepseek_p2",
    ]
    sensitivity_labels = [
        "Phi4\n700*",
        "Phi4\n2,048",
        "Phi4\n8-bit",
        "DS\nmatched",
        "DS\nnative",
        "DS\ngrammar",
        "Crand\npanel",
        "C3\npanel",
        "Phi4\nrepair",
        "DS\nP2†",
    ]
    summary_lookup = {row["condition"]: row for row in summary_rows}
    sensitivity_values = (
        np.array([float(summary_lookup[name]["jsr"]) for name in sensitivity_order]) * 100
    )
    sensitivity_low = (
        np.array([float(summary_lookup[name]["wilson_95_low"]) for name in sensitivity_order]) * 100
    )
    sensitivity_high = (
        np.array([float(summary_lookup[name]["wilson_95_high"]) for name in sensitivity_order])
        * 100
    )
    ax = axes[1, 0]
    sx = np.arange(len(sensitivity_order))
    ax.bar(
        sx,
        sensitivity_values,
        color=[GREY, GOLD, BLUE, CYAN, ORANGE, PURPLE, "#56B4E9", NAVY, RED, "#009E73"],
        width=0.7,
    )
    ax.errorbar(
        sx,
        sensitivity_values,
        yerr=[
            np.maximum(0, sensitivity_values - sensitivity_low),
            np.maximum(0, sensitivity_high - sensitivity_values),
        ],
        fmt="none",
        ecolor=INK,
        capsize=2.5,
        lw=1,
    )
    for index, name in enumerate(sensitivity_order):
        row = summary_lookup[name]
        ax.text(
            index,
            min(108, sensitivity_values[index] + 4),
            f"{row['successes']}/{row['worlds']}",
            ha="center",
            fontsize=6.8,
        )
    ax.axvline(8.5, color="#A0A0A0", linestyle="--", linewidth=0.8)
    ax.set_xticks(sx, sensitivity_labels, fontsize=6.2)
    ax.set_ylim(0, 116)
    ax.set_ylabel("World-level JSR (%)")
    ax.set_title("Fixed-panel sensitivity and archived search controls")
    panel_label(ax, "c")

    ax = axes[1, 1]
    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition_rows = list(csv.DictReader(handle))
    with (fair_analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition_rows.extend(
            {**row, "condition": "deepseek_fair_interface_cself"} for row in csv.DictReader(handle)
        )
    stage_aliases = {
        "response_returned": "response",
        "request_returned": "response",
        "serialization_returned": "response",
        "parse_valid": "parse",
        "json_parse_valid": "parse",
        "strict_whole_response_json": "parse",
        "schema_valid": "schema",
        "plan_schema_valid": "schema",
        "operation_valid": "operation",
        "operation_names_valid": "operation",
        "argument_type_valid": "types",
        "argument_types_valid": "types",
        "executable": "execute",
        "J1": "J1",
        "J2": "J2",
        "J3": "J3",
        "J4": "J4",
        "J5": "J5",
    }
    attrition_stages = [
        "response",
        "parse",
        "schema",
        "operation",
        "types",
        "execute",
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
    ]
    attrition_lookup: dict[str, dict[str, float]] = {}
    for row in attrition_rows:
        stage = stage_aliases.get(row["stage"])
        if stage:
            attrition_lookup.setdefault(row["condition"], {})[stage] = (float(row["rate"]) * 100 if int(row["denominator"]) else np.nan)
    line_conditions = [
        "historical_phi4_4bit_cself",
        "phi4_4bit_budget_cself",
        "phi8_cself",
        "deepseek_matched_cself",
        "deepseek_native_cself",
        "deepseek_fair_interface_cself",
        "phi8_cself_repair",
    ]
    line_labels = [
        "Phi4 700*",
        "Phi4 2,048",
        "Phi4 8-bit",
        "DS matched",
        "DS native",
        "DS grammar",
        "Phi4 repair",
    ]
    line_colours = [GREY, GOLD, BLUE, CYAN, ORANGE, PURPLE, RED]
    tx = np.arange(len(attrition_stages))
    for name, label, colour in zip(line_conditions, line_labels, line_colours, strict=True):
        ax.plot(
            tx,
            [attrition_lookup[name].get(stage, np.nan) for stage in attrition_stages],
            marker="o",
            ms=2.4,
            lw=1.25,
            color=colour,
            label=label,
        )
    ax.set_xticks(tx, attrition_stages, rotation=38, ha="right", fontsize=6.5)
    ax.set_ylim(-3, 106)
    ax.set_ylabel("Passing stage (%)")
    ax.legend(
        frameon=True,
        framealpha=0.9,
        edgecolor="none",
        facecolor="white",
        fontsize=5.8,
        ncol=2,
        loc="lower left",
    )
    ax.set_title("Response-to-verdict attrition")
    panel_label(ax, "d")
    fig.suptitle(
        "Figure 4 | Component attribution, transfer and model sensitivity",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=2.0, w_pad=1.5)
    return save_figure(fig, "figure_4_sensitivity.png")


def figure_5() -> Path:
    analysis = ROOT / "experiments" / "nmi_realizer_audit_v1" / "analysis"
    with (analysis / "condition_summary.csv").open(newline="", encoding="utf-8") as handle:
        summaries = list(csv.DictReader(handle))
    with (analysis / "paired_transitions.csv").open(newline="", encoding="utf-8") as handle:
        transitions = list(csv.DictReader(handle))
    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition = list(csv.DictReader(handle))

    def summary(source: str, population: str, policy: str) -> dict[str, str]:
        return next(
            row
            for row in summaries
            if row["source"] == source
            and row["population"] == population
            and row["policy"] == policy
        )

    groups = [
        ("C3", "known", "C3\nknown"),
        ("C3", "heldout", "C3\nheld out"),
        ("C_rand", "known", "Crand\nknown"),
        ("C_rand", "heldout", "Crand\nheld out"),
        ("DeepSeek_grammar", "fixed_known_panel", "DS grammar\npanel"),
    ]
    policies = ["aligned", "motif_disabled", "role_action_blind_binding"]
    policy_labels = ["Aligned", "Motif disabled", "Role/action blind"]
    policy_colours = [NAVY, GREY, ORANGE]

    fig, axes = plt.subplots(2, 2, figsize=(10.6, 7.0))
    ax = axes[0, 0]
    x = np.arange(len(groups))
    width = 0.24
    for offset, (policy, label, colour) in enumerate(
        zip(policies, policy_labels, policy_colours, strict=True)
    ):
        rows = [summary(source, population, policy) for source, population, _ in groups]
        values = np.array([100 * float(row["jsr"]) for row in rows])
        lows = np.array([100 * float(row["wilson_95_low"]) for row in rows])
        highs = np.array([100 * float(row["wilson_95_high"]) for row in rows])
        positions = x + (offset - 1) * width
        ax.bar(positions, values, width=width, color=colour, label=label)
        ax.errorbar(
            positions,
            values,
            yerr=[np.maximum(0, values - lows), np.maximum(0, highs - values)],
            fmt="none",
            ecolor=INK,
            capsize=2,
            lw=0.8,
        )
        for position, value, row in zip(positions, values, rows, strict=True):
            if value >= 40:
                ax.text(
                    position,
                    value - 5,
                    f"{row['successes']}/{row['worlds']}",
                    ha="center",
                    va="top",
                    fontsize=5.6,
                    color="white",
                    weight="bold",
                    rotation=90,
                )
            elif value > 0:
                ax.text(
                    position,
                    value + 2.5,
                    f"{row['successes']}/{row['worlds']}",
                    ha="center",
                    fontsize=5.5,
                    rotation=90,
                )
    ax.set_xticks(x, [label for _, _, label in groups], fontsize=7)
    ax.set_ylim(0, 125)
    ax.set_ylabel("World-level JSR (%)")
    ax.set_title("Incumbent substitution removes discrimination by design")
    ax.legend(
        frameon=False,
        fontsize=6.3,
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.96),
    )
    panel_label(ax, "a")

    ax = axes[0, 1]
    sources = ["C3", "C_rand", "DeepSeek_grammar"]
    source_labels = ["C3", "Crand", "DS grammar"]
    transition_lookup = {(row["source"], row["comparison"]): row for row in transitions}
    blind_comparison = "aligned_vs_role_action_blind_binding"
    lost = np.array(
        [int(transition_lookup[(source, blind_comparison)]["aligned_only"]) for source in sources]
    )
    gained = np.array(
        [
            int(transition_lookup[(source, blind_comparison)]["counterfactual_only"])
            for source in sources
        ]
    )
    retained = np.array(
        [int(transition_lookup[(source, blind_comparison)]["both_pass"]) for source in sources]
    )
    y = np.arange(len(sources))
    ax.barh(y, -lost, color=RED, label="Lost")
    ax.barh(y, gained, color=CYAN, label="Gained")
    for index, value in enumerate(lost):
        ax.text(-value - 1, index, str(value), va="center", ha="right", fontsize=7)
    for index, value in enumerate(gained):
        ax.text(value + 1, index, str(value), va="center", ha="left", fontsize=7)
    for index, value in enumerate(retained):
        ax.text(0, index + 0.24, f"{value} retained", ha="center", fontsize=6.5, color=NAVY)
    bound = max(max(lost), max(gained), 1) * 1.3
    ax.set_xlim(-bound, bound)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks(y, source_labels)
    ax.set_xlabel("Paired world transitions under role/action-blind binding")
    ax.set_title("Field rebinding has a selective effect")
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    panel_label(ax, "b")

    ax = axes[1, 0]
    stages = ["J0", "J1", "J2", "J3", "J4", "J5"]
    annotation_offsets = {"C3": (6, 5), "C_rand": (0, -11), "DeepSeek_grammar": (-8, 7)}
    for source, label, colour in zip(sources, source_labels, [NAVY, ORANGE, PURPLE], strict=True):
        rows = [
            row
            for row in attrition
            if row["source"] == source and row["policy"] == "motif_disabled"
        ]
        lookup = {row["stage"]: row for row in rows}
        values = [100 * float(lookup[stage]["rate"]) for stage in stages]
        ax.plot(stages, values, marker="o", lw=1.6, ms=3.5, label=label, color=colour)
        ax.annotate(
            f"{lookup['J2']['passed']}/{lookup['J2']['denominator']}",
            xy=(2, values[2]),
            xytext=annotation_offsets[source],
            textcoords="offset points",
            color=colour,
            fontsize=6.2,
            ha="center",
        )
    ax.set_ylim(-3, 108)
    ax.set_ylabel("Cumulative candidate retention (%)")
    ax.set_title("Most slots reach J1-J2, none reaches J3")
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    panel_label(ax, "c")

    ax = axes[1, 1]
    signatures = [
        "relation_arity_3",
        "unobserved_dependency",
        "bound_relation",
        "multi_argument_function",
        "self_composed_function",
        "temporally_indexed_recurrence",
        "unobserved_selector",
        "shared_rule_binding",
    ]
    matrix = []
    for source in sources:
        matrix.append(
            [
                int(
                    transition_lookup[(source, f"aligned_vs_mask_signature:{signature}")][
                        "aligned_only"
                    ]
                )
                for signature in signatures
            ]
        )
    matrix_array = np.array(matrix)
    image_plot = ax.imshow(matrix_array, cmap="Oranges", aspect="auto", vmin=0, vmax=100)
    for row_index in range(matrix_array.shape[0]):
        for column_index in range(matrix_array.shape[1]):
            value = matrix_array[row_index, column_index]
            ax.text(
                column_index,
                row_index,
                str(value),
                ha="center",
                va="center",
                fontsize=6.5,
                color="white" if value >= 55 else INK,
            )
    short_signatures = [
        "arity 3",
        "latent dep.",
        "bound rel.",
        "multi-arg",
        "self-comp.",
        "temporal",
        "selector",
        "shared rule",
    ]
    ax.set_xticks(
        np.arange(len(signatures)), short_signatures, rotation=35, ha="right", fontsize=6.3
    )
    ax.set_yticks(np.arange(len(sources)), source_labels)
    ax.set_title("Worlds lost when one signature is masked")
    fig.colorbar(image_plot, ax=ax, label="Aligned-only successes", fraction=0.036, pad=0.02)
    panel_label(ax, "d")

    fig.suptitle(
        "Figure 5 | Counterfactual dependence on motif semantics",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=2.1, w_pad=1.5)
    return save_figure(fig, "figure_5_realizer_audit.png")


def figure_4_editorial() -> Path:
    analysis = ROOT / "experiments" / "nmi_realizer_audit_v1" / "analysis"
    with (analysis / "condition_summary.csv").open(newline="", encoding="utf-8") as handle:
        summaries = list(csv.DictReader(handle))
    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition = list(csv.DictReader(handle))
    paired_path = (
        ROOT / "experiments" / "nmi_fair_interface_v1" / "analysis" / "paired_crand_comparison.csv"
    )
    with paired_path.open(newline="", encoding="utf-8") as handle:
        paired = next(csv.DictReader(handle))

    def row_for(source: str, population: str, policy: str) -> dict[str, str]:
        return next(
            row
            for row in summaries
            if row["source"] == source
            and row["population"] == population
            and row["policy"] == policy
        )

    fig, axes = plt.subplots(2, 2, figsize=(10.6, 6.8))

    ax = axes[0, 0]
    ax.axis("off")
    boxes = [
        (0.03, "Archived run", "2,400 candidate verdicts\n500/500 jump worlds", BLUE),
        (0.55, "Model-free replay", "2,400/2,400 matched\n500/500 retained", ORANGE),
    ]
    for x0, title, detail, colour in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x0, 0.30),
                0.40,
                0.42,
                boxstyle="round,pad=0.02",
                fc="white",
                ec=colour,
                lw=2,
            )
        )
        ax.text(x0 + 0.20, 0.59, title, ha="center", weight="bold", color=NAVY)
        ax.text(x0 + 0.20, 0.43, detail, ha="center", va="center", fontsize=8)
    ax.add_patch(FancyArrowPatch((0.44, 0.51), (0.54, 0.51), arrowstyle="->", color=NAVY, lw=1.5))
    ax.text(0.49, 0.58, "remove model output", ha="center", fontsize=6.3, color=GREY)
    ax.set_title("Successful content was already deterministic")
    panel_label(ax, "a")

    ax = axes[0, 1]
    groups = [
        ("C3", "known", "Deterministic\nsearch"),
        ("C3", "heldout", "Deterministic\nheld out"),
        ("DeepSeek_grammar", "fixed_known_panel", "Grammar-constrained\nmodel proposal"),
    ]
    x = np.arange(len(groups))
    width = 0.34
    aligned_rows = [row_for(source, population, "aligned") for source, population, _ in groups]
    disabled_rows = [
        row_for(source, population, "role_action_blind_binding") for source, population, _ in groups
    ]
    aligned = np.array([100 * float(row["jsr"]) for row in aligned_rows])
    disabled = np.array([100 * float(row["jsr"]) for row in disabled_rows])
    ax.bar(x - width / 2, aligned, width, color=NAVY, label="Aligned realizer")
    ax.bar(x + width / 2, disabled, width, color=ORANGE, label="Role/action-blind")
    for index, row in enumerate(aligned_rows):
        ax.text(
            index - width / 2,
            aligned[index] + 3,
            f"{row['successes']}/{row['worlds']}",
            ha="center",
            fontsize=7,
        )
        blind_row = disabled_rows[index]
        ax.text(index + width / 2, disabled[index] + 3,
                f"{blind_row['successes']}/{blind_row['worlds']}", ha="center", fontsize=7)
    ax.set_xticks(x, [label for _, _, label in groups], fontsize=7)
    ax.set_ylim(0, 116)
    ax.set_ylabel("World success rate (%)")
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    ax.set_title("Field binding changes a subset of successes")
    panel_label(ax, "b")

    ax = axes[1, 0]
    transition_labels = ["Both fail", "Random only", "Model only", "Both pass"]
    transition_values = [
        int(paired["both_fail"]),
        int(paired["reference_only_success"]),
        int(paired["comparison_only_success"]),
        int(paired["both_succeed"]),
    ]
    colours = [GREY, CYAN, ORANGE, NAVY]
    left = 0
    for label, value, colour in zip(transition_labels, transition_values, colours, strict=True):
        ax.barh([0], [value], left=left, color=colour, label=label, height=0.45)
        if value >= 5:
            ax.text(
                left + value / 2,
                0,
                str(value),
                ha="center",
                va="center",
                color="white",
                weight="bold",
            )
        else:
            ax.annotate(
                str(value),
                xy=(left + value / 2, 0.22),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center",
                fontsize=7,
                color=NAVY,
            )
        left += value
    ax.set_xlim(0, 96)
    ax.set_yticks([])
    ax.set_xlabel("Paired worlds (n=96)")
    ax.legend(frameon=False, fontsize=6.5, ncol=2, loc="upper center")
    ax.set_title("Model proposals do not exceed random composition")
    panel_label(ax, "c")

    ax = axes[1, 1]
    stages = ["J0", "J1", "J2", "J3"]
    sources = ["C3", "C_rand", "DeepSeek_grammar"]
    labels = ["Deterministic search", "Random composition", "Model proposals"]
    for source, label, colour in zip(sources, labels, [NAVY, CYAN, ORANGE], strict=True):
        rows = [
            row
            for row in attrition
            if row["source"] == source and row["policy"] == "motif_disabled"
        ]
        lookup = {row["stage"]: row for row in rows}
        values = [100 * float(lookup[stage]["rate"]) for stage in stages]
        ax.plot(stages, values, marker="o", lw=1.8, ms=4, label=label, color=colour)
    ax.set_ylim(-3, 106)
    ax.set_ylabel("Candidate slots retained (%)")
    ax.legend(frameon=False, fontsize=6.5, loc="lower left")
    ax.set_title("Structurally valid candidates lose discrimination at J3")
    panel_label(ax, "d")

    fig.suptitle(
        "Figure 4 | Component attribution of system-level escape",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=2.0, w_pad=1.5)
    return save_figure(fig, "figure_4_component_attribution.png")


def figure_5_worked() -> Path:
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    ax.axis("off")
    stages = [
        (0.02, 0.61, 0.16, 0.25, "Observations", "x=z=w\ny=9x^3", BLUE),
        (0.22, 0.61, 0.16, 0.25, "Incumbent", "y = 9x^3\nexact fit", GREY),
        (
            0.42,
            0.57,
            0.20,
            0.33,
            "Four rewrites",
            "1 reify edge\n2 arity -> 3\n3 bind z\n4 bind w",
            ORANGE,
        ),
        (0.66, 0.61, 0.16, 0.25, "Candidate", "y = 9xzw\noutside grammar", BLUE),
        (0.84, 0.61, 0.14, 0.25, "Commit", "z: 6 -> 7\nx=w=6", RED),
    ]
    for x0, y0, w, h, title, body, colour in stages:
        ax.add_patch(
            FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0.015", fc="white", ec=colour, lw=2)
        )
        ax.text(x0 + w / 2, y0 + h - 0.07, title, ha="center", weight="bold", color=NAVY)
        ax.text(x0 + w / 2, y0 + 0.09, body, ha="center", va="center", fontsize=8.5)
    for left, right in ((0.18, 0.22), (0.38, 0.42), (0.62, 0.66), (0.82, 0.84)):
        ax.add_patch(FancyArrowPatch((left, 0.735), (right, 0.735), arrowstyle="-|>", color=NAVY))

    outcomes = [
        (0.12, "Frozen predictions", "incumbent 1,944\ncandidate 2,268", NAVY),
        (0.40, "Reveal intervention", "observed 2,268\ncandidate wins", ORANGE),
        (0.68, "Held-out falsification", "z=5 -> 1,620\ncandidate exact", CYAN),
    ]
    for x0, title, body, colour in outcomes:
        ax.add_patch(
            FancyBboxPatch(
                (x0, 0.16), 0.22, 0.24, boxstyle="round,pad=0.02", fc=LIGHT, ec=colour, lw=1.6
            )
        )
        ax.text(x0 + 0.11, 0.32, title, ha="center", weight="bold", color=NAVY, fontsize=9)
        ax.text(x0 + 0.11, 0.22, body, ha="center", va="center", fontsize=8.5)
    ax.add_patch(FancyArrowPatch((0.34, 0.28), (0.40, 0.28), arrowstyle="-|>", color=NAVY))
    ax.add_patch(FancyArrowPatch((0.62, 0.28), (0.68, 0.28), arrowstyle="-|>", color=NAVY))
    ax.text(
        0.93,
        0.28,
        "J0-J5\nPASS",
        ha="center",
        va="center",
        fontsize=13,
        weight="bold",
        color=ORANGE,
    )
    fig.suptitle(
        "Figure 5 | One complete prospective escape",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    return save_figure(fig, "figure_5_worked_example.png")


def extended_sensitivity_figures() -> dict[str, Path]:
    """Build grammar-constrained-interface source-data figures from verified CSVs."""
    analysis = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "analysis"
    fair_analysis = ROOT / "experiments" / "nmi_fair_interface_v1" / "analysis"
    with (analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summary_rows = list(csv.DictReader(handle))
    with (fair_analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summary_rows.extend(csv.DictReader(handle))
    order = [
        "historical_phi4_4bit_cself",
        "phi4_4bit_budget_cself",
        "phi8_cself",
        "deepseek_matched_cself",
        "deepseek_native_cself",
        "deepseek_fair_interface_cself",
        "phi8_cself_repair",
        "deepseek_p2",
    ]
    labels = [
        "Phi4\n4b / 700*",
        "Phi4\n4b / 2,048",
        "Phi4\n8b / 700",
        "DeepSeek\nmatched",
        "DeepSeek\nnative",
        "DeepSeek\ngrammar",
        "Phi4 8b\none repair",
        "DeepSeek P2\nn=40",
    ]
    colours = [GREY, GOLD, BLUE, CYAN, ORANGE, PURPLE, RED, "#009E73"]
    lookup = {row["condition"]: row for row in summary_rows}
    values = np.array([100 * float(lookup[name]["jsr"]) for name in order])
    low = np.array([100 * float(lookup[name]["wilson_95_low"]) for name in order])
    high = np.array([100 * float(lookup[name]["wilson_95_high"]) for name in order])

    fig, ax = plt.subplots(figsize=(10.6, 5.2))
    x = np.arange(len(order))
    ax.bar(x, values, color=colours, width=0.68)
    ax.errorbar(
        x,
        values,
        yerr=[np.maximum(0, values - low), np.maximum(0, high - values)],
        fmt="none",
        ecolor=INK,
        capsize=3,
        lw=1,
    )
    for index, name in enumerate(order):
        row = lookup[name]
        ax.text(index, values[index] + 3.2, f"{row['successes']}/{row['worlds']}", ha="center")
    ax.axvline(6.5, color="#999999", linestyle="--", linewidth=0.9)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 105)
    ax.set_ylabel("World-level jump success rate")
    ax.set_title("Fixed-panel sensitivity and supplied-representation control", weight="bold")
    fig.tight_layout()
    world_path = save_figure(fig, "extended_sensitivity_world_jsr.png")

    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition_rows = list(csv.DictReader(handle))
    with (fair_analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition_rows.extend(
            {**row, "condition": "deepseek_fair_interface_cself"} for row in csv.DictReader(handle)
        )
    aliases = {
        "response_returned": "response",
        "request_returned": "response",
        "serialization_returned": "response",
        "parse_valid": "parse",
        "json_parse_valid": "parse",
        "strict_whole_response_json": "parse",
        "schema_valid": "schema",
        "plan_schema_valid": "schema",
        "operation_valid": "operation",
        "operation_names_valid": "operation",
        "argument_type_valid": "types",
        "argument_types_valid": "types",
        "executable": "execute",
        "J1": "J1",
        "J2": "J2",
        "J3": "J3",
        "J4": "J4",
        "J5": "J5",
    }
    stages = [
        "response",
        "parse",
        "schema",
        "operation",
        "types",
        "execute",
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
    ]
    attrition_lookup: dict[str, dict[str, float]] = {}
    for row in attrition_rows:
        stage = aliases.get(row["stage"])
        if stage:
            attrition_lookup.setdefault(row["condition"], {})[stage] = (100 * float(row["rate"]) if int(row["denominator"]) else np.nan)
    fig, ax = plt.subplots(figsize=(10.6, 5.2))
    line_order = order[:-1]
    line_labels = [
        "Phi4 700*",
        "Phi4 2,048",
        "Phi4 8-bit",
        "DS matched",
        "DS native",
        "DS grammar",
        "Phi4 repair",
    ]
    for name, label, colour in zip(line_order, line_labels, colours[:-1], strict=True):
        ax.plot(
            np.arange(len(stages)),
            [attrition_lookup[name].get(stage, np.nan) for stage in stages],
            marker="o",
            ms=3.5,
            lw=1.5,
            color=colour,
            label=label,
        )
    ax.set_xticks(np.arange(len(stages)), stages, rotation=30, ha="right")
    ax.set_ylim(-3, 105)
    ax.set_ylabel("Passing stage (%)")
    ax.set_title("C_self response-to-verdict attrition", weight="bold")
    ax.legend(frameon=False, ncol=4, fontsize=7.5, loc="upper right")
    fig.tight_layout()
    attrition_path = save_figure(fig, "extended_sensitivity_attrition.png")

    with (analysis / "per_family.csv").open(newline="", encoding="utf-8") as handle:
        family_rows = list(csv.DictReader(handle))
    with (fair_analysis / "per_family.csv").open(newline="", encoding="utf-8") as handle:
        family_rows.extend(
            {**row, "condition": "deepseek_fair_interface_cself"} for row in csv.DictReader(handle)
        )
    families = sorted({row["family"] for row in family_rows})
    family_lookup = {(row["family"], row["condition"]): float(row["jsr"]) for row in family_rows}
    matrix = np.array([[family_lookup[(family, name)] for name in order] for family in families])
    fig, ax = plt.subplots(figsize=(11.0, 5.4))
    image = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    for row_index in range(len(families)):
        for column_index in range(len(order)):
            value = matrix[row_index, column_index]
            ax.text(
                column_index,
                row_index,
                f"{value:.2f}",
                ha="center",
                va="center",
                color="white" if value < 0.65 else "black",
                fontsize=7.5,
            )
    ax.set_xticks(np.arange(len(order)), labels, rotation=20, ha="right")
    ax.set_yticks(np.arange(len(families)), [name.replace("_", " ") for name in families])
    ax.set_title("Per-family descriptive sensitivity results", weight="bold")
    fig.colorbar(image, ax=ax, label="JSR", fraction=0.028, pad=0.02)
    fig.tight_layout()
    family_path = save_figure(fig, "extended_sensitivity_per_family.png")
    return {"world": world_path, "attrition": attrition_path, "family": family_path}


class Rule(Flowable):
    def __init__(self, width: float, colour=None, thickness: float = 1.2):
        super().__init__()
        self.width = width
        self.height = thickness + 2
        self.colour = colour or colors.HexColor(BLUE)
        self.thickness = thickness

    def draw(self) -> None:
        self.canv.setStrokeColor(self.colour)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 1, self.width, 1)


def publication_rate(row):
    denominator = int(row["denominator"])
    if denominator == 0:
        return "NA"
    rate = 100 * int(row["passed"]) / denominator
    return f"{rate:.3f}%" if 0 < rate < 0.1 else f"{rate:.1f}%"


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="DejaVu-Bold",
            fontSize=25,
            leading=30,
            textColor=colors.HexColor(NAVY),
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "manuscript_title": ParagraphStyle(
            "ManuscriptTitle",
            parent=base["Title"],
            fontName="DejaVu-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor(NAVY),
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="DejaVu",
            fontSize=11,
            leading=16,
            textColor=colors.HexColor(GREY),
            spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="DejaVu-Bold",
            fontSize=17,
            leading=21,
            textColor=colors.HexColor(NAVY),
            spaceBefore=13,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="DejaVu-Bold",
            fontSize=12.5,
            leading=16,
            textColor=colors.HexColor(BLUE),
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=9.3,
            leading=13.2,
            textColor=colors.HexColor(INK),
            alignment=TA_LEFT,
            spaceAfter=7,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=9.6,
            leading=14,
            textColor=colors.HexColor(INK),
            leftIndent=7 * mm,
            rightIndent=7 * mm,
            borderColor=colors.HexColor(CYAN),
            borderWidth=0,
            borderPadding=8,
            backColor=colors.HexColor("#F5FAFA"),
            spaceAfter=10,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=7.7,
            leading=10.3,
            textColor=colors.HexColor(GREY),
            spaceBefore=4,
            spaceAfter=10,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=7.4,
            leading=9.5,
            textColor=colors.HexColor(GREY),
        ),
        "reference": ParagraphStyle(
            "Reference",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=7.8,
            leading=10.2,
            textColor=colors.HexColor(INK),
            spaceAfter=3,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="DejaVu-Bold",
            fontSize=11.5,
            leading=16,
            textColor=colors.white,
            backColor=colors.HexColor(NAVY),
            borderPadding=12,
            spaceBefore=6,
            spaceAfter=10,
        ),
        "center": ParagraphStyle(
            "Center",
            parent=base["BodyText"],
            fontName="DejaVu",
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor(GREY),
        ),
    }


def page_decor(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D7E0E5"))
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(colors.HexColor(GREY))
    canvas.drawString(20 * mm, height - 11.5 * mm, "NMI MANUSCRIPT WITH FIGURES | 5 SEPTEMBER 2026")
    canvas.drawRightString(width - 20 * mm, 11 * mm, f"{doc.page}")
    canvas.drawString(20 * mm, 11 * mm, "Complete scientific discussion copy | not yet submitted")
    canvas.restoreState()


def manuscript_page_decor(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D7E0E5"))
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(colors.HexColor(GREY))
    canvas.drawString(20 * mm, height - 11.5 * mm, "MANUSCRIPT FOR SCIENTIFIC DISCUSSION")
    canvas.drawRightString(width - 20 * mm, 11 * mm, f"{doc.page}")
    canvas.drawString(
        20 * mm, 11 * mm, "Nature Machine Intelligence Article format | not yet submitted"
    )
    canvas.restoreState()


def image_flow(path: Path, width: float = 171 * mm) -> Image:
    from PIL import Image as PILImage

    with PILImage.open(path) as source:
        w, h = source.size
    return Image(str(path), width=width, height=width * h / w)


def caption(text: str, st) -> Paragraph:
    return Paragraph(inline_markup(text), st["caption"])


def design_table(st) -> Table:
    data = [
        [
            "Condition",
            "Representation proposal",
            "Operation capacity",
            "Final slots",
            "LLM calls",
            "Role",
        ],
        ["B0 / B1", "Model direct / sampled", "3 candidate attempts", "3", "6", "AJ5 baselines"],
        [
            "B2 / B3",
            "Fixed space / attribute only",
            "3 candidate attempts",
            "3",
            "6",
            "AJ5 controls",
        ],
        ["B4 / B5", "Typed high-level changes", "3 proposals", "3", "6", "AJ5 focal"],
        ["C0 / C2", "Fixed / one generic edit", "192 evaluations", "3", "6", "CJ5 controls"],
        ["C3", "48 paths x 4 generic edits", "192 operations", "3", "6", "CJ5 focal"],
        ["Cself", "Model writes 48 four-edit plans", "192 attempted", "3", "6", "Self-proposal"],
        ["Crand", "48 random four-edit paths", "192 operations", "3", "6", "Search control"],
        [
            "C1 / C5",
            "Atomic / oracle representation",
            "non-comparable*",
            "3",
            "6",
            "Reference ceilings",
        ],
    ]
    wrapped = [[Paragraph(inline_markup(str(cell)), st["small"]) for cell in row] for row in data]
    table = Table(
        wrapped,
        colWidths=[20 * mm, 48 * mm, 29 * mm, 18 * mm, 18 * mm, 31 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CDD7DD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def literature_table(st) -> Table:
    data = [
        [
            "Evaluation",
            "Executable",
            "Frozen language",
            "Canonical out-of-space test",
            "Prospective intervention",
            "Independent falsification",
            "Proposal / reasoning separation",
            "Replay",
            "Breadth",
        ],
        [
            "Hypothesis Search [14]",
            "partial",
            "NR",
            "NR",
            "NR",
            "held-out tasks",
            "language hypothesis / program",
            "NR",
            "ARC induction",
        ],
        [
            "HypoGeniC [15]",
            "text",
            "NR",
            "NR",
            "NR",
            "held-out examples",
            "generation / ranking",
            "NR",
            "hypotheses",
        ],
        [
            "POPPER [16]",
            "partial",
            "NR",
            "NR",
            "sequential tests",
            "agentic falsification",
            "hypothesis / validator",
            "NR",
            "6 domains",
        ],
        [
            "FunSearch [13]",
            "yes",
            "program skeleton",
            "NR",
            "evaluator feedback",
            "held-out tests",
            "proposer / evaluator",
            "partial",
            "mathematics",
        ],
        [
            "PiEvo [23]",
            "yes",
            "evolving principles",
            "NR",
            "task dependent",
            "task dependent",
            "proposer / search",
            "NR",
            "4 benchmarks",
        ],
        [
            "Model Discovery Agent [24]",
            "yes",
            "open set",
            "NR",
            "Bayesian design",
            "posterior checks",
            "proposer / inference",
            "NR",
            "physics, chemistry, biology",
        ],
        [
            "HypoArena [25]",
            "judged text",
            "NR",
            "NR",
            "context regression",
            "rubric / judge",
            "NR",
            "NR",
            "988 cases; 6 domains; 15 models",
        ],
        [
            "EvoSCM [26]",
            "yes",
            "evolving causal models",
            "NR",
            "active intervention",
            "prospective prediction",
            "evolution / selection",
            "NR",
            "simulated physical worlds",
        ],
        [
            "This work",
            "yes",
            "yes",
            "canonical certificate",
            "outcome locked",
            "independent exact cases",
            "factorial + component audit",
            "exact",
            "9 synthetic families; 2-checkpoint sensitivity",
        ],
    ]
    wrapped = [[Paragraph(inline_markup(str(cell)), st["small"]) for cell in row] for row in data]
    table = Table(
        wrapped,
        colWidths=[22 * mm, 13 * mm, 15 * mm, 21 * mm, 18 * mm, 20 * mm, 23 * mm, 14 * mm, 25 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CDD7DD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def manuscript_story(st, figures: dict[int, Path]) -> list:
    text = (ROOT / "manuscript" / "NMI_MANUSCRIPT.md").read_text()
    lines = text.splitlines()
    story: list = []
    paragraph: list[str] = []
    inserted: set[int] = set()
    skipping_markdown_table = False
    paragraph_style = "body"
    reached_abstract = False

    def flush() -> None:
        if paragraph:
            content = " ".join(item.strip() for item in paragraph)
            paragraph.clear()
            if "[" in content and "REQUIRED BEFORE SUBMISSION" in content:
                return
            story.append(Paragraph(inline_markup(content), st[paragraph_style]))

    for line in lines:
        stripped = line.strip()
        if not reached_abstract:
            if stripped == "## Abstract":
                reached_abstract = True
            else:
                continue
        if stripped == "<!-- INTRODUCTION -->":
            flush()
            paragraph_style = "body"
            continue
        if skipping_markdown_table:
            if stripped.startswith("|") or not stripped:
                continue
            skipping_markdown_table = False
        stripped = stripped.replace(
            "**[DISCLOSURE REQUIRES EXPLICIT APPROVAL BY ALL AUTHORS BEFORE SUBMISSION.]**",
            "This disclosure remains subject to approval by all human authors before submission.",
        )
        if stripped.startswith("# "):
            continue
        if stripped.startswith("## "):
            flush()
            heading = stripped[3:]
            paragraph_style = "abstract" if heading == "Abstract" else "body"
            if heading == "Abstract":
                story.append(Paragraph("Abstract", st["h1"]))
            elif heading == "Results":
                story.append(Paragraph("Results", st["h1"]))
            else:
                story.append(Paragraph(inline_markup(heading), st["h1"]))
        elif stripped.startswith("### "):
            flush()
            paragraph_style = "body"
            heading = stripped[4:]
            if heading.startswith("Table 1 |"):
                story.extend(
                    [
                        Paragraph(inline_markup(heading), st["h2"]),
                        literature_table(st),
                        Paragraph(
                            "NR, not reported in the cited publication. Entries describe published evaluation designs and do not imply absence of an unreported feature.",
                            st["small"],
                        ),
                    ]
                )
                skipping_markdown_table = True
                continue
            story.append(Paragraph(inline_markup(heading), st["h2"]))
            if (
                heading == "A prospective criterion for hypothesis-space expansion"
                and 1 not in inserted
            ):
                story.extend(
                    [
                        Spacer(1, 4),
                        image_flow(figures[1]),
                        caption(
                            "Figure 1 | A prospective assay for hypothesis-space expansion. Panel a illustrates observational equivalence and a committed action; panels b-d are schematics of structural escape, commitment-before-outcome-reveal ordering and the conjunctive J0-J5 gates. JSR denotes the proportion of worlds with at least one candidate passing every gate.",
                            st,
                        ),
                    ]
                )
                inserted.add(1)
            elif (
                heading == "Typed proposals and fixed-language structural controls"
                and 2 not in inserted
            ):
                story.extend(
                    [
                        image_flow(figures[2]),
                        caption(
                            "Figure 2 | External typed proposals and their gate attrition. Panels a and b report world-level jump success rate (JSR) for n=400 worlds per condition; intervals are prospectively specified family-stratified bootstrap 95% intervals. Panel c reports cumulative successful-world counts as one, two and three slots are admitted. Panel d reports cumulative candidate retention from J0 to J5 for 1,200 candidates per condition; candidates are not independent replicates. Internal condition codes are retained in Methods and source data. All AJ5 conditions recorded 0/200 control-world false jumps.",
                            st,
                        ),
                    ]
                )
                inserted.add(2)
            elif (
                heading
                == "Generic rewrites and fixed motif realization produce validated representations"
                and 3 not in inserted
            ):
                story.extend(
                    [
                        image_flow(figures[3]),
                        caption(
                            "Figure 3 | Generic search with fixed motif realization. Panel a is schematic. Panel b reports known-family JSR with Wilson 95% intervals for n=400 worlds per condition. Atomic and oracle conditions are references with different operation semantics. [L] The legacy model interface failed before executable proposal evaluation; its zero does not isolate conceptual proposal ability. C3 and random composition compare complete search-and-selection policies. Panel c reports descriptive rates for 50 worlds per family. Deterministic composition combines generic edit search with a fixed, family-aligned motif-to-basis realizer; saturation is within-generator reliability, not independent family replication.",
                            st,
                        ),
                    ]
                )
                inserted.add(3)
            elif (
                heading == "Counterfactual replay tests predictive content and field binding"
                and 4 not in inserted
            ):
                story.extend(
                    [
                        image_flow(figures[4]),
                        caption(
                            "Figure 4 | Component attribution of system-level escape. Panel a compares archived deterministic-search verdicts with inference-free replay; all 2,400 candidate verdicts matched. Incumbent substitution forces zero prediction separation and J3 failure by construction; it does not establish that the basis library is irreplaceable. Panel b compares aligned and role/action-blind binding for C3 on 400 known-family and 100 held-out worlds, and grammar-constrained model proposals on the fixed 96-world panel. Panel c pairs the model proposer with random composition on those same 96 worlds; similar aggregate success does not establish policy equivalence. Panel d reports cumulative candidate-slot attrition under motif-disabled replay; candidate slots are not independent replicates. The post-confirmatory counterfactual made zero model calls and fixed archived candidates rather than rerunning search.",
                            st,
                        ),
                    ]
                )
                inserted.add(4)
            elif heading == "A worked prospective escape" and 5 not in inserted:
                story.extend(
                    [
                        image_flow(figures[5]),
                        caption(
                            "Figure 5 | Worked held-out example. Correlated observations make the cubic incumbent and triadic candidate observationally identical. A committed intervention separates them before outcome reveal, and a separate held-out case falsifies the incumbent.",
                            st,
                        ),
                    ]
                )
                inserted.add(5)
        elif not stripped:
            flush()
        elif stripped.startswith("**["):
            continue
        elif re.match(r"^\d+\.\s", stripped):
            flush()
            story.append(Paragraph(inline_markup(stripped), st["reference"]))
        else:
            paragraph.append(stripped)
    flush()
    return story


def markdown_appendix_story(path: Path, st) -> list:
    story: list = []
    paragraph: list[str] = []
    table_rows: list[list[str]] = []
    in_fence = False

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), st["body"]))
            paragraph.clear()

    def flush_table() -> None:
        if not table_rows:
            return
        rows = [row for row in table_rows if not all(set(cell) <= {"-", ":"} for cell in row)]
        table_rows.clear()
        if not rows:
            return
        width = 165 * mm / len(rows[0])
        wrapped = [[Paragraph(inline_markup(cell), st["small"]) for cell in row] for row in rows]
        result = Table(wrapped, colWidths=[width] * len(rows[0]), repeatRows=1, hAlign="LEFT")
        result.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CDD7DD")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F3F6F8")],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.extend([result, Spacer(1, 3 * mm)])

    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            flush_table()
        if line.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            paragraph.append(f"`{line}`")
        elif line.startswith("# "):
            flush()
            story.append(Paragraph(inline_markup(line[2:]), st["title"]))
        elif line.startswith("## "):
            flush()
            story.append(Paragraph(inline_markup(line[3:]), st["h1"]))
        elif line.startswith("### "):
            flush()
            story.append(Paragraph(inline_markup(line[4:]), st["h2"]))
        elif line.startswith("- "):
            flush()
            story.append(Paragraph(inline_markup(line[2:]), st["body"], bulletText="-"))
        elif not line:
            flush()
        elif line.startswith("|"):
            flush()
            table_rows.append([cell.strip() for cell in line.strip("|").split("|")])
        else:
            paragraph.append(line)
    flush()
    flush_table()
    return story


def sensitivity_tables(st) -> list:
    analysis = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "analysis"
    fair_analysis = ROOT / "experiments" / "nmi_fair_interface_v1" / "analysis"

    def condition_label(name: str) -> str:
        labels = {
            "historical_phi4_4bit_cself": "Historical Phi-4 4-bit C_self",
            "phi4_4bit_budget_cself": "Phi-4 4-bit 2,048-token C_self",
            "phi8_cself": "Phi-4 8-bit C_self",
            "deepseek_matched_cself": "DeepSeek matched C_self",
            "deepseek_native_cself": "DeepSeek native C_self",
            "deepseek_fair_interface_cself": "DeepSeek grammar-constrained C_self",
            "phi8_cself_repair": "Phi-4 8-bit one-repair C_self",
            "deepseek_p2": "DeepSeek supplied-representation P2",
        }
        return labels.get(name, name.replace("_", " "))

    with (analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summaries = list(csv.DictReader(handle))
    with (fair_analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summaries.extend(csv.DictReader(handle))
    summary_data = [["Condition", "Population", "Success", "JSR", "Wilson 95% CI"]]
    for row in summaries:
        summary_data.append(
            [
                condition_label(row["condition"]),
                row["population"],
                f"{row['successes']}/{row['worlds']}",
                f"{100 * float(row['jsr']):.1f}%",
                f"{100 * float(row['wilson_95_low']):.1f}-{100 * float(row['wilson_95_high']):.1f}%",
            ]
        )

    def table(data: list[list[str]], widths: list[float]) -> Table:
        wrapped = [
            [Paragraph(inline_markup(str(cell)), st["small"]) for cell in row] for row in data
        ]
        result = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
        result.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CDD7DD")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F3F6F8")],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return result

    with (analysis / "paired_world_differences.csv").open(newline="", encoding="utf-8") as handle:
        paired = list(csv.DictReader(handle))
    with (fair_analysis / "paired_world_differences.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        paired.extend(csv.DictReader(handle))
    paired_data = [
        [
            "Reference",
            "Comparison",
            "Both fail",
            "Both pass",
            "New only",
            "Old only",
            "JSR difference",
        ]
    ]
    for row in paired:
        paired_data.append(
            [
                condition_label(row["reference"]),
                condition_label(row["comparison"]),
                row["both_fail"],
                row["both_succeed"],
                row["comparison_only_success"],
                row["reference_only_success"],
                f"{float(row['paired_jsr_difference']):+.3f}",
            ]
        )

    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition = list(csv.DictReader(handle))
    attrition_data = [["Condition", "Unit", "Stage", "Passed", "Denominator", "Rate"]]
    for row in attrition:
        attrition_data.append(
            [
                condition_label(row["condition"]),
                row.get("unit", ""),
                row["stage"],
                row["passed"],
                row["denominator"],
                publication_rate(row),
            ]
        )

    with (analysis / "compute_ledger.csv").open(newline="", encoding="utf-8") as handle:
        ledger = list(csv.DictReader(handle))
    ledger_data = [
        [
            "Condition",
            "Calls",
            "Attempts",
            "Prompt tokens",
            "Completion tokens",
            "Reasoning text",
            "Latency (s)",
        ]
    ]
    for row in ledger:
        ledger_data.append(
            [
                condition_label(row["condition"]),
                row["llm_calls"],
                row["transport_attempts"],
                row["prompt_tokens"],
                row["completion_tokens"],
                row["reasoning_text_available_calls"],
                f"{float(row['latency_seconds_sum']):.1f}",
            ]
        )

    with (analysis / "phi_budget_world_summary.csv").open(newline="", encoding="utf-8") as handle:
        budget_summaries = list(csv.DictReader(handle))
    budget_summary_data = [["Condition", "Population", "Success", "JSR", "Wilson 95% CI"]]
    for row in budget_summaries:
        budget_summary_data.append(
            [
                row["condition"].replace("_", " "),
                row["population"],
                f"{row['successes']}/{row['worlds']}",
                f"{100 * float(row['jsr']):.1f}%",
                f"{100 * float(row['wilson_95_low']):.1f}-{100 * float(row['wilson_95_high']):.1f}%",
            ]
        )
    with (analysis / "phi_budget_paired_differences.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        budget_paired = list(csv.DictReader(handle))
    budget_paired_data = [
        ["Reference", "Comparison", "Both fail", "Both pass", "New only", "Old only", "Difference"]
    ]
    for row in budget_paired:
        budget_paired_data.append(
            [
                row["reference"].replace("_", " "),
                row["comparison"].replace("_", " "),
                row["both_fail"],
                row["both_succeed"],
                row["comparison_only_success"],
                row["reference_only_success"],
                f"{float(row['paired_jsr_difference']):+.3f}",
            ]
        )
    with (analysis / "phi_budget_gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        budget_attrition = list(csv.DictReader(handle))
    budget_attrition_data = [["Population", "Unit", "Stage", "Passed", "Denominator", "Rate"]]
    for row in budget_attrition:
        budget_attrition_data.append(
            [
                row["condition"].replace("_", " "),
                row["unit"],
                row["stage"],
                row["passed"],
                row["denominator"],
                publication_rate(row),
            ]
        )
    with (analysis / "phi_budget_compute_ledger.csv").open(newline="", encoding="utf-8") as handle:
        budget_ledger = list(csv.DictReader(handle))
    budget_ledger_data = [
        ["Population", "Calls", "Attempts", "Prompt tokens", "Completion tokens", "Latency (s)"]
    ]
    for row in budget_ledger:
        budget_ledger_data.append(
            [
                row["condition"].replace("_", " "),
                row["llm_calls"],
                row["transport_attempts"],
                row["prompt_tokens"],
                row["completion_tokens"],
                f"{float(row['latency_seconds_sum']):.1f}",
            ]
        )

    with (fair_analysis / "per_family.csv").open(newline="", encoding="utf-8") as handle:
        fair_families = list(csv.DictReader(handle))
    fair_family_data = [["Family", "Success", "JSR", "Wilson 95% CI"]]
    for row in fair_families:
        fair_family_data.append(
            [
                row["family"].replace("_", " "),
                f"{row['successes']}/{row['worlds']}",
                f"{100 * float(row['jsr']):.1f}%",
                f"{100 * float(row['wilson_95_low']):.1f}-{100 * float(row['wilson_95_high']):.1f}%",
            ]
        )
    with (fair_analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        fair_attrition = list(csv.DictReader(handle))
    fair_attrition_data = [["Unit", "Stage", "Passed", "Denominator", "Rate"]]
    for row in fair_attrition:
        fair_attrition_data.append(
            [
                row["unit"].replace("_", " "),
                row["stage"],
                row["passed"],
                row["denominator"],
                publication_rate(row),
            ]
        )
    with (fair_analysis / "compute_ledger.csv").open(newline="", encoding="utf-8") as handle:
        fair_ledger = list(csv.DictReader(handle))
    fair_ledger_data = [
        ["Stage", "Calls", "Prompt tokens", "Completion tokens", "Cap hits", "Latency (s)"]
    ]
    for row in fair_ledger:
        fair_ledger_data.append(
            [
                row["stage"],
                row["calls"],
                row["prompt_tokens"],
                row["completion_tokens"],
                row["cap_hits"],
                f"{float(row['latency_seconds']):.1f}",
            ]
        )

    with (fair_analysis / "paired_crand_comparison.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        crand = next(csv.DictReader(handle))
    crand_data = [
        ["Comparison", "Both fail", "C_rand only", "Grammar only", "Both pass", "Success counts"],
        [
            "C_rand vs grammar-constrained DeepSeek",
            crand["both_fail"],
            crand["reference_only_success"],
            crand["comparison_only_success"],
            crand["both_succeed"],
            f"{crand['reference_successes']}/96 vs {crand['comparison_successes']}/96",
        ],
    ]
    with (fair_analysis / "validated_signature_distribution.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        signatures = list(csv.DictReader(handle))
    signature_data = [
        ["Realizer signature", "Executable selected", "Validated", "Successful worlds"]
    ]
    for row in signatures:
        signature_data.append(
            [
                row["structural_signature"],
                row["selected_executable_candidates"],
                row["validated_candidates"],
                row["successful_worlds"],
            ]
        )

    return [
        Paragraph("Sensitivity result table", st["h1"]),
        table(summary_data, [39 * mm, 59 * mm, 20 * mm, 17 * mm, 30 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("Paired world-level transitions", st["h1"]),
        table(paired_data, [32 * mm, 32 * mm, 18 * mm, 18 * mm, 18 * mm, 18 * mm, 25 * mm]),
        PageBreak(),
        Paragraph("Complete cumulative gate attrition", st["h1"]),
        table(attrition_data, [39 * mm, 48 * mm, 22 * mm, 19 * mm, 22 * mm, 18 * mm]),
        PageBreak(),
        Paragraph("Model-call and compute ledger", st["h1"]),
        table(ledger_data, [39 * mm, 16 * mm, 17 * mm, 25 * mm, 28 * mm, 23 * mm, 23 * mm]),
        Paragraph(
            "Reasoning-token counts are reported only when exposed by the serving API; reasoning-text availability is not converted into an inferred token count.",
            st["small"],
        ),
        PageBreak(),
        Paragraph("Full Phi-4 completion-budget sensitivity", st["h1"]),
        table(budget_summary_data, [42 * mm, 56 * mm, 20 * mm, 17 * mm, 30 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("Full paired completion-budget transitions", st["h1"]),
        table(
            budget_paired_data,
            [32 * mm, 32 * mm, 18 * mm, 18 * mm, 18 * mm, 18 * mm, 25 * mm],
        ),
        PageBreak(),
        Paragraph("Full Phi-4 completion-budget gate attrition", st["h1"]),
        table(budget_attrition_data, [42 * mm, 47 * mm, 22 * mm, 19 * mm, 22 * mm, 18 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("Full Phi-4 completion-budget compute ledger", st["h1"]),
        table(budget_ledger_data, [46 * mm, 18 * mm, 20 * mm, 29 * mm, 31 * mm, 24 * mm]),
        PageBreak(),
        Paragraph("Grammar-constrained DeepSeek sensitivity", st["h1"]),
        table(fair_family_data, [62 * mm, 26 * mm, 25 * mm, 45 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("Paired comparison with archived random composition", st["h1"]),
        table(crand_data, [45 * mm, 20 * mm, 22 * mm, 23 * mm, 20 * mm, 35 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("Selected-candidate realizer signatures", st["h1"]),
        table(signature_data, [62 * mm, 36 * mm, 30 * mm, 34 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("Grammar-constrained compute ledger", st["h1"]),
        table(fair_ledger_data, [31 * mm, 18 * mm, 31 * mm, 34 * mm, 20 * mm, 29 * mm]),
        PageBreak(),
        Paragraph("Grammar-constrained cumulative attrition", st["h1"]),
        table(fair_attrition_data, [53 * mm, 42 * mm, 22 * mm, 26 * mm, 20 * mm]),
    ]


def realizer_audit_tables(st) -> list:
    analysis = ROOT / "experiments" / "nmi_realizer_audit_v1" / "analysis"
    with (analysis / "condition_summary.csv").open(newline="", encoding="utf-8") as handle:
        summaries = list(csv.DictReader(handle))
    with (analysis / "paired_transitions.csv").open(newline="", encoding="utf-8") as handle:
        transitions = list(csv.DictReader(handle))
    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition = list(csv.DictReader(handle))

    def table(data: list[list[str]], widths: list[float]) -> Table:
        wrapped = [
            [Paragraph(inline_markup(str(cell)), st["small"]) for cell in row] for row in data
        ]
        result = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
        result.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CDD7DD")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F3F6F8")],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return result

    key_policies = {"aligned", "motif_disabled", "role_action_blind_binding"}
    summary_data = [["Source", "Population", "Policy", "Success", "JSR", "Wilson 95% CI"]]
    for row in summaries:
        if row["policy"] not in key_policies:
            continue
        summary_data.append(
            [
                row["source"],
                row["population"],
                row["policy"],
                f"{row['successes']}/{row['worlds']}",
                f"{100 * float(row['jsr']):.1f}%",
                f"{100 * float(row['wilson_95_low']):.1f}-{100 * float(row['wilson_95_high']):.1f}%",
            ]
        )

    mask_data = [
        ["Source", "Masked signature", "Aligned only", "Mask only", "Both pass", "Difference"]
    ]
    for row in transitions:
        if "mask_signature:" not in row["comparison"]:
            continue
        signature = row["comparison"].split("mask_signature:", 1)[1]
        if int(row["aligned_only"]) == 0 and int(row["counterfactual_only"]) == 0:
            continue
        mask_data.append(
            [
                row["source"],
                signature,
                row["aligned_only"],
                row["counterfactual_only"],
                row["both_pass"],
                f"{float(row['paired_jsr_difference']):+.3f}",
            ]
        )

    disabled_gate_data = [["Source", "Stage", "Passed", "Denominator", "Rate"]]
    for row in attrition:
        if row["policy"] != "motif_disabled":
            continue
        disabled_gate_data.append(
            [
                row["source"],
                row["stage"],
                row["passed"],
                row["denominator"],
                publication_rate(row),
            ]
        )

    return [
        PageBreak(),
        Paragraph("Realizer-dependence source data", st["title"]),
        Paragraph("Aligned, disabled and role/action-blind policies", st["h1"]),
        table(summary_data, [28 * mm, 32 * mm, 43 * mm, 19 * mm, 17 * mm, 29 * mm]),
        PageBreak(),
        Paragraph("Leave-one-signature-out paired transitions", st["h1"]),
        table(mask_data, [28 * mm, 51 * mm, 22 * mm, 18 * mm, 22 * mm, 22 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("Motif-disabled cumulative candidate attrition", st["h1"]),
        table(disabled_gate_data, [45 * mm, 25 * mm, 25 * mm, 30 * mm, 25 * mm]),
    ]


def build_pdf() -> Path:
    register_fonts()
    setup_plot()
    TMP.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    analysis = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "analysis"
    manifest_path = analysis / "postprocessing_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("PDF build locked: run minimal sensitivity postprocessing first")
    manifest = json.loads(manifest_path.read_text())
    if (
        manifest.get("status") != "complete_verified"
        or int(manifest.get("replay_mismatches", -1)) != 0
        or int(manifest.get("model_calls_made", -1)) != 0
    ):
        raise ValueError("PDF build locked: sensitivity postprocessing is not verified")
    fair_validation_path = (
        ROOT
        / "experiments"
        / "nmi_fair_interface_v1"
        / "results"
        / "deepseek_fair_cself"
        / "validation.json"
    )
    if not fair_validation_path.is_file():
        raise ValueError("PDF build locked: fair-interface replay is missing")
    fair_validation = json.loads(fair_validation_path.read_text())
    if (
        fair_validation.get("status") != "complete_verified"
        or int(fair_validation.get("replay_mismatches", -1)) != 0
        or int(fair_validation.get("model_calls_made", -1)) != 0
    ):
        raise ValueError("PDF build locked: fair-interface replay is not verified")
    realizer_base = ROOT / "experiments" / "nmi_realizer_audit_v1"
    realizer_validation_path = realizer_base / "results" / "validation.json"
    realizer_analysis_path = realizer_base / "analysis" / "manifest.json"
    if not realizer_validation_path.is_file() or not realizer_analysis_path.is_file():
        raise ValueError("PDF build locked: realizer audit is missing")
    realizer_validation = json.loads(realizer_validation_path.read_text())
    if (
        realizer_validation.get("status") != "complete_verified"
        or not bool(realizer_validation.get("zero_model_calls"))
        or int(realizer_validation.get("aligned_replay_mismatch_count", -1)) != 0
    ):
        raise ValueError("PDF build locked: realizer audit is not verified")
    figs = {
        1: figure_1(),
        2: figure_2(),
        3: figure_3(),
        4: figure_4_editorial(),
        5: figure_5_worked(),
    }
    extended_figs = extended_sensitivity_figures()
    st = styles()

    frame = Frame(
        20 * mm,
        18 * mm,
        A4[0] - 40 * mm,
        A4[1] - 36 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=3 * mm,
        bottomPadding=3 * mm,
    )
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="A prospective assay reveals scaffold-driven hypothesis-space expansion",
        author="Jing-Rung Huang and Wen-Hsiang Lu",
    )
    doc.addPageTemplates(PageTemplate(id="content", frames=[frame], onPage=page_decor))
    story: list = [
        Spacer(1, 18 * mm),
        Paragraph(
            "A prospective assay reveals scaffold-driven hypothesis-space expansion",
            st["manuscript_title"],
        ),
        Paragraph(
            "<b>Jing-Rung Huang</b><sup>1,*</sup> and <b>Wen-Hsiang Lu</b><sup>1</sup>",
            st["body"],
        ),
        Paragraph(
            "<sup>1</sup> Department of Computer Science and Information Engineering, "
            "National Cheng Kung University, Tainan 701, Taiwan",
            st["subtitle"],
        ),
        Paragraph(
            "<sup>*</sup> Corresponding author: Jing-Rung Huang "
            "(p78084063@mail.ncku.edu.tw)<br/>"
            "ORCID: Jing-Rung Huang, 0000-0003-4776-3550; "
            "Wen-Hsiang Lu, 0009-0002-5149-6790",
            st["subtitle"],
        ),
        Rule(75 * mm, colors.HexColor(ORANGE), 3),
        Spacer(1, 8 * mm),
        Paragraph("Article | manuscript for scientific discussion", st["subtitle"]),
    ]
    story.extend(manuscript_story(st, figs))
    story.extend([PageBreak(), Paragraph("Supplementary Information", st["title"]), Paragraph("Contents: Supplementary Methods S1-S18 (including Supplementary Table 1); targeted sensitivity source tables; Extended Data Figures 1-3 (world success, attrition, per-family results); realizer-audit source tables. Conditional rates with no executable candidates are NA.", st["body"])])
    story.extend(markdown_appendix_story(ROOT / "manuscript" / "NMI_SUPPLEMENTARY_METHODS.md", st))
    story.extend([PageBreak(), Paragraph("Targeted sensitivity source data", st["title"])])
    story.extend(
        [
            image_flow(extended_figs["world"]),
            caption(
                "Extended Data Figure 1 | Exact world-level sensitivity results and Wilson 95% intervals, including the separately frozen grammar-constrained interface condition. The asterisk identifies the fixed historical slice of the original n=400 confirmation; the supplied-representation control uses a distinct balanced n=40 subset.",
                st,
            ),
            PageBreak(),
            image_flow(extended_figs["attrition"]),
            caption(
                "Extended Data Figure 2 | Response-to-verdict attrition, including the grammar-constrained interface cascade. Denominators and units change at the executable boundary and are reported in the accompanying source-data tables.",
                st,
            ),
            PageBreak(),
            image_flow(extended_figs["family"]),
            caption(
                "Extended Data Figure 3 | Per-family descriptive sensitivity results. Grammar-constrained-interface successes were confined to meta-law and unification; the supplied-representation control used a different balanced subset. No family-level or candidate-level significance test was performed.",
                st,
            ),
            Spacer(1, 5 * mm),
        ]
    )
    story.extend(sensitivity_tables(st))
    story.extend(realizer_audit_tables(st))
    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    print(build_pdf())
