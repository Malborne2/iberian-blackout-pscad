r"""Diagnostic copy of a v2 case: record internal signals of a module and set parameters on all its instances (S30 sec 25).

usage: python iberia_eq\pscad\add_probe.py --src C:\PSCAD_work\v3r_a --dst C:\PSCAD_work\rly_m1 --defn RES_Plant
                                          --signals VPOIRMS VMF ARM TRIP1 [--set Vt1=0.9 MeasSide=1]
Each signal gets a datalabel + pgb pair in a free strip below the module's schematic (adds channels: the build map
changes, so use cold runs, not a snapshot of another build). --set applies to every instance of v2:<defn> on Main.
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pscx_canvas import OfflineCanvas

ap = argparse.ArgumentParser(); ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True)
ap.add_argument("--defn", required=True); ap.add_argument("--signals", nargs="+", default=[]); ap.add_argument("--set", nargs="*", default=[])
a = ap.parse_args(); os.makedirs(a.dst, exist_ok=True); P = os.path.join(a.dst, "v2.pscx")
t = open(os.path.join(a.src, "v2.pscx"), encoding="utf-8").read()
n = 0
for kv in a.set:
    k, v = kv.split("=", 1)
    def setp(m):
        global n; n += 1
        return re.sub(rf'(<param name="{k}" value=")[^"]*(")', rf"\g<1>{v}\g<2>", m.group(0))
    t = re.sub(rf'<User [^>]*defn="v2:{a.defn}".*?</User>', setp, t, flags=re.S)
open(P, "w", encoding="utf-8").write(t)
cv = OfflineCanvas(P, canvas=a.defn)
ymax = max(int(u.get("y", 0)) for u in cv.main) // 18 + 6
for k, s in enumerate(a.signals):
    x = 10 + 8 * k
    lb = cv.add_component("master", "datalabel", x, ymax, 0); lb.parameters(Name=s)
    g = cv.add_component("master", "pgb", x, ymax, 0); g.parameters(Name=f"P_{s}")
cv.save()
print(f"{P}: {len(a.signals)} probes in {a.defn} at y = {ymax}; {n} parameter sets ({a.set})")
