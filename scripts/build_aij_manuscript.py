"""Render AIJ Markdown and its supplement without altering frozen evidence."""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, mathtext
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/AIJ_manuscript_and_supplement.pdf"
TMP = ROOT / "tmp/pdfs/aij"
WIDTH = A4[0] - 40 * mm
INK = colors.HexColor("#192b3b")


def register_fonts():
    for name, weight, style in [("Article", "normal", "normal"), ("Article-Bold", "bold", "normal"), ("Article-Italic", "normal", "oblique"), ("Article-BoldItalic", "bold", "oblique")]:
        path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight=weight, style=style))
        pdfmetrics.registerFont(TTFont(name, path))
    pdfmetrics.registerFontFamily("Article", normal="Article", bold="Article-Bold", italic="Article-Italic", boldItalic="Article-BoldItalic")


def inline(value):
    value = value.translate(str.maketrans({"–":"-", "—":"-", "‑":"-", "−":"-"}))
    value = html.escape(value)
    value = re.sub(r"\b([DLG])_(obs|int|fal)\b",r"\1<sub>\2</sub>",value)
    value = re.sub(r"`([^`]+)`", r'<font color="#324d62">\1</font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"<i>\1</i>", value)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#285b7a">\1</link>', value)
    # Plain URLs remain visible and clickable; long tokens may wrap.
    value = re.sub(r'(?<!["=])(https?://[^\s<]+)', lambda m: '<link href="'+m[1]+'" color="#285b7a">'+m[1]+'</link>', value) if '<link' not in value else value
    return value


def styles():
    base = dict(fontName="Article", fontSize=9.5, leading=14, textColor=INK, spaceAfter=7, splitLongWords=True, allowWidows=0, allowOrphans=0)
    body = ParagraphStyle("body", **base, alignment=TA_JUSTIFY)
    return {
        "body":body,
        "title":ParagraphStyle("title", parent=body, fontName="Article-Bold", fontSize=18, leading=23, alignment=0, spaceAfter=16),
        "h2":ParagraphStyle("h2", parent=body, fontName="Article-Bold", fontSize=12.5, leading=17, alignment=0, spaceBefore=13, spaceAfter=8, keepWithNext=True),
        "h3":ParagraphStyle("h3", parent=body, fontName="Article-Bold", fontSize=10.5, leading=15, alignment=0, spaceBefore=10, keepWithNext=True),
        "caption":ParagraphStyle("caption", parent=body, fontSize=8, leading=11.5, alignment=0, spaceAfter=10),
        "cell":ParagraphStyle("cell", parent=body, fontSize=8, leading=11.5, alignment=0, spaceAfter=0),
        "ref":ParagraphStyle("ref", parent=body, fontSize=8.5, leading=12.5, alignment=0, leftIndent=18, firstLineIndent=-18, spaceAfter=5),
        "list":ParagraphStyle("list", parent=body, leftIndent=11, firstLineIndent=-8, alignment=0),
        "code":ParagraphStyle("code", parent=body, fontSize=8.2, leading=12, alignment=0, leftIndent=10, rightIndent=10, backColor=colors.HexColor("#f1f4f6"), borderPadding=7),
    }


def picture(path, max_height=104*mm):
    with PILImage.open(path) as im:
        w,h=im.size
    factor=min(WIDTH/w,max_height/h)
    return Image(str(path),width=w*factor,height=h*factor,hAlign="CENTER")


