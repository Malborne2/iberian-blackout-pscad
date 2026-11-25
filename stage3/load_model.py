"""Make the network loads static voltage-dependent (PLAN_OLD B5: "do not use constant power").

Every `master:fixed_load` on `Main` carries a per-part voltage index: `NP`/`NQ` for part A (`Parts = 1` in
this model, so only NP/NQ are used).  0 = constant power, 1 = constant current, 2 = constant impedance.
The model was built with NP = NQ = 0 (source: every load's paramlist), which at the 0.39-0.54 pu the plant
fleet settles to asks the network for the *full* 25.2 GW / 5.78 Gvar at half voltage - i.e. 2.5x nominal
current, and the series Q loss of the 400 kV network goes up with the square.  PLAN_OLD B5 says explicitly
"Unsheddable part: static voltage-dependent load ... so do not use constant power."

This script changes only NP and NQ (and prints what it did). PO, QO, VBO, VPU, KPF/KQF and the reference
voltage are untouched, so at a bus sitting at 1.0 pu the load is unchanged.

usage: python stage3\\load_model.py --pscx C:\\PSCAD_work\\iberia4.pscx [--np 1] [--nq 1]
                                    [--restore] [--dry]
       --restore puts NP = NQ = 0 back (the S1-S19 model).

Projects must NOT be loaded in PSCAD while this runs (skill P12).
"""
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--np", type=float, default=1.0)
    ap.add_argument("--nq", type=float, default=1.0)
    ap.add_argument("--restore", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    npv, nqv = (0.0, 0.0) if a.restore else (a.np, a.nq)

    root = ET.parse(a.pscx).getroot()
    main = [d for d in root.iter("Definition") if d.get("name") == "Main"][0]
    sch = main.find("schematic")
    n = 0
    tot_p = tot_q = 0.0
    for u in sch.findall("User"):
        if u.get("defn") != "master:fixed_load":
            continue
        pl = u.find("paramlist")
        ps = {p.get("name"): p for p in pl.findall("param")}
        if ps["Parts"].get("value") != "1":
            raise SystemExit("a load has Parts != 1: NP/NQ alone would not describe it")
        n += 1
        old = (ps["NP"].get("value"), ps["NQ"].get("value"))
        ps["NP"].set("value", f"{npv:g}")
        ps["NQ"].set("value", f"{nqv:g}")
        tot_p += float(ps["PO"].get("value"))
        tot_q += float(ps["QO"].get("value"))
        print(f"  load {u.get('id')} at ({int(u.get('x')) // 18},{int(u.get('y')) // 18}): "
              f"NP/NQ {old[0]}/{old[1]} -> {npv:g}/{nqv:g}")
    print(f"{n} loads, NP={npv:g} NQ={nqv:g}; total load {3 * tot_p:.1f} MW / {3 * tot_q:.1f} Mvar at 1.0 pu")
    if a.dry:
        print("(dry run, nothing written)")
        return
    Path(a.pscx).write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
    print("written:", a.pscx)


if __name__ == "__main__":
    main()
