"""Axis calibration from the PDF's own text layer (exact, no pixel guessing)."""
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Resources" / "Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf"

page_no = int(sys.argv[1])
doc = pymupdf.open(PDF)
page = doc[page_no - 1]
SC = 300 / 72          # render scale used by render_pages.py
words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,wordno
for w in words:
    x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
    print(f"{txt!r:22} x={x0*SC:7.1f}..{x1*SC:7.1f}  y={(y0*SC+y1*SC)/2:7.1f}")
doc.close()
