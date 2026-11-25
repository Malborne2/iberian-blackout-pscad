"""Compare each line's per-unit data: base (Bergeron) vs rebased (PI).

In the base project the data sits in the TLine_n definitions; each page T<a>_<b> instantiates
one of them. In the rebased project the data sits on the page itself (pi_section).
"""
import re
from math import pi
from pathlib import Path

BASE = Path(r"C:\PSCAD_work\iberia_base.pscx")
REB = Path(r"C:\PSCAD_work\iberia1_stage1.pscx")


def definitions(text):
    out = {}
    for m in re.finditer(r'<Definition[^>]*?name="([^"]+)"[^>]*?>', text):
        start = m.end()
        nxt = text.find("<Definition", start)
        out[m.group(1)] = text[start: nxt if nxt > 0 else len(text)]
    return out


def num(block, key):
    m = re.search(r'<param name="' + key + r'" value="([^"]*)"', block)
    if not m:
        return None
    try:
        return float(m.group(1).split()[0])
    except ValueError:
        return None


bt = BASE.read_text(encoding="utf-8", errors="replace")
rt = REB.read_text(encoding="utf-8", errors="replace")
bd, rd = definitions(bt), definitions(rt)

# base: TLine_n -> (R, X, B, VR, MVA)
line = {}
for name, body in bd.items():
    short = name.split(":")[-1]
    if re.fullmatch(r"TLine_\d+", short):
        blk = re.search(r'defn="[^"]*Line_ManualYZ".*?(?=<User|\Z)', body, re.S)
        if blk:
            line[short] = tuple(num(blk.group(0), k) for k in ("R", "X", "B", "VR", "MVA"))

pages = {k: v for k, v in bd.items() if re.fullmatch(r"(?:.*:)?T\d+_\d+", k.split(":")[-1] and k)}
pages = {k: v for k, v in bd.items() if re.fullmatch(r"T\d+_\d+", k.split(":")[-1])}
print(f"line definitions with data: {len(line)}   pages: {len(pages)}")

rows, bad = 0, []
for page, body in pages.items():
    short_page = page.split(":")[-1]
    inst = re.search(r'defn="[^"]*?(TLine_\d+)"', body)
    rbody = rd.get(short_page) or rd.get(page)
    if not (inst and rbody):
        bad.append((short_page, "no instance/page", bool(inst), bool(rbody)))
        continue
    dat = line.get(inst.group(1))
    rp = re.search(r'defn="[^"]*pi_section".*?(?=<User|\Z)', rbody, re.S)
    if not (dat and rp):
        bad.append((short_page, "no data/pi", bool(dat), bool(rp)))
        continue
    R0, X0, B0, VR0, MV0 = dat
    Rp, Lp, Cp = (num(rp.group(0), k) for k in ("Rp1", "Lp1", "Cp1"))
    VR1, MV1 = num(rp.group(0), "VR"), num(rp.group(0), "MVA")
    if None in (R0, X0, B0, Rp, Lp, Cp, VR0, MV0, VR1, MV1):
        bad.append((short_page, "unparsed"))
        continue
    Z0, Z1 = VR0 ** 2 / MV0, VR1 ** 2 / MV1
    R0p, X0p, B0p = R0 / Z0, X0 / Z0, B0 * Z0
    R1p, X1p = Rp / Z1, Lp * 2 * pi * 50 / Z1
    B1p = Cp * 1e-6 * 2 * pi * 50 * Z1
    e = max(abs(R1p - R0p) / R0p if R0p else 0,
            abs(X1p - X0p) / X0p if X0p else 0,
            abs(B1p - B0p) / B0p if B0p else 0)
    rows += 1
    if e > 5e-3:
        bad.append((short_page, f"Rpu {R0p:.5f}->{R1p:.5f} Xpu {X0p:.5f}->{X1p:.5f} Bpu {B0p:.4f}->{B1p:.4f}", round(e * 100, 2)))

print(f"compared {rows}; outside 0.5 %: {len(bad)}")
for x in bad:
    print("  ", x)
