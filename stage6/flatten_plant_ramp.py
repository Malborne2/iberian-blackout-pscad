"""Start the plants AT their dispatch instead of ramping them from zero (S22, G6 baseline fix).

Measured (runs 79/82/88): the plant `upramp`s have X1 = 0.1 s, X2 = 0.6 s and **no `Y1`**, so every
plant is ramped 0 -> Y2 in half a second at t = 0. That 14 GW step excites the 0.222 Hz mode with a
1 s amplitude of ~0.22 Hz and a decay time of ~3 s, so at t = 3 s (where the Case A events fire) the
frequency baseline is still ringing at ~0.1 Hz - larger than the event responses being measured.

Setting `Y1 = Y2` makes the ramp flat: the plant's Pref is its dispatch from t = 0, i.e. the initial
condition, with no start-up step. Only plant upramps are touched (Y2 > 0); the LFDD relay's
frequency ramp (Y2 = -1.7) is left alone.

usage: python stage6/flatten_plant_ramp.py --pscx C:\\PSCAD_work\\ib4hv.pscx
"""
import argparse
import xml.etree.ElementTree as ET

G = 18


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
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
    for c in walk(sch):
        if c.tag != "User" or (c.get("defn") or "") != "master:upramp":
            continue
        pl = c.find("paramlist")
        vals = {p.get("name"): p.get("value") for p in pl.findall("param")}
        try:
            y2 = float(vals.get("Y2", "0"))
        except ValueError:
            continue
        if y2 <= 0:                      # the LFDD frequency ramp (-1.7) is not a plant Pref
            continue
        found = False
        for p in pl.findall("param"):
            if p.get("name") == "Y1":
                p.set("value", vals["Y2"])
                found = True
        if not found:
            ET.SubElement(pl, "param", {"name": "Y1", "value": vals["Y2"]})
        n += 1

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - {n} plant upramps flattened (Y1 = Y2, no start-up step)")


if __name__ == "__main__":
    main()
