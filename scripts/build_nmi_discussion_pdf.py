"""Build a discussion-ready NMI manuscript PDF from frozen publication artifacts."""

from __future__ import annotations

import csv
import html
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
    ax.axvline(3, color=CYAN, ls="--", lw=1.5)
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
        "Canonical membership failure proves R is outside H(R0)",
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
        "Figure 1 | A prospective assay for bounded representation escape",
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
    labels = ["B0\nDirect", "B1\nSampled", "B2\nFixed", "B3\nAttribute", "B4\nTyped", "B5\nFull"]
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
    ax.set_xticks(np.arange(6), labels)
    ax.set_ylabel("Jump success rate (%)")
    ax.set_ylim(0, 46)
    ax.set_title("World-level AJ5 success", pad=9)
    panel_label(ax, "a")

    ax = axes[0, 1]
    fact_labels = ["P0\nLLM", "P1\nExternal", "P2\nOracle"]
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
    ax.plot(slots, np.array([53, 101, 142]) / 4, marker="o", lw=2.5, color=BLUE, label="B4 typed")
    ax.plot(slots, np.array([58, 96, 142]) / 4, marker="o", lw=2.5, color=ORANGE, label="B5 full")
    for x0, a, b in zip(slots, [53, 101, 142], [58, 96, 142], strict=True):
        ax.text(x0 - 0.05, a / 4 + 2.2, str(a), color=BLUE, fontsize=8, ha="right")
        ax.text(x0 + 0.05, b / 4 - 3.8, str(b), color=ORANGE, fontsize=8, ha="left")
    ax.set_xticks(slots)
    ax.set_xlabel("Candidate slots used")
    ax.set_ylabel("Successful worlds (%)")
    ax.set_ylim(0, 43)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Success by candidate opportunity", pad=9)
    panel_label(ax, "c")

    ax = axes[1, 1]
    gates = ["J0", "J1", "J2", "J3", "J4", "J5"]
    b4 = [1200, 823, 573, 270, 154, 154]
    b5 = [1200, 838, 562, 262, 145, 145]
    x = np.arange(len(gates))
    ax.plot(x, np.array(b4) / 12, marker="o", lw=2.2, color=BLUE, label="B4")
    ax.plot(x, np.array(b5) / 12, marker="o", lw=2.2, color=ORANGE, label="B5")
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
        "C0",
        "C1*",
        "C2",
        "C3",
        "Cself",
        "Crand",
        "C5*",
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
    ax.set_xticks(np.arange(7), labels)
    ax.set_ylabel("Jump success rate (%)")
    ax.set_ylim(0, 116)
    ax.set_title("Generic composition reaches every known-family world")
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
    ax.bar(x - w / 2, c1, w, color=GOLD, label="C1 atomic reference")
    ax.bar(x + w / 2, c3, w, color=ORANGE, label="C3 generic composition")
    ax.set_xticks(x, names, fontsize=7.3, rotation=24, ha="right")
    ax.set_ylim(0, 112)
    ax.set_ylabel("Jump success rate (%)")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.set_title("C3 saturates all eight generators; C1 varies by family", pad=10)
    panel_label(ax, "c")
    fig.suptitle(
        "Figure 3 | Generic rewrites compose into validated representations",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.text(
        0.98,
        0.015,
        "Retained jump gain rho = 3.053 (95% CI 2.685-3.540)",
        ha="right",
        fontsize=8,
        color=NAVY,
        weight="bold",
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
    positions = {
        "x1": (0.12, 0.72),
        "x2": (0.12, 0.5),
        "x3": (0.12, 0.28),
        "r3": (0.53, 0.5),
        "y": (0.88, 0.5),
    }
    for key in ("x1", "x2", "x3"):
        ax.add_patch(Circle(positions[key], 0.055, fc=LIGHT, ec=BLUE, lw=1.5))
        ax.text(*positions[key], key, ha="center", va="center")
        ax.add_patch(
            FancyArrowPatch((0.18, positions[key][1]), (0.46, 0.5), arrowstyle="->", color=GREY)
        )
    ax.add_patch(
        FancyBboxPatch(
            (0.46, 0.4), 0.14, 0.2, boxstyle="round,pad=0.02", fc="#FFF3E8", ec=ORANGE, lw=2
        )
    )
    ax.text(0.53, 0.5, "arity-3\nrelation", ha="center", va="center", weight="bold", color=NAVY)
    ax.add_patch(FancyArrowPatch((0.61, 0.5), (0.82, 0.5), arrowstyle="->", color=GREY))
    ax.add_patch(Circle(positions["y"], 0.06, fc=LIGHT, ec=NAVY, lw=1.5))
    ax.text(*positions["y"], "y", ha="center", va="center")
    ax.text(
        0.5,
        0.12,
        "reify edge -> change arity -> bind arguments",
        ha="center",
        color=NAVY,
        weight="bold",
    )
    ax.set_title("Held-out triadic relation needs multiple rewrites")
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
    ax.set_title("Composition transfers; random paths rarely do")
    panel_label(ax, "b")

    analysis = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "analysis"
    with (analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summary_rows = list(csv.DictReader(handle))
    sensitivity_order = [
        "historical_phi4_4bit_cself",
        "phi8_cself",
        "deepseek_matched_cself",
        "deepseek_native_cself",
        "phi8_cself_repair",
        "deepseek_p2",
    ]
    sensitivity_labels = ["Phi4\n4-bit*", "Phi4\n8-bit", "DS\nmatched", "DS\nnative", "Phi4\nrepair", "DS\nP2†"]
    summary_lookup = {row["condition"]: row for row in summary_rows}
    sensitivity_values = np.array([float(summary_lookup[name]["jsr"]) for name in sensitivity_order]) * 100
    sensitivity_low = np.array([float(summary_lookup[name]["wilson_95_low"]) for name in sensitivity_order]) * 100
    sensitivity_high = np.array([float(summary_lookup[name]["wilson_95_high"]) for name in sensitivity_order]) * 100
    ax = axes[1, 0]
    sx = np.arange(len(sensitivity_order))
    ax.bar(sx, sensitivity_values, color=[GREY, BLUE, BLUE, ORANGE, RED, "#009E73"], width=0.7)
    ax.errorbar(
        sx,
        sensitivity_values,
        yerr=[np.maximum(0, sensitivity_values - sensitivity_low), np.maximum(0, sensitivity_high - sensitivity_values)],
        fmt="none",
        ecolor=INK,
        capsize=2.5,
        lw=1,
    )
    for index, name in enumerate(sensitivity_order):
        row = summary_lookup[name]
        ax.text(index, min(108, sensitivity_values[index] + 4), f'{row["successes"]}/{row["worlds"]}', ha="center", fontsize=6.8)
    ax.axvline(4.5, color="#A0A0A0", linestyle="--", linewidth=0.8)
    ax.set_xticks(sx, sensitivity_labels)
    ax.set_ylim(0, 116)
    ax.set_ylabel("World-level JSR (%)")
    ax.set_title("Fixed-panel targeted sensitivity")
    panel_label(ax, "c")

    ax = axes[1, 1]
    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition_rows = list(csv.DictReader(handle))
    stage_aliases = {
        "response_returned": "response", "request_returned": "response",
        "parse_valid": "parse", "json_parse_valid": "parse",
        "schema_valid": "schema", "plan_schema_valid": "schema",
        "operation_valid": "operation", "operation_names_valid": "operation",
        "argument_type_valid": "types", "argument_types_valid": "types",
        "executable": "execute", "J1": "J1", "J2": "J2", "J3": "J3", "J4": "J4", "J5": "J5",
    }
    attrition_stages = ["response", "parse", "schema", "operation", "types", "execute", "J1", "J2", "J3", "J4", "J5"]
    attrition_lookup: dict[str, dict[str, float]] = {}
    for row in attrition_rows:
        stage = stage_aliases.get(row["stage"])
        if stage:
            attrition_lookup.setdefault(row["condition"], {})[stage] = float(row["rate"]) * 100
    line_conditions = sensitivity_order[:-1]
    line_labels = ["Phi4 4-bit*", "Phi4 8-bit", "DS matched", "DS native", "Phi4 repair"]
    line_colours = [GREY, BLUE, CYAN, ORANGE, RED]
    tx = np.arange(len(attrition_stages))
    for name, label, colour in zip(line_conditions, line_labels, line_colours, strict=True):
        ax.plot(tx, [attrition_lookup[name].get(stage, np.nan) for stage in attrition_stages], marker="o", ms=2.4, lw=1.25, color=colour, label=label)
    ax.set_xticks(tx, attrition_stages, rotation=38, ha="right", fontsize=6.5)
    ax.set_ylim(-3, 106)
    ax.set_ylabel("Passing stage (%)")
    ax.legend(frameon=False, fontsize=5.8, ncol=2, loc="upper right")
    ax.text(0.02, 0.04, "Model-free C3 replay: 2,400/2,400 gate matches", transform=ax.transAxes, fontsize=6.2, color=NAVY)
    ax.set_title("Response-to-verdict attrition")
    panel_label(ax, "d")
    fig.suptitle(
        "Figure 4 | Transfer, replay and targeted model sensitivity",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=2.0, w_pad=1.5)
    return save_figure(fig, "figure_4_sensitivity.png")


def figure_5() -> Path:
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    ax.axis("off")
    stages = [
        (0.02, 0.61, 0.16, 0.25, "Observations", "x=z=w\ny=9x^3", BLUE),
        (0.22, 0.61, 0.16, 0.25, "Incumbent", "y = 9x^3\nexact fit", GREY),
        (0.42, 0.57, 0.20, 0.33, "Four rewrites", "1 reify edge\n2 arity -> 3\n3 bind z\n4 bind w", ORANGE),
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
        (0.68, "Independent falsification", "z=5 -> 1,620\ncandidate exact", CYAN),
    ]
    for x0, title, body, colour in outcomes:
        ax.add_patch(
            FancyBboxPatch((x0, 0.16), 0.22, 0.24, boxstyle="round,pad=0.02", fc=LIGHT, ec=colour, lw=1.6)
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
    canvas.drawString(20 * mm, height - 11.5 * mm, "NMI MANUSCRIPT WITH FIGURES | 3 SEPTEMBER 2026")
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
    canvas.drawString(20 * mm, 11 * mm, "Nature Machine Intelligence Article format | not yet submitted")
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
        ["Evaluation", "Exec", "Frozen", "Non-member", "Prospective", "Falsify", "Attribution / replay", "Breadth"],
        ["Hypothesis Search / HypoGen", "partial", "no", "no", "no", "no", "no", "language tasks"],
        ["POPPER", "partial", "no", "no", "yes", "yes", "limited", "literature"],
        ["FunSearch", "yes", "skeleton", "no", "feedback", "tests", "proposer/evaluator", "mathematics"],
        ["PiEvo", "yes", "evolving", "no", "varies", "varies", "proposer/search", "4 benchmarks"],
        ["Model Discovery Agent", "yes", "open set", "no", "Bayesian", "predictive", "proposer/inference", "3 sciences"],
        ["HypoArena", "judged", "no", "no", "context", "rubric", "no", "988 / 6 / 15"],
        ["EvoSCM", "yes", "evolving", "no", "active", "prospective", "evolution/selection", "causal systems"],
        ["This work", "yes", "yes", "canonical", "locked", "exact", "factorial / exact", "9 families / 1 model"],
    ]
    wrapped = [[Paragraph(inline_markup(str(cell)), st["small"]) for cell in row] for row in data]
    table = Table(
        wrapped,
        colWidths=[27 * mm, 14 * mm, 17 * mm, 20 * mm, 20 * mm, 17 * mm, 31 * mm, 25 * mm],
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

    def flush() -> None:
        if paragraph:
            content = " ".join(item.strip() for item in paragraph)
            paragraph.clear()
            if "[" in content and "REQUIRED BEFORE SUBMISSION" in content:
                return
            story.append(Paragraph(inline_markup(content), st["body"]))

    for line in lines:
        stripped = line.strip()
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
            if heading in {
                "Acknowledgements",
                "Author contributions",
                "Competing interests",
                "Correspondence",
            }:
                break
            if heading == "Abstract":
                story.append(Paragraph("Abstract", st["h1"]))
            elif heading == "Results":
                story.append(Paragraph("Results", st["h1"]))
            else:
                story.append(Paragraph(inline_markup(heading), st["h1"]))
        elif stripped.startswith("### "):
            flush()
            heading = stripped[4:]
            if heading.startswith("Table 1 |"):
                story.extend([Paragraph(inline_markup(heading), st["h2"]), literature_table(st)])
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
                            "Figure 1 | The assay combines canonical structural non-membership with a prospective intervention and independent falsification. Panel a is schematic; panels b-d summarize the registered pipeline.",
                            st,
                        ),
                    ]
                )
                inserted.add(1)
            elif (
                heading == "Typed proposals outperform fixed-space alternatives"
                and 2 not in inserted
            ):
                story.extend(
                    [
                        image_flow(figures[2]),
                        caption(
                            "Figure 2 | AJ5 world-level jump success. Error bars are registered family-stratified bootstrap 95% intervals. Counts are successful worlds; n=400 per jump condition. All conditions recorded 0/200 false jumps.",
                            st,
                        ),
                    ]
                )
                inserted.add(2)
            elif (
                heading == "Generic rewrites compose into validated representations"
                and 3 not in inserted
            ):
                story.extend(
                    [
                        image_flow(figures[3]),
                        caption(
                            "Figure 3 | CJ5 known-family reconstruction. Error bars in panel b are Wilson 95% intervals; n=400 worlds per condition. C1 and C5 are reference conditions with different operation semantics. Per-family panels contain 50 worlds each.",
                            st,
                        ),
                    ]
                )
                inserted.add(3)
            elif heading == "A deterministic component audit removes the language model" and 4 not in inserted:
                story.extend(
                    [
                        image_flow(figures[4]),
                        caption(
                            "Figure 4 | Held-out transfer, deterministic replay and the minimal targeted sensitivity extension. Panel c reports the fixed 96-world paired panel, except the predeclared n=40 supplied-representation control. Error bars are Wilson 95% intervals. Panel d uses plan-opportunity rates for new C_self conditions and response-level rates for the historical interface; historical parse validity denotes legacy object extraction, not strict whole-response JSON. No candidate-level significance tests were performed.",
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
                            "Figure 5 | Worked held-out example. Correlated observations make the cubic incumbent and triadic candidate observationally identical. A committed intervention separates them before outcome reveal, and an independent case falsifies the incumbent.",
                            st,
                        ),
                    ]
                )
                inserted.add(5)
        elif not stripped:
            flush()
        elif stripped.startswith("**["):
            continue
        else:
            paragraph.append(stripped)
    flush()
    return story


def markdown_appendix_story(path: Path, st) -> list:
    story: list = []
    paragraph: list[str] = []
    in_fence = False

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), st["body"]))
            paragraph.clear()

    for raw in path.read_text().splitlines():
        line = raw.strip()
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
            story.append(Paragraph(inline_markup(line[2:]), st["body"], bulletText="•"))
        elif not line:
            flush()
        elif line.startswith("|"):
            continue
        else:
            paragraph.append(line)
    flush()
    return story


