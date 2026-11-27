r"""Set the built-in test hooks of a replay case without rebuilding (S30 sec 23). Project must not be loaded.

usage: python iberia_eq\pscad\set_test.py --pscx <v2.pscx> [--ftest t1:t2:df] [--vtest t1:t2:dv] [--off]
The replay build (build_v2.py --replay) always contains two inert ramps, upramp blocks named FTEST_RAMP and VTEST_RAMP
(Y2 = 0): FTEST is added to every under-frequency stage input, VTEST to every rooftop-PV voltage input. This script sets
X1/X2/Y2 of those blocks; --off makes them inert again. Values only: the build map is unchanged.
"""
import argparse, re

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); ap.add_argument("--ftest"); ap.add_argument("--vtest")
ap.add_argument("--off", action="store_true"); a = ap.parse_args()
t = open(a.pscx, encoding="utf-8").read(); done = []
for name, spec in (("FTEST_RAMP", a.ftest), ("VTEST_RAMP", a.vtest)):
    if not spec and not a.off: continue
    t1, t2, dd = (float(x) for x in spec.split(":")) if spec else (1000.0, 1001.0, 0.0)
    def edit(m):
        blk = m.group(0)
        if f'<param name="Name" value="{name}"' not in blk: return blk
        for k, v in (("X1", t1), ("X2", t2), ("Y2", dd)):
            blk = re.sub(rf'(<param name="{k}" value=")[^"]*(")', rf"\g<1>{v:g}\g<2>", blk)
        done.append(f"{name}: 0 -> {dd:g} over {t1:g}..{t2:g} s"); return blk
    t = re.sub(r'<User [^>]*defn="master:upramp".*?</User>', edit, t, flags=re.S)
if not done: raise SystemExit("no test hook found or nothing requested (is this a replay build with hooks?)")
open(a.pscx, "w", encoding="utf-8").write(t); print("; ".join(done))
