"""Render report pages to PNG for digitising (Stage 0).

Usage: python stage0/render_pages.py 16 127 129 131 299 300
Writes stage0/pages/pgNNN.png at 300 dpi.
"""
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Resources" / "Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf"
OUT = Path(__file__).with_name("pages")

def main(pages: list[int]) -> None:
    OUT.mkdir(exist_ok=True)
    doc = pymupdf.open(PDF)
    print(f"pdf pages: {doc.page_count}")
    for p in pages:
        page = doc[p - 1]                      # PDF page 1 = report page 1
        pix = page.get_pixmap(dpi=300)
        f = OUT / f"pg{p:03d}.png"
        pix.save(f)
        print(f"{f}  {pix.width}x{pix.height}")
    doc.close()

if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [16])
