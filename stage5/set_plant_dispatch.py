"""Re-dispatch the 18 plants by a common pu increment (WP4 French-end representation / WP5 lever 3).

Each plant's set-point is the `Y2` of a `master:upramp` on Main (verified for the 3,132 MVA plant:
upramp 1700000146 Y2 0.899745 -> label PR18 -> Pref pin (7,72)).

usage:
  python stage5\set_plant_dispatch.py --pscx C:\\PSCAD_work\\ib4hv.pscx --raise-pu 0.0604 [--show]
  python stage5\\set_plant_dispatch.py --pscx C:\\PSCAD_work\\ib4hv.pscx --set-total-mw 1000

Project must be UNLOADED (rule P12).
"""
import argparse
import xml.etree.ElementTree as ET

SBASES = [400.0, 172.0, 167.0, 2402.0, 647.0, 162.0, 566.0, 405.0, 339.0, 236.0,
          1194.0, 612.0, 130.0, 2498.0, 589.0, 348.0, 3132.0, 2550.0]
import os
# S23: ib5 uprated every plant x1.30 (stage11/prepare_ib5.py). Set KPLANT=1 for pre-ib5 cases.
KPLANT = float(os.environ.get("KPLANT", "1.30"))
SBASES = [s * KPLANT for s in SBASES]
TOTAL = sum(SBASES)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--raise-pu", type=float, default=None)
    ap.add_argument("--set-total-mw", type=float, default=None)
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    if a.set_total_mw is not None and a.raise_pu is None:
        a.raise_pu = a.set_total_mw / TOTAL

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    ups = [c for c in main.find("schematic")
           if c.tag == "User" and (c.get("defn") or "") == "master:upramp"]
    print(f"  upramps on Main: {len(ups)}")
    for c in ups:
        pl = c.find("paramlist")
        y2 = [p for p in pl.findall("param") if p.get("name") == "Y2"]
        if not y2:
            continue
        old = float(y2[0].get("value"))
        if a.show or a.raise_pu is None:
            print(f"    upramp {c.get('id')}: Y2 {old:.6f} (={old:.0f} pu)")
            continue
        new = old + a.raise_pu
        y2[0].set("value", f"{new:.6f}")
        print(f"    upramp {c.get('id')}: Y2 {old:.6f} -> {new:.6f}")
    if a.raise_pu is not None and not a.show:
        tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
        print(f"  written: {a.pscx}  (+{a.raise_pu:.4f} pu on every plant = "
              f"+{a.raise_pu*TOTAL:.0f} MW of {TOTAL:.0f} MVA installed)")


if __name__ == "__main__":
    main()
