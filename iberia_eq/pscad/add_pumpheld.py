r"""PumpUnit: hold the pumping power at rotor release, like SyncUnit (S30 sec 10). Project must not be loaded.

usage: python iberia_eq\pscad\add_pumpheld.py --pscx C:\PSCAD_work\v2sld\v2.pscx [--pmec0]

Why: the lt6 PumpUnit (stage12\make_pumpunit.py, RUNLOG S27 sec 28) disables the held-power term PMH in the torque sum
(PMT = TRIM + PTRT, TRIM = Pmec * ramp 5 -> 7 s). On the stiff bench that was fine. In the v2 network every pump
motor has ZERO load torque at the 5 s release: the 7 motors speed up (50 -> 50.9 Hz in 0.2 s), their ~3 GW draw
vanishes, and the generators race (sld_health12: machine Pe -8 GW in 0.25 s, loss of synchronism).
Fix: torque-sum input D (PMH) back to +1, so the motor keeps the load it carried when released; Pmec becomes a trim
as in SyncUnit and must be 0 (Pmec = P0/S on top of PMH double-counts the load, S27 sec 28). PLD stays the input for
the under-frequency pump-shedding stages.
  --pmec0 : also set Pmec = 0.0 on every PumpUnit instance in Main (for cases built before build_v2 set it).
"""
import argparse, re
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); ap.add_argument("--pmec0", action="store_true")
a = ap.parse_args()
tree = ET.parse(a.pscx); root = tree.getroot()
d = [x for x in root.iter("Definition") if x.get("name") == "PumpUnit"][0]
s = [e for e in d.find("schematic") if e.get("defn") == "master:sumjct" and e.get("x") == "540" and e.get("y") == "1548"]
assert len(s) == 1, "PumpUnit torque sum (540,1548) not found"
p = next(q for q in s[0].iter("param") if q.get("name") == "D"); old = p.get("value"); p.set("value", "1")
n = 0
if a.pmec0:
    for u in root.iter("User"):
        if (u.get("defn") or "").endswith(":PumpUnit"):
            for q in u.iter("param"):
                if q.get("name") == "Pmec": q.set("value", "0.0"); n += 1
open(a.pscx, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
print(f"PumpUnit torque sum D: {old} -> 1 (PMH held at release); Pmec -> 0 on {n} instances" if a.pmec0 else
      f"PumpUnit torque sum D: {old} -> 1 (PMH held at release)")
