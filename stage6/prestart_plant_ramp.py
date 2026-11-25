"""Make the plant Pref ramps already finished at t = 0 (S22, G6 baseline fix, second attempt).

Measured: adding `Y1 = Y2` to the plant `upramp`s changed NOTHING (`run 89` is identical to `run 88`
to four decimals), so the block always ramps from zero; `Y1` is not its start value.

The ramp DOES respect its window, so moving the window entirely before t = 0 makes the block output
Y2 at the first step: X1 = -1 s, X2 = 0 s. The plants then start at their dispatch as an initial
condition, with no 14 GW start-up step to excite the 0.222 Hz mode.

Only plant upramps are touched (Y2 > 0); the LFDD relay's frequency ramp (Y2 = -1.7) is left alone.

usage: python stage6/prestart_plant_ramp.py --pscx C:\\PSCAD_work\\ib4hv.pscx
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
        if y2 <= 0:
            continue
        for p in pl.findall("param"):
            if p.get("name") == "X1":
                p.set("value", "-1")
            elif p.get("name") == "X2":
                p.set("value", "0")
        n += 1

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - {n} plant upramps pre-started (X1 = -1 s, X2 = 0 s, Y2 unchanged)")


if __name__ == "__main__":
    main()
