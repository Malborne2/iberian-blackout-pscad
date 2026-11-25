"""Force the plant trip for the whole plant fleet (S22, Stage 5 G5 clause 3).

The 18 plants share ONE Force net called FRC, driven by the single master:const at (84,8).
Setting its Value to 1 forces `Force = 1` on every RES_Plant, i.e. a total plant generation loss.

usage: python stage6/set_global_force.py --pscx C:\\PSCAD_work\\ib4hv.pscx --value 1
"""
import argparse
import xml.etree.ElementTree as ET

G = 18


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--value", default="1")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")

    hits = []
    stack = [sch]
    while stack:
        el = stack.pop()
        for c in el:
            if c.tag == "User":
                if (c.get("defn") or "") == "master:const":
                    try:
                        xy = (int(c.get("x")) // G, int(c.get("y")) // G)
                    except (TypeError, ValueError):
                        continue
                    pl = c.find("paramlist")
                    vals = {p.get("name"): p.get("value") for p in pl.findall("param")}
                    if xy == (84, 8) and vals.get("Value") == "0":
                        hits.append((c, pl))
            else:
                stack.append(c)

    if len(hits) != 1:
        raise SystemExit(f"expected exactly one FRC const at (84,8), found {len(hits)}")

    c, pl = hits[0]
    for p in pl.findall("param"):
        if p.get("name") == "Value":
            p.set("value", a.value)
    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - global FRC Value 0 -> {a.value} (all 18 plants)")


if __name__ == "__main__":
    main()
