r"""Set the exciter initialisation time ExInit in SyncUnit and PumpUnit (S30 sec 12). Project must not be loaded.

usage: python iberia_eq\pscad\add_exinit.py --pscx C:\PSCAD_work\v2sld\v2.pscx --t 2.5

The exciter (excac_2016_2) computes its voltage reference when ExInit ramps 0 -> 1. In the ib6-derived modules the
ramp is X1 = Tstart (instance parameter, 0.5) to X2 = 0.51 (literal), so the reference is fixed at 0.5 s. In v2 the
RES plants are still ramping then (Id 0.25 of 1.0 at 0.5 s, full at ~1.25 s): the references fit a non-load-flow
state and the pre-release machine output is 21.2 GW against 15.7 GW in the load flow (v2_pump, S30 sec 11/12).
Setting Tstart alone fails ("Start of ramp should be less than saturating input", EMTDC RAMP abort), so this script
sets both ends: X1 = T, X2 = T + 0.01 (literals) in both definitions. T must stay below the 5 s rotor release.
"""
import argparse
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); ap.add_argument("--t", type=float, required=True)
a = ap.parse_args()
assert 0.52 <= a.t < 5.0, "ExInit must be after S2M (0.52 s) and before the release (5 s)"
tree = ET.parse(a.pscx); root = tree.getroot(); n = 0
for nm in ("SyncUnit", "PumpUnit"):
    d = [x for x in root.iter("Definition") if x.get("name") == nm][0]
    for e in d.find("schematic"):
        if e.get("defn") == "master:upramp":
            pv = {p.get("name"): p for p in e.iter("param")}
            if pv["X1"].get("value") in ("Tstart",) or pv["Y2"].get("value") == "1.0" and pv["X2"].get("value") not in ("7.0",):
                if pv["X2"].get("value") == "7.0": continue
                pv["X1"].set("value", f"{a.t:g}"); pv["X2"].set("value", f"{a.t + 0.01:g}"); n += 1
assert n == 2, f"expected 2 ExInit ramps, patched {n}"
open(a.pscx, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
print(f"ExInit ramp -> {a.t:g} .. {a.t + 0.01:g} s in SyncUnit and PumpUnit")
