"""Verify that each number used by the model really appears on the page PLAN.md cites.

Reads the PDF text layer directly (no secondary documents).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Resources" / "Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf"

# (label, needle as it appears in the text, page cited in PLAN.md)
CHECKS = [
    ("Spain demand 25.2 GW", "25,2", 11),
    ("solar PV 16,540 MW", "16,540", 11),
    ("wind 3,630 MW", "3,630", 11),
    ("nuclear 3,400 MW", "3,400", 11),
    ("pumping 3,031 MW", "3,031", 11),
    ("cos phi 0.985", "0.985", 17),
    ("kinetic energy 119,474 MWs", "119,474", 51),
    ("H 2.2-2.7 s", "2.2", 51),
    ("Granada 355 MW / 165 Mvar", "165", 122),
    ("Granada LV 233.4 kV = 1.061 pu", "233.4", 122),
    ("400 kV side 417.9 kV", "417.9", 122),
    ("trip 1.10 pu, 0 s on 220 kV side", "1.10", 122),
    ("Badajoz 582 MW / 165 Mvar", "582", 126),
    ("Badajoz 145 MW / 38 Mvar", "38", 126),
    ("south RES absorption 2,300 Mvar", "2,300", 216),
    ("reactor 150 Mvar", "150", 217),
    ("south reactors 2,700-3,015 Mvar", "2,700", 216),
    ("reactors connected 1,300 Mvar", "1,300", 216),
    ("HVDC 2 x 1,000 MW", "1,000", 101),
    ("HVDC K = 360 MW/deg", "360", 102),
    ("HVDC T = 50 s", "50", 102),
    ("HVDC +400/-600 Mvar", "600", 102),
    ("HVDC constant power at 12:09, 1,000 MW", "1,000", 71),
    ("HVDC 405 kV set-point", "405", 136),
    ("HVDC 7.7 Mvar at 12:33:00", "7.7", 136),
    ("POD-Q +/-100 Mvar blocked 12:03:51", "100", 69),
    ("OV setting 1.089 pu / 1.5 s", "1.089", 160),
    ("OV setting 1.139 pu / 0.2 s", "1.139", 160),
    ("OV setting 1.15 pu / 0.6 s", "1.15", 160),
    ("ride-through 1.10 pu / 60 min", "1.10", 141),
    ("LFDD 6 steps 49.0-48.0 Hz", "48.0", 200),
    ("LFDD step 1 = 1,176 MW", "1,176", 200),
    ("total disconnected demand 8,504.9 MW", "8,504.9", 200),
    ("pumps 2,168 MW at 49.5 Hz", "2,168", 198),
    ("pumps 588 MW at 49.3 Hz", "588", 198),
    ("loss of synchronism 12:33:19.6", "19.6", 130),
    ("Vmax 442.5 kV at 12:33:17", "442.5", 123),
    ("Vmax 451.4 kV at 12:33:18", "451.4", 123),
    ("400 kV above 440 kV from 16.68", "16.68", 123),
    ("HVDC block 12:33:23.960", "23.960", 120),
    ("0.63 Hz oscillation", "0.63", 66),
    ("Almaraz swing 30 kV", "30", 67),
    ("voltage down to 375 kV", "375", 67),
    ("ce frequency dips to 49.9", "49.9", 16),
    ("POD-Q saturated 50 s", "50", 69),
    ("0.63 Hz second harmonic 1.26 Hz", "1.26", 248),
]


def pages() -> dict[int, str]:
    doc = pymupdf.open(PDF)
    out = {}
    for i, page in enumerate(doc, start=1):
        out[i] = page.get_text()
    doc.close()
    return out


def main() -> int:
    pg = pages()
    bad = 0
    for label, needle, cited in CHECKS:
        hits = [p for p, t in pg.items() if needle in t]
        ok = cited in hits
        near = ", ".join(str(p) for p in hits[:8])
        print(f"{'OK  ' if ok else 'MISS'}  p.{cited:<4} {label:<46} found on: {near}")
        bad += not ok
    print(f"\n{len(CHECKS)-bad}/{len(CHECKS)} cited pages confirmed; {bad} need checking")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
