"""Raise the pre-event collector voltage with the plant Q(V) droop (S22, Stage 7 / WP5 lever).

Measured starting point (`run 100`, steady 5-6 s): every plant terminal sits at **0.979-1.032 pu** and
`Qmode = 0`, i.e. the converters are fixed-PF and `Vset` is inert. The report has Granada at **1.061 pu**
at 12:32:56 and above 1.10 a second later.

This script switches every plant to the **Q(V) droop** (`Qmode = 1`, proven in WP6 5a / run 56) and sets
`Vset`, so each converter regulates its terminal toward that value. Injected Q is bounded by the plant's
own current limit, so the achieved voltage is measured, not assumed.

usage: python stage7/raise_plant_voltage.py --pscx X --vset 1.10 [--qmode 1]
"""
import argparse
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--vset", default="1.10")
    ap.add_argument("--qmode", default="1")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]

    def walk(el):
        for c in el:
            yield c
            if c.tag != "User":
                yield from walk(c)

    n = 0
    for c in walk(main_def.find("schematic")):
        if c.tag != "User" or not (c.get("defn") or "").endswith(":RES_Plant"):
            continue
        pl = c.find("paramlist")
        for q in pl.findall("param"):
            if q.get("name") == "Qmode":
                q.set("value", a.qmode)
            elif q.get("name") == "Vset":
                q.set("value", a.vset)
        n += 1

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - {n} plants: Qmode {a.qmode}, Vset {a.vset} pu")


if __name__ == "__main__":
    main()