def markdown(path, s):
    lines=path.read_text().splitlines(); story=[]; i=0; refs=False; equations=0
    while i<len(lines):
        line=lines[i].strip(); i+=1
        if not line: continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]),s["title"])); continue
        if line.startswith("## "):
            refs=line=="## References"
            story.append(Paragraph(inline(line[3:]),s["h2"])); continue
        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:]),s["h3"])); continue
        if line==r"\[":
            math=[]
            while lines[i].strip()!=r"\]": math.append(lines[i].strip()); i+=1
            i+=1; equations+=1
            expression=" ".join(math).replace(r"\bigl","").replace(r"\bigr","").rstrip(".")
            expression=expression.replace(r"\mathcal P",r"\mathcal{P}").replace(r"\mathcal U",r"\mathcal{U}")
            target=TMP/f"equation_{equations}.png"
            mathtext.math_to_image("$"+expression+"$",str(target),dpi=240,prop=font_manager.FontProperties(size=13),color="#192b3b")
            preceding=story.pop()
            story.append(KeepTogether([preceding,Spacer(1,5),picture(target,13*mm),Spacer(1,9)])); continue
        if line.startswith("!["):
            match=re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)",line); assert match,line
            while i<len(lines) and not lines[i].strip(): i+=1
            caption=lines[i].strip(); assert caption.startswith("Figure "),caption; i+=1
            story.append(KeepTogether([Spacer(1,5),picture(path.parent/match[2]),Spacer(1,5),Paragraph(inline(caption),s["caption"])])); continue
        if line.startswith("|"):
            rows=[line]
            while i<len(lines) and lines[i].strip().startswith("|"): rows.append(lines[i].strip()); i+=1
            values=[[cell.strip() for cell in row.strip("|").split("|")] for row in rows if not re.fullmatch(r"[| :\-]+",row)]
            n=len(values[0]); assert all(len(r)==n for r in values)
            widths={2:[.31,.69],3:[.32,.34,.34],4:[.24,.24,.26,.26],5:[.28,.18,.18,.18,.18]}.get(n,[1/n]*n)
            if values[0][0]=="Gate": widths=[.10,.42,.48]
            if values[0][0]=="AJ5 condition": widths=[.34,.24,.42]
            if values[0][0]=="CJ5 condition": widths=[.40,.30,.30]
            cells=[[Paragraph(inline(("**"+v+"**") if ri==0 else v),s["cell"]) for v in row] for ri,row in enumerate(values)]
            table=Table(cells,colWidths=[WIDTH*w for w in widths],repeatRows=1,hAlign="LEFT")
            table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e9eff3")),("LINEBELOW",(0,0),(-1,0),.65,INK),("LINEBELOW",(0,-1),(-1,-1),.5,INK),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f7f9fa")]),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
            while i<len(lines) and not lines[i].strip(): i+=1
            caption=None
            if i<len(lines) and lines[i].strip().startswith("Table "):
                caption=Paragraph(inline(lines[i].strip()),s["caption"]); i+=1
            # Tables in this manuscript are short enough to keep with captions.
            prefix=[]
            if story and isinstance(story[-1],Paragraph) and story[-1].style.name in ("h2","h3"):
                prefix=[story.pop()]
            story.append(KeepTogether(prefix+[table,Spacer(1,5)]+([caption] if caption else []))); continue
        if line.startswith("```"):
            block=[]
            while i<len(lines) and not lines[i].startswith("```"): block.append(lines[i]); i+=1
            i+=1
            preceding=story.pop()
            prefix=[]
            if story and isinstance(story[-1],Paragraph) and story[-1].style.name in ("h2","h3"):
                prefix=[story.pop()]
            story.append(KeepTogether(prefix+[preceding,Paragraph(inline(" ".join(block)),s["code"])])); continue
        if line.startswith("- "):
            story.append(Paragraph("• "+inline(line[2:]),s["list"])); continue
        paragraph=[line]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(("#","|","![","```","- ","\\[")):
            # Reference entries are separate paragraphs even without blank lines.
            if refs and re.match(r"\d+\. ",lines[i]): break
            paragraph.append(lines[i].strip()); i+=1
        style="ref" if refs else "caption" if line.startswith("Table ") else "body"
        story.append(Paragraph(inline(" ".join(paragraph)),s[style]))
    return story


def footer(canvas, doc):
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#bdc8d0"))
    canvas.line(20*mm,17*mm,A4[0]-20*mm,17*mm)
    canvas.setFont("Article",7); canvas.setFillColor(colors.HexColor("#566774"))
    canvas.drawString(20*mm,12*mm,"Hypothesis-space expansion | AIJ manuscript")
    canvas.drawRightString(A4[0]-20*mm,12*mm,str(doc.page)); canvas.restoreState()


def main():
    TMP.mkdir(parents=True,exist_ok=True); OUT.parent.mkdir(parents=True,exist_ok=True)
    register_fonts(); s=styles()
    sources=[ROOT/"manuscript/AIJ_MANUSCRIPT.md",ROOT/"manuscript/AIJ_SUPPLEMENTARY_METHODS.md"]
    story=markdown(sources[0],s)+[PageBreak()]+markdown(sources[1],s)
    doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=19*mm,bottomMargin=23*mm,title="Prospective evaluation and component attribution of hypothesis-space expansion in AI systems",author="Jing-Rung Huang and Wen-Hsiang Lu")
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    inputs=sources+sorted((ROOT/"manuscript/figures/aij").glob("*.png"))+[Path(__file__)]
    manifest={"output":str(OUT.relative_to(ROOT)),"sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(),"input_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
    (ROOT/"reports/AIJ_PDF_BUILD_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(OUT)


if __name__=="__main__": main()
