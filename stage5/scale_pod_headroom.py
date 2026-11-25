"""Headroom-scaled POD injection on an UNLOADED .pscx (S22, from RUNLOG S21 §66).

POD_eff = PODP * (Imax - IDREF_FF) / Imax, so the damping signal cannot be rectified by the current limit.
Valid while IDREF_FF > 0 (injecting plants), which holds at this operating point - recorded, not assumed.

The multiplier is inserted between the existing PODP label and the IDREF injection sum, which is retargeted
from PODP to PODN.

usage: python stage5/scale_pod_headroom.py --pscx C:\\PSCAD_work\\ib4hv.pscx
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350002001]
IMAX = 1.1


def nid():
    ID[0] += 1
    return str(ID[0])


def params(el):
    pl = el.find("paramlist")
    return {p.get("name"): p.get("value") for p in pl.findall("param")} if pl is not None else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
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
        if k in ("master:const", "master:sumjct", "master:gain", "master:mult", "master:datalabel") and k not in proto:
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

    # h = (Imax - IDREF_FF) / Imax ;  PODN = PODP * h
    place("master:const", 34, 344, Name="", Value=f"{IMAX}")
    place("master:datalabel", 36, 344, Name="IMAXL")           # const O (34+2)
    place("master:sumjct", 42, 344, D="1", F="-1", A="0", B="0", C="0", E="0", G="0")
    place("master:datalabel", 40, 344, Name="IMAXL")           # sum A (42-2)
    place("master:datalabel", 42, 346, Name="IDREF_FF")        # sum F (42,344+2)
    place("master:datalabel", 44, 344, Name="HEAD")            # sum O
    place("master:gain", 50, 344, Name="", G=f"{1/IMAX:.6f}", Dim="1")
    place("master:datalabel", 48, 344, Name="HEAD")
    place("master:datalabel", 52, 344, Name="HNORM")           # gain O
    place("master:mult", 58, 344)
    place("master:datalabel", 56, 344, Name="PODP")            # mult IN1 (58-2)
    place("master:datalabel", 58, 346, Name="HNORM")           # mult IN2 (58,344+2)
    place("master:datalabel", 60, 344, Name="PODN")            # mult O

    # retarget the injection sum at (78,190) from PODP to PODN
    n = 0
    for c in sch:
        if c.tag != "User" or not (c.get("defn") or "").endswith(":datalabel"):
            continue
        try:
            xy = (int(c.get("x")) // G, int(c.get("y")) // G)
        except (TypeError, ValueError):
            continue
        if xy != (78, 192):
            continue
        for q in c.find("paramlist").findall("param"):
            if q.get("name") == "Name" and q.get("value") == "PODP":
                q.set("value", "PODN")
                n += 1
    print(f"  injection label retargeted: {n}")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - POD scaled by (Imax - IDREF)/Imax")


if __name__ == "__main__":
    main()
