"""Per-bus collector-tap trim (WP5 lever 4), from one run's own .psout.

V_collector scales ~ 1/tap for a given power transfer, so the first-order correction is

    tap_new = tap_old * V_measured / V_target

usage:
  python stage5\\tap_trim.py --psout <psout> --win 7 8 [--target 1.03] [--apply C:\\PSCAD_work\\ib4hv.pscx]

--apply writes the tap consts with the same ids used by set_plant_relay.py (project must be UNLOADED).
Prints the measured value, the suggestion and the previous suggestion for comparison.
"""
import argparse
import sys
import numpy as np
import mhi.psout

BUSES = {33: [1, 18], 34: [5, 6, 7, 8, 9, 10, 11], 35: [12, 13, 14], 36: [2, 3, 4], 38: [15, 16, 17]}
TAPS = {"33": 1931291851, "34": 2006720080, "35": 705661550, "36": 506809771, "38": 1387559265}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--psout", required=True)
    ap.add_argument("--win", nargs=2, type=float, default=[7.0, 8.0])
    ap.add_argument("--target", type=float, default=1.03)
    ap.add_argument("--old", type=float, default=0.962)
    ap.add_argument("--apply")
    ap.add_argument("--vt", default=None, help="comma list bus:vt to also set, e.g. 38:1.5")
    a = ap.parse_args()

    f = mhi.psout.File(a.psout)
    r = f.run(0)

    def g(p):
        return np.asarray(r.call(p, sep="/").data, float)

    t = np.asarray(r.call("Root/Main/RES_Plant[1]/ID/0/1", sep="/").domain.data, float)
    w = (t >= a.win[0]) & (t <= a.win[1])
    print(f"{a.psout}  window {a.win[0]}-{a.win[1]} s  target {a.target}")
    new = {}
    for bus, ks in BUSES.items():
        v = np.mean([g(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[w].mean() for k in ks])
        iq = np.mean([g(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[w].mean() for k in ks])
        tap = a.old * v / a.target
        new[bus] = tap
        print(f"  bus {bus}: VDF {v:6.4f}  iq {iq:+.4f}  -> tap {tap:.4f}")

    if a.apply:
        import xml.etree.ElementTree as ET
        tree = ET.parse(a.apply)
        root = tree.getroot()
        sch = [d for d in root.find("definitions") if d.get("name") == "Main"][0].find("schematic")
        for bus, val in new.items():
            cid = str(TAPS[str(bus)])
            hit = [c for c in sch if c.get("id") == cid]
            if not hit:
                print(f"  WARN bus {bus}: const {cid} not found")
                continue
            pl = hit[0].find("paramlist")
            for p in pl.findall("param"):
                if p.get("name") == "Value":
                    print(f"  apply bus {bus}: {p.get('value')} -> {val:.4f}")
                    p.set("value", f"{val:.4f}")
        tree.write(a.apply, encoding="utf-8", xml_declaration=True)
        print(f"written: {a.apply}")
    f.close()


if __name__ == "__main__":
    main()
