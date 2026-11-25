"""Verify the 34 PI conversions by pairing each page's old Bergeron data with its new PI data.

Uses two files: the pristine base (Bergeron) and the converted model.
"""
import re
import sys
from math import pi
from pathlib import Path

BASE = Path(r"C:\PSCAD_work\iberia_base.pscx")
CONV = Path(r"C:\PSCAD_work\iberia1_pi1.pscx")


def defs(path):
    """Split the file into <Definition ...> blocks keyed by name."""
    t = path.read_text(encoding="utf-8", errors="replace")
    out = {}
    for m in re.finditer(r'<Definition[^>]*name="([^"]+)"[^>]*>(.*?)(?=<Definition|\Z)', t, re.S):
        out[m.group(1)] = m.group(2)
    return out


def pval(block, key):
    m = re.search(r'<param name="' + key + r'" value="([^"]*)"', block)
    return m.group(1) if m else None


base, conv = defs(BASE), defs(CONV)
print(f"definitions: base={len(base)} converted={len(conv)}")

# base: page -> TLine_n via the instance definition name prefix
line_data = {}          # n -> (R, X, B)
for name, body in base.items():
    short = name.split(":")[-1]
    if re.fullmatch(r"TLine_\d+", short):
        ln = re.search(r'defn="[^"]*Line_ManualYZ".*?</User>', body, re.S)
        if ln:
            vals = [pval(ln.group(0), k) for k in ("R", "X", "B")]
            if all(v is not None for v in vals):
                line_data[short] = tuple(float(v) for v in vals)

page_map = {}
for name, body in base.items():
    if re.fullmatch(r"T\d+_\d+", name):
        inst = re.search(r'defn="[^"]*?(TLine_\d+)"', body)
        if inst:
            page_map[name] = inst.group(1)
print(f"pages mapped in base: {len(page_map)}  line defs: {len(line_data)}")

bad = []
for page, tl in sorted(page_map.items()):
    if tl not in line_data:
        bad.append((page, "no data for " + tl)); continue
    body = conv.get(page, "")
    pi_block = re.search(r'defn="master:pi_section".*?</User>', body, re.S)
    if not pi_block:
        bad.append((page, "no pi in converted")); continue
    Rp, Lp, Cp = (float(pval(pi_block.group(0), k)) for k in ("Rp1", "Lp1", "Cp1"))
    R, X, B = line_data[tl]
    Xc, Bc = Lp * 2 * pi * 50, Cp * 1e-6 * 2 * pi * 50
    eX = abs(Xc - X) / X if X else 0
    eB = abs(Bc - B) / B if B else 0
    eR = abs(Rp - R) / R if R else 0
    if max(eR, eX, eB) > 1e-6:
        bad.append((page, f"R {R}->{Rp}, X {X}->{Xc:.4f}, B {B}->{Bc:.8f}", eR, eX, eB))

print(f"checked {len(page_map)} pages; {len(bad)} mismatches")
for b in bad:
    print("  ", b)
