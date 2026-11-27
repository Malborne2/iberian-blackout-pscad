r"""Fix the POI RMS measurement of the RES OV relay (S30 sec 25). Project must not be loaded.

usage: python iberia_eq\pscad\fix_poirms.py --pscx <v2.pscx> [--undo]
The relay's POI side (MeasSide 1, stage3/build_resplant.py WP6 item 4) takes the RMS of VA_PU, the phase-A voltage in
pu of the PEAK base, so VPOIRMS reads 1/sqrt(2) of the bus voltage (bench rly_m1: VPOIRMS 0.725 vs VDF 1.025 pu) and
no relay with MeasSide 1 could ever trip (rp_cascade: 0 of 11). master:rms-inst scales only as Type DIGITAL, where
OUT = RMS / Scale (Analog ignores Scale; a first try with Scale = sqrt(2) on Analog changed nothing, bench rly_m1): sets
Type = 1 (digital, NSAM samples per 50 Hz cycle) and Scale = 1/sqrt(2) on the block of the RES_Plant definition. Constant inside the module: the build map and a snapshot of the case stay valid.
"""
import argparse, math, re

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); ap.add_argument("--undo", action="store_true"); a = ap.parse_args()
t = open(a.pscx, encoding="utf-8").read()
i = t.index('name="RES_Plant"', t.index("<definitions")); j = t.index("</Definition>", i)
d = t[i:j]; v = "1" if a.undo else f"{1 / math.sqrt(2):.8f}"; ty = "0" if a.undo else "1"
def fix(m):
    s = re.sub(r'(<param name="Scale" value=")[^"]*(")', rf"\g<1>{v}\g<2>", m.group(0))
    s = re.sub(r'(<param name="freq" value=")[^"]*(")', r"\g<1>50\g<2>", s)
    return re.sub(r'(<param name="Type" value=")[^"]*(")', rf"\g<1>{ty}\g<2>", s)
d2, n = re.subn(r'<User [^>]*defn="master:rms-inst".*?</User>', fix, d, flags=re.S)
if n != 1: raise SystemExit(f"expected 1 rms-inst block in RES_Plant, found {n}")
open(a.pscx, "w", encoding="utf-8").write(t[:i] + d2 + t[j:]); print(f"{a.pscx}: RES_Plant rms-inst Type = {ty}, Scale = {v}, freq 50")