def sensitivity_tables(st) -> list:
    analysis = ROOT / "experiments" / "nmi_minimal_sensitivity_v1" / "analysis"
    with (analysis / "world_summary.csv").open(newline="", encoding="utf-8") as handle:
        summaries = list(csv.DictReader(handle))
    summary_data = [["Condition", "Population", "Success", "JSR", "Wilson 95% CI"]]
    for row in summaries:
        summary_data.append(
            [
                row["condition"].replace("_", " "),
                row["population"],
                f'{row["successes"]}/{row["worlds"]}',
                f'{100 * float(row["jsr"]):.1f}%',
                f'{100 * float(row["wilson_95_low"]):.1f}-{100 * float(row["wilson_95_high"]):.1f}%',
            ]
        )
    def table(data: list[list[str]], widths: list[float]) -> Table:
        wrapped = [[Paragraph(inline_markup(str(cell)), st["small"]) for cell in row] for row in data]
        result = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
        result.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CDD7DD")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
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
    paired_data = [["Reference", "Comparison", "Both fail", "Both pass", "New only", "Old only", "JSR difference"]]
    for row in paired:
        paired_data.append(
            [
                row["reference"].replace("_", " "),
                row["comparison"].replace("_", " "),
                row["both_fail"],
                row["both_succeed"],
                row["comparison_only_success"],
                row["reference_only_success"],
                f'{float(row["paired_jsr_difference"]):+.3f}',
            ]
        )

    with (analysis / "gate_attrition.csv").open(newline="", encoding="utf-8") as handle:
        attrition = list(csv.DictReader(handle))
    attrition_data = [["Condition", "Unit", "Stage", "Passed", "Denominator", "Rate"]]
    for row in attrition:
        attrition_data.append(
            [
                row["condition"].replace("_", " "),
                row.get("unit", ""),
                row["stage"],
                row["passed"],
                row["denominator"],
                f'{100 * float(row["rate"]):.1f}%',
            ]
        )

    with (analysis / "compute_ledger.csv").open(newline="", encoding="utf-8") as handle:
        ledger = list(csv.DictReader(handle))
    ledger_data = [["Condition", "Calls", "Attempts", "Prompt tokens", "Completion tokens", "Reasoning text", "Latency (s)"]]
    for row in ledger:
        ledger_data.append(
            [
                row["condition"].replace("_", " "),
                row["llm_calls"],
                row["transport_attempts"],
                row["prompt_tokens"],
                row["completion_tokens"],
                row["reasoning_text_available_calls"],
                f'{float(row["latency_seconds_sum"]):.1f}',
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
    ]


def build_pdf() -> Path:
    from abductive_jump.minimal_sensitivity_reports import build as build_sensitivity_reports

    register_fonts()
    setup_plot()
    TMP.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    build_sensitivity_reports(ROOT)
    figs = {1: figure_1(), 2: figure_2(), 3: figure_3(), 4: figure_4(), 5: figure_5()}
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
        title="A prospective assay for hypothesis-space expansion in AI systems",
        author="Complete scientific discussion copy",
    )
    doc.addPageTemplates(PageTemplate(id="content", frames=[frame], onPage=page_decor))
    story: list = [
        Spacer(1, 18 * mm),
        Paragraph("A prospective assay for hypothesis-space expansion in AI systems", st["manuscript_title"]),
        Rule(75 * mm, colors.HexColor(ORANGE), 3),
        Spacer(1, 8 * mm),
        Paragraph("Article | manuscript for scientific discussion", st["subtitle"]),
    ]
    story.extend(manuscript_story(st, figs))
    story.extend([PageBreak(), Paragraph("Supplementary Information", st["title"])])
    story.extend(markdown_appendix_story(ROOT / "manuscript" / "NMI_SUPPLEMENTARY_METHODS.md", st))
    story.extend([PageBreak(), Paragraph("Targeted sensitivity source data", st["title"])])
    sensitivity_figures = ROOT / "reports" / "figures" / "minimal_sensitivity"
    story.extend(
        [
            image_flow(sensitivity_figures / "figure1-world-jsr.png"),
            caption("Extended Data Figure 8a | Exact world-level sensitivity results and Wilson 95% intervals. The supplied-representation control uses a distinct balanced n=40 subset.", st),
            PageBreak(),
            image_flow(sensitivity_figures / "figure2-gate-attrition.png"),
            caption("Extended Data Figure 8b | Response-to-verdict attrition. Denominators and units are reported in the accompanying source-data tables.", st),
            PageBreak(),
            image_flow(sensitivity_figures / "figure3-per-family.png"),
            caption("Extended Data Figure 8c | Per-family descriptive sensitivity results; no family-level or candidate-level significance test was performed.", st),
            Spacer(1, 5 * mm),
        ]
    )
    story.extend(sensitivity_tables(st))
    story.extend([PageBreak(), Paragraph("Protocol and claim audit", st["title"])])
    story.extend(markdown_appendix_story(ROOT / "docs" / "publication" / "NMI_CLAIM_MATRIX.md", st))
    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    print(build_pdf())
