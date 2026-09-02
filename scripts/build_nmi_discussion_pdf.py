"""Build a discussion-ready NMI manuscript PDF from frozen publication artifacts."""

from __future__ import annotations

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
OUTPUT = ROOT / "output" / "pdf" / "NMI_discussion_draft.pdf"

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
    ax.text(-0.08, 1.05, label, transform=ax.transAxes, weight="bold", fontsize=12)


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
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.8))

    ax = axes[0]
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
    for i, (v, count) in enumerate(zip(vals, counts, strict=True)):
        ax.text(i, v * 100 + 3.8, f"{count}/400", ha="center", fontsize=7.5)
    ax.set_xticks(np.arange(6), labels)
    ax.set_ylabel("Jump success rate (%)")
    ax.set_ylim(0, 46)
    ax.set_title("Typed proposals outperform fixed-space alternatives")
    panel_label(ax, "a")

    ax = axes[1]
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
    ax.set_title("Only the representation source changes")
    panel_label(ax, "b")

    ax = axes[2]
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
    ax.set_title("Success grows with registered opportunities")
    panel_label(ax, "c")
    fig.suptitle(
        "Figure 2 | Representation proposals separate from reasoning",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92), w_pad=1.5)
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
        "C0\nFixed",
        "C1\nAtomic*",
        "C2\nDepth 1",
        "C3\nCompose",
        "Cself\nLLM",
        "Crand\nRandom",
        "C5\nOracle*",
    ]
    values = np.array([lookup[k]["jsr"] for k in order]) * 100
    low = np.array([lookup[k]["jsr_ci_low"] for k in order]) * 100
    high = np.array([lookup[k]["jsr_ci_high"] for k in order]) * 100
    fig = plt.figure(figsize=(10.4, 6.0))
    grid = fig.add_gridspec(
        2, 2, height_ratios=[0.8, 1.2], width_ratios=[0.38, 0.62], hspace=0.42, wspace=0.28
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
    for i, (v, count) in enumerate(zip(values, counts, strict=True)):
        ax.text(i, v + 4, f"{count}/400", ha="center", fontsize=7.2)
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
    names = [r["family"].replace("_", "\n") for r in fam]
    c1 = np.array([r["c1_jsr"] for r in fam]) * 100
    c3 = np.array([r["c3_jsr"] for r in fam]) * 100
    x = np.arange(len(names))
    w = 0.36
    ax.bar(x - w / 2, c1, w, color=GOLD, label="C1 atomic reference")
    ax.bar(x + w / 2, c3, w, color=ORANGE, label="C3 generic composition")
    ax.set_xticks(x, names, fontsize=7.3)
    ax.set_ylim(0, 112)
    ax.set_ylabel("Jump success rate (%)")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.text(
        0.99,
        0.08,
        "retained jump gain rho = 3.053\n95% CI 2.685-3.540",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color=NAVY,
        weight="bold",
    )
    ax.set_title("C3 succeeds across all eight structural families")
    panel_label(ax, "c")
    fig.suptitle(
        "Figure 3 | Generic rewrites compose into validated representations",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.93))
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

    ax = axes[1, 0]
    categories = ["Depth-one\nalternatives", "Successful C3\ncandidates"]
    rates = [0, 100]
    bars = ax.bar(categories, rates, color=[GREY, ORANGE], width=0.56)
    ax.set_ylim(0, 116)
    ax.set_ylabel("Validated / observed (%)")
    ax.text(bars[0].get_x() + bars[0].get_width() / 2, 4, "0 / 17,280", ha="center", fontsize=8)
    ax.text(
        bars[1].get_x() + bars[1].get_width() / 2,
        104,
        "all at registered depth 4",
        ha="center",
        fontsize=8,
    )
    ax.set_title("Depth is bounded within the registered system")
    panel_label(ax, "c")

    ax = axes[1, 1]
    ax.axis("off")
    cards = [
        ("0 / 300", "C3 false jumps"),
        ("10,800 / 10,800", "AJ5 exact replay"),
        ("16,800 / 16,800", "CJ5 exact replay"),
        ("0", "exclusions or shard reruns"),
    ]
    for i, (number, label) in enumerate(cards):
        row, col = divmod(i, 2)
        x0, y0 = 0.03 + col * 0.5, 0.57 - row * 0.42
        ax.add_patch(
            FancyBboxPatch(
                (x0, y0), 0.44, 0.31, boxstyle="round,pad=0.02", fc=LIGHT, ec=BLUE, lw=1.3
            )
        )
        ax.text(
            x0 + 0.22,
            y0 + 0.2,
            number,
            ha="center",
            va="center",
            fontsize=13,
            weight="bold",
            color=NAVY,
        )
        ax.text(x0 + 0.22, y0 + 0.08, label, ha="center", va="center", fontsize=8)
    ax.set_title("The complete audit trail reproduces")
    panel_label(ax, "d")
    fig.suptitle(
        "Figure 4 | Held-out transfer, specificity and audit trail",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=2.0, w_pad=1.5)
    return save_figure(fig, "figure_4_heldout.png")


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
    canvas.drawString(20 * mm, height - 11.5 * mm, "NMI DISCUSSION DRAFT | 2 SEPTEMBER 2026")
    canvas.drawRightString(width - 20 * mm, 11 * mm, f"{doc.page}")
    canvas.drawString(20 * mm, 11 * mm, "Not for submission - figures redraw frozen results")
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


