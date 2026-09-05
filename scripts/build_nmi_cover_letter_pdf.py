"""Build the NMI cover letter PDF from the maintained Markdown source."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "NMI_COVER_LETTER.md"
OUTPUT = ROOT / "output" / "pdf" / "NMI_cover_letter.pdf"


def register_fonts() -> None:
    # Use the PDF-standard Helvetica family so the builder has no external
    # font dependency and renders consistently on the submission system.
    return None


def inline_markup(value: str) -> str:
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
    value = html.escape(value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", value)
    return value.replace("\n", "<br/>")


def read_paragraphs() -> list[str]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    paragraphs: list[str] = []
    buffer: list[str] = []
    for line in lines:
        if not line.strip():
            if buffer:
                paragraphs.append("\n".join(buffer).strip())
                buffer = []
        else:
            buffer.append(line.rstrip())
    if buffer:
        paragraphs.append("\n".join(buffer).strip())
    return paragraphs


def draw_page(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D7DEE5"))
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, height - 17 * mm, width - doc.rightMargin, height - 17 * mm)
    canvas.setFillColor(colors.HexColor("#65727E"))
    canvas.setFont("Helvetica", 8.5)
    canvas.drawRightString(width - doc.rightMargin, 11 * mm, "Cover letter | Nature Machine Intelligence")
    canvas.restoreState()


def build() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=24 * mm,
        rightMargin=24 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
        title="Cover letter - A prospective assay reveals scaffold-driven hypothesis-space expansion",
        author="Jing-Rung Huang, on behalf of both authors",
        subject="Submission cover letter for Nature Machine Intelligence",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="cover")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=draw_page)])

    heading = ParagraphStyle(
        "Heading",
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#17324D"),
        spaceAfter=5 * mm,
    )
    date_style = ParagraphStyle(
        "Date",
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#65727E"),
        spaceAfter=3 * mm,
    )
    body = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=10.6,
        leading=15.3,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#182026"),
        spaceAfter=4.1 * mm,
    )
    sign = ParagraphStyle(
        "Sign",
        fontName="Helvetica",
        fontSize=10.2,
        leading=14.1,
        textColor=colors.HexColor("#182026"),
        spaceAfter=0,
    )

    paragraphs = read_paragraphs()
    story = [
        Paragraph("Cover Letter", heading),
        Paragraph("5 September 2026", date_style),
    ]
    for index, paragraph in enumerate(paragraphs):
        if index == 5:
            story.append(PageBreak())
        style = sign if index >= len(paragraphs) - 1 else body
        story.append(Paragraph(inline_markup(paragraph), style))
    doc.build(story)


if __name__ == "__main__":
    build()
