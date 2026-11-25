"""G8 counterfactual 1: raise the Iberian machines' inertia by 20 % (S22, Stage 8).

G8 (PLAN_OLD Part C): "+20 % inertia does **not** prevent collapse (p.302)". This script raises `H`
from 2.5 to 3.0 s on the four Iberian `SyncUnit`s only - the 200 GVA France equivalent (H 25 s) is a
model artefact, not part of the Iberian fleet, so leaving it fixed is what makes the test meaningful.

usage: python stage8/raise_inertia.py --pscx X [--factor 1.2]
"""
import argparse
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--factor", type=float, default=1.2)
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]

    def walk(el):
        for c in el:
            yield c
            if c.tag != "User":
                yield from walk(c)

    changed = []
    for c in walk(main_def.find("schematic")):
        if c.tag != "User" or not (c.get("defn") or "").endswith(":SyncUnit"):
            continue
        pl = c.find("paramlist")
        vals = {p.get("name"): p.get("value") for p in pl.findall("param")}
        if float(vals.get("Sbase", 0)) > 100000:      # France equivalent: leave alone
            continue
        new = float(vals["H"]) * a.factor
        for p in pl.findall("param"):
            if p.get("name") == "H":
                p.set("value", f"{new:.3f}")
        changed.append((vals.get("Sbase"), vals.get("H"), f"{new:.3f}"))

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - H raised x{a.factor} on {len(changed)} Iberian units:")
    for s, old, new in changed:
        print(f"   Sbase {s:>9s}: H {old} -> {new}")


if __name__ == "__main__":
    main()
