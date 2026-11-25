r"""S26: set the five collector-tap consts of ib6 (WP7 step (b) lever 1).

WP7(b) uses the taps first (PLAN 1b.5(b)).  The lever is first-order: V_collector ~ tap
(measured S21 D21-5: tap_new = tap_old * V_meas / V_target reproduced the recorded tap set exactly).
Changing them is a pre-event value change -> warm re-settle (PLAN 2b S6).

usage:
  python stage12\set_taps.py --pscx C:\PSCAD_work\s25\ib6.pscx --show
  python stage12\set_taps.py --pscx ... --from-psout <psout> --win 30 32 --target 1.061 [--apply]
  python stage12\set_taps.py --pscx ... --set 33=1.0138,34=0.9160 --apply
The project must be UNLOADED when --apply is given (P12).
"""
import argparse, xml.etree.ElementTree as ET

IID = {"33": "1931291851", "34": "2006720080", "35": "705661550", "36": "506809771", "38": "1387559265"}
BUSPL = {"33": [1, 18], "34": [5, 6, 7, 8, 9, 10, 11], "35": [12, 13, 14], "36": [2, 3, 4], "38": [15, 16, 17]}


def read_pscx(path):
    r = ET.parse(path).getroot()
    D = {d.get("name"): d for d in r.iter("Definition")}
    M = D["Main"].find("schematic")
    out = {}
    for c in M:
        if c.get("id") in IID.values():
            for q in c.find("paramlist").findall("param"):
                if q.get("name") == "Value":
                    out[[b for b, i in IID.items() if i == c.get("id")][0]] = float(q.get("value"))
    return out


ap = argparse.ArgumentParser()
ap.add_argument("--pscx", required=True)
ap.add_argument("--show", action="store_true")
ap.add_argument("--from-psout")
ap.add_argument("--win", nargs=2, type=float, default=[30.0, 32.0])
ap.add_argument("--target", type=float, default=1.061)
ap.add_argument("--set", default=None)
ap.add_argument("--apply", action="store_true")
a = ap.parse_args()

old = read_pscx(a.pscx)
print("current taps: " + "  ".join(f"{b}:{v:.4f}" for b, v in sorted(old.items())))

new = dict(old)
if a.from_psout:
    import mhi.psout
    import numpy as np
    r = mhi.psout.File(a.from_psout).run(0)
    t = np.asarray(r.call("Root/Main/SyncUnit[1]/Wspd/0/1", sep="/").domain.data, float)
    w = (t >= a.win[0]) & (t <= a.win[1])
    print(f"measured VDF, window {a.win[0]}-{a.win[1]} s of {a.from_psout}")
    for b, ks in BUSPL.items():
        v = np.mean([np.asarray(r.call(f"Root/Main/RES_Plant[{k}]/VDF/0/1", sep="/").data, float)[w].mean() for k in ks])
        new[b] = old[b] * v / a.target
        print(f"  bus {b}: VDF {v:.4f}  tap {old[b]:.4f} -> {new[b]:.4f}")
if a.set:
    for kv in a.set.split(","):
        b, v = kv.split("=")
        new[b] = float(v)

print("new taps:     " + "  ".join(f"{b}:{v:.4f}" for b, v in sorted(new.items())))
if not a.apply:
    print("(dry run; add --apply with the project unloaded)")
    raise SystemExit(0)

r = ET.parse(a.pscx)
root = r.getroot()
D = {d.get("name"): d for d in root.iter("Definition")}
M = D["Main"].find("schematic")
n = 0
for c in M:
    for b, i in IID.items():
        if c.get("id") == i:
            for q in c.find("paramlist").findall("param"):
                if q.get("name") == "Value":
                    q.set("value", f"{new[b]:.6f}")
                    n += 1
assert n == 5, n
r.write(a.pscx, encoding="utf-8", xml_declaration=True)
print(f"written {a.pscx} ({n} taps)")
