"""Lengthen the plant Pref ramp to X2 = 2 s (S22, G6 baseline, third attempt).

The start-up step is the masking transient: 14 GW delivered in 0.5 s rings the 0.222 Hz mode with
~0.22 Hz at 1 s and tau ~= 3 s (runs 88-90). Spreading the SAME 14 GW over 1.9 s (X1 = 0.1 -> X2 = 2.0)
leaves the initial condition untouched - the plants still start at zero, so the network is solved for
the same pre-event state - and cuts the excitation amplitude roughly with the ramp length.

Only plant upramps are touched (Y2 > 0); the LFDD relay's frequency ramp (Y2 = -1.7) is left alone.

usage: python stage6/lengthen_plant_ramp.py --pscx C:\\PSCAD_work\\ib4hv.pscx --x2 2.0
"""
import argparse
import xml.etree.ElementTree as ET

G = 18


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--x2", default="2.0")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")

    def walk(el):
        for c in el:
            yield c
            if c.tag != "User":
                yield from walk(c)

    n = 0
    old_x2 = set()
    for c in walk(sch):
        if c.tag != "User" or (c.get("defn") or "") != "master:upramp":
            continue
        pl = c.find("paramlist")
        vals = {p.get("name"): p.get("value") for p in pl.findall("param")}
        try:
            y2 = float(vals.get("Y2", "0"))
        except ValueError:
            continue
        if y2 <= 0:
            continue
        old_x2.add(vals.get("X2"))
        for p in pl.findall("param"):
            if p.get("name") == "X2":
                p.set("value", a.x2)
        n += 1

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - {n} plant upramps: X2 {sorted(old_x2)} -> {a.x2} s "
          f"(Y2 and the initial condition unchanged)")


if __name__ == "__main__":
    main()
