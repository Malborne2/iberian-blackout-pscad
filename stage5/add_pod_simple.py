"""Add an unscaled POD (washout + gain on the plant's own power) to an UNLOADED .pscx (S22 lever-3 test).

Pdev = PMEAS - lag(PMEAS, 0.5 s); PODP = Kpod*Pdev; IDREF_FF = IDREF_PP + PODP.
The grid-following reference label at (72,182) becomes IDREF_PP so the injection sum owns IDREF_FF.

usage: python stage5/add_pod_simple.py --pscx C:\\PSCAD_work\\ib4hv.pscx [--kpod 0.5]
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350003001]


def nid():
    ID[0] += 1
    return str(ID[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--kpod", type=float, default=0.5)
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    d = [x for x in root.find("definitions") if x.get("name") == "RES_Plant"][0]
    sch = d.find("schematic")

    proto = {}
    for c in sch:
        if c.tag != "User":
            continue
        k = c.get("defn") or ""
        if k in ("master:realpole", "master:sumjct", "master:gain", "master:datalabel") and k not in proto:
            proto[k] = c

    def place(kind, x, y, **vals):
        el = copy.deepcopy(proto[kind])
        el.set("id", nid())
        el.set("x", str(x * G))
        el.set("y", str(y * G))
        pl = el.find("paramlist")
        for q in pl.findall("param"):
            if q.get("name") in vals:
                q.set("value", str(vals.pop(q.get("name"))))
        for k, v in vals.items():
            ET.SubElement(pl, "param", {"name": k, "value": str(v)})
        sch.append(el)

    # rename the grid-following driver at (72,182)
    for c in sch:
        if c.tag != "User" or not (c.get("defn") or "").endswith(":datalabel"):
            continue
        try:
            xy = (int(c.get("x")) // G, int(c.get("y")) // G)
        except (TypeError, ValueError):
            continue
        if xy == (72, 182):
            for q in c.find("paramlist").findall("param"):
                if q.get("name") == "Name" and q.get("value") == "IDREF_FF":
                    q.set("value", "IDREF_PP")
                    print("  IDREF_FF driver -> IDREF_PP")

    # washout chain at y = 336
    place("master:realpole", 10, 336, Name="", Limit="0", COM="Real_Pole", Reset="0", YO="0.9",
          Dim="1", G="1", T="0.5", Max="10.0", Min="-10.0")
    place("master:datalabel", 8, 336, Name="PMEAS")
    place("master:datalabel", 12, 336, Name="PLAG")
    place("master:sumjct", 18, 336, D="1", F="-1", A="0", B="0", C="0", E="0", G="0")
    place("master:datalabel", 16, 336, Name="PMEAS")
    place("master:datalabel", 18, 338, Name="PLAG")
    place("master:datalabel", 20, 336, Name="PDEV")
    place("master:gain", 26, 336, Name="", G=f"{a.kpod}", Dim="1")
    place("master:datalabel", 24, 336, Name="PDEV")
    place("master:datalabel", 28, 336, Name="PODP")

    # injection into IDREF_FF at (78,190)
    place("master:sumjct", 78, 190, D="1", F="1", A="0", B="0", C="0", E="0", G="0")
    place("master:datalabel", 76, 190, Name="IDREF_PP")
    place("master:datalabel", 78, 192, Name="PODP")
    place("master:datalabel", 80, 190, Name="IDREF_FF")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - POD Kpod {a.kpod}")


if __name__ == "__main__":
    main()
