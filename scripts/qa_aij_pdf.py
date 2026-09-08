"""Read-only PDF checks and page contact sheets for visual review."""
from pathlib import Path
import json
import re
import pdfplumber
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/"output/pdf/AIJ_manuscript_and_supplement.pdf"
TMP=ROOT/"tmp/pdfs/aij"


def main():
    pages=[]; violations=[]
    with pdfplumber.open(PDF) as pdf:
        for number,page in enumerate(pdf.pages,1):
            text=page.extract_text() or ""
            pages.append({"page":number,"characters":len(text),"images":len(page.images),"first_line":text.splitlines()[0],"last_body_line":text.splitlines()[-2]})
            assert len(text)>50,(number,"empty page")
            for char in page.chars:
                if char["x0"]<49 or char["x1"]>page.width-49 or char["top"]<40 or char["bottom"]>page.height-22:
                    violations.append({"page":number,"text":char["text"],"x0":char["x0"],"x1":char["x1"],"top":char["top"]})
            assert "\ufffd" not in text and "(cid:" not in text,(number,"unmapped glyph")
        alltext="\n".join(p.extract_text() or "" for p in pdf.pages)
    assert not violations,violations[:10]
    for number in range(1,8): assert f"Figure {number}." in alltext,number
    for number in range(1,7): assert f"Table {number}." in alltext,number
    for number in range(1,19): assert f"S{number}." in alltext,number
    for number in range(1,43): assert re.search(rf"(?m)^{number}\. ",alltext),number
    for term in ["2,400","142/400","3,939","15/96","16/96","35,533","36,168","12,056"]: assert term in alltext,term
    renders=[TMP/f"page-{i:02d}.png" for i in range(1,len(pages)+1)]
    assert all(p.exists() for p in renders),"Missing current-page render"
    for start in range(0,len(renders),3):
        selected=renders[start:start+3]
        sheet=Image.new("RGB",(900*len(selected),1300),"#d4dce2")
        draw=ImageDraw.Draw(sheet)
        for col,path in enumerate(selected):
            with Image.open(path) as im:
                thumb=ImageOps.contain(im,(880,1250))
                sheet.paste(thumb,(col*900+10,35))
            draw.text((col*900+15,10),f"Page {start+col+1}",fill="black")
        sheet.save(TMP/f"contact_{start+1:02d}_{start+len(selected):02d}.png")
    (ROOT/"reports/AIJ_PDF_QA.json").write_text(json.dumps({"pages":pages,"bounds_violations":violations,"checks":"page bounds; nonempty pages; mapped glyphs; 7 figures; 6 tables; 18 supplementary sections; 42 references; numerical sentinels","visual_inspection":"See AIJ_SUBMISSION_READINESS.md; contact sheets are QA intermediates."},indent=2)+"\n")
    print(f"{len(pages)} pages checked; 0 bounds/glyph failures; contact sheets prepared")


if __name__=="__main__": main()