def manuscript_story(st, figures: dict[int, Path]) -> list:
    text = (ROOT / "manuscript" / "NMI_MANUSCRIPT.md").read_text()
    lines = text.splitlines()
    story: list = []
    paragraph: list[str] = []
    inserted: set[int] = set()

    def flush() -> None:
        if paragraph:
            content = " ".join(item.strip() for item in paragraph)
            paragraph.clear()
            if "[" in content and "REQUIRED BEFORE SUBMISSION" in content:
                return
            story.append(Paragraph(inline_markup(content), st["body"]))

    for line in lines:
        stripped = line.strip()
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
                story.extend([PageBreak(), Paragraph("Results", st["h1"])])
            else:
                story.append(Paragraph(inline_markup(heading), st["h1"]))
        elif stripped.startswith("### "):
            flush()
            heading = stripped[4:]
            story.append(Paragraph(inline_markup(heading), st["h2"]))
            if (
                heading == "A prospective criterion for representation-level escape"
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
                heading == "Typed representation proposals outperform fixed-space alternatives"
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
            elif (
                heading == "Composition transfers to a held-out structural family"
                and 4 not in inserted
            ):
                story.extend(
                    [
                        image_flow(figures[4]),
                        caption(
                            "Figure 4 | Held-out structural-family result and integrity checks. Error bars in panel b are Wilson 95% intervals; n=100 worlds per condition. The hold-out is structurally new but conceptually adjacent to prior binary relation reification.",
                            st,
                        ),
                    ]
                )
                inserted.add(4)
        elif not stripped:
            flush()
        elif stripped.startswith("**["):
            continue
        else:
            paragraph.append(stripped)
    flush()
    return story


def build_pdf() -> Path:
    register_fonts()
    setup_plot()
    TMP.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figs = {1: figure_1(), 2: figure_2(), 3: figure_3(), 4: figure_4()}
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
        title="Measuring representation change in language-model discovery",
        author="Discussion draft",
    )
    doc.addPageTemplates(PageTemplate(id="content", frames=[frame], onPage=page_decor))

    story: list = [
        Spacer(1, 36 * mm),
        Paragraph("DISCUSSION DRAFT", st["subtitle"]),
        Paragraph("Measuring representation change in language-model discovery", st["title"]),
        Rule(75 * mm, colors.HexColor(ORANGE), 3),
        Spacer(1, 10 * mm),
        Paragraph(
            "A preregistered, prospective benchmark of bounded hypothesis-space escape",
            st["subtitle"],
        ),
        Spacer(1, 18 * mm),
        Paragraph("The central result", st["h1"]),
        Spacer(1, 3 * mm),
        Paragraph(
            "A frozen language model can participate in prospectively validated representation change when embedded in a transparent typed search scaffold. The evidence applies to the tested model, interface and synthetic worlds - not to autonomous scientific discovery or human-like creativity.",
            st["callout"],
        ),
        Spacer(1, 12 * mm),
        Paragraph("Prepared for scientific discussion | 2 September 2026", st["subtitle"]),
        Paragraph(
            "Status: conditionally ready. Numbers are audited; author metadata, archival DOI and final production figures remain pre-submission actions.",
            st["small"],
        ),
        PageBreak(),
        Paragraph("Discussion overview", st["h1"]),
        Paragraph("What the experiments establish", st["h2"]),
        Paragraph(
            "AJ5 validates the assay: typed external proposals succeed in 142/400 worlds, while direct, sampling-matched, fixed-space and attribute-only conditions succeed in 0-1/400. CJ5 removes atomic family answers: generic four-step compositions succeed in 400/400 known-family and 100/100 held-out structural-family worlds.",
            st["body"],
        ),
        Paragraph("What makes the comparison informative", st["h2"]),
        Paragraph(
            "The incumbent grammar is frozen, the best incumbent predictor is explicit, interventions are committed before outcomes are observed, and every candidate must pass six deterministic gates. Proposal source changes while the reasoning path and final candidate opportunity remain controlled.",
            st["body"],
        ),
        Paragraph("What the experiments do not establish", st["h2"]),
        Paragraph(
            "The study does not show unrestricted scientific discovery, independent model creativity or concept-free invention. Generic primitives and search strata are supplied by the researchers; the held-out family is structurally new but conceptually adjacent; and C3 saturation indicates a well-aligned synthetic benchmark.",
            st["body"],
        ),
        Spacer(1, 5 * mm),
        Paragraph("Headline evidence", st["h2"]),
    ]
    headline = [
        ["Phase", "Focal result", "Strong comparator", "Specificity", "Replay"],
        [
            "AJ5",
            "142/400 B4 and B5",
            "0-1/400 B0-B3",
            "0/200 controls per condition",
            "10,800/10,800",
        ],
        [
            "CJ5 known",
            "400/400 C3",
            "52/400 random; 0/400 self",
            "0/200 C3 controls",
            "part of 16,800/16,800",
        ],
        [
            "CJ5 held out",
            "100/100 C3",
            "13/100 random; 0/100 self",
            "0/100 C3 controls",
            "part of 16,800/16,800",
        ],
    ]
    headline_wrapped = [
        [Paragraph(inline_markup(cell), st["small"]) for cell in row] for row in headline
    ]
    htable = Table(
        headline_wrapped, colWidths=[25 * mm, 39 * mm, 42 * mm, 40 * mm, 31 * mm], repeatRows=1
    )
    htable.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CDD7DD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend(
        [
            htable,
            Spacer(1, 8 * mm),
            Paragraph("Controlled comparison design", st["h2"]),
            design_table(st),
            Paragraph(
                "* C1 and C5 are conditional references; their operation semantics are not treated as compute-equivalent to C3.",
                st["small"],
            ),
            PageBreak(),
            Paragraph("Visual results", st["h1"]),
            image_flow(figs[1]),
            caption(
                "Figure 1 | Bounded representation-level escape requires structural non-membership, observational adequacy, prospective intervention gain and independent falsification. The visual is a discussion schematic derived from the registered protocol.",
                st,
            ),
            PageBreak(),
            image_flow(figs[2]),
            caption(
                "Figure 2 | AJ5 world-level results. Exact counts and registered uncertainty are drawn from condition_summary.parquet and final_verdict.json.",
                st,
            ),
            PageBreak(),
            image_flow(figs[3]),
            caption(
                "Figure 3 | CJ5 known-family results. Generic composition separates from fixed, depth-one, self-composition and random controls.",
                st,
            ),
            PageBreak(),
            image_flow(figs[4]),
            caption(
                "Figure 4 | Held-out structural-family results, registered depth bounds and deterministic replay. Zero accepted controls is finite-sample evidence, not proof of zero risk.",
                st,
            ),
            PageBreak(),
            Paragraph("Manuscript draft", st["title"]),
            Paragraph(
                "Formatted from the audited NMI manuscript source. Figures are repeated at their relevant Results subsections for discussion in context.",
                st["subtitle"],
            ),
        ]
    )
    story.extend(manuscript_story(st, figs))
    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    print(build_pdf())
