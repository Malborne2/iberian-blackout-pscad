r"""Set the SyncUnit/PumpUnit mode-switch times (S30 sec 12). Project must not be loaded.

usage: python iberia_eq\pscad\add_switchtimes.py --pscx <v2.pscx> [--s2m 0.52] [--l2n 5.0]

The ib6-derived modules switch at fixed times (literals in compare blocks of the definition):
  S2M  (342,1188)  source -> machine at 0.52 s;
  L2N  (342,1260)  rotor locked -> free at 5.0 s;
  RQ   (1512,972)  outer Q loop enabled at 5.0 s (inverted compare), kept equal to L2N.
Static network test: --s2m 100 --l2n 100 keeps every unit an ideal source at its load-flow |V| and angle for the
whole run, so each unit's P/Q is what the PSCAD network demands at the load-flow voltages. Compare with the load flow
(read_v2.py) to find network-model mismatches.
"""
import argparse
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True)
ap.add_argument("--s2m", type=float, default=0.52); ap.add_argument("--l2n", type=float, default=5.0); a = ap.parse_args()
POS = {("342", "1188"): a.s2m, ("342", "1260"): a.l2n, ("1512", "972"): a.l2n}
tree = ET.parse(a.pscx); root = tree.getroot(); n = 0
for nm in ("SyncUnit", "PumpUnit"):
    d = [x for x in root.iter("Definition") if x.get("name") == nm][0]
    for e in d.find("schematic"):
        k = (e.get("x"), e.get("y"))
        if e.get("defn") == "master:compare" and k in POS:
            p = next(q for q in e.iter("param") if q.get("name") == "X"); p.set("value", f"{POS[k]:g}"); n += 1
print(f"patched {n} compare blocks: S2M {a.s2m:g} s, L2N/RQ {a.l2n:g} s")
open(a.pscx, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
