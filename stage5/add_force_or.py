"""Add TRIP = (1 - EN) OR Force to RES_Plant in an UNLOADED .pscx (S22).

The accepted project came from a snapshot, not from the current generator, so the edit is applied to the
XML: block 1's latch label becomes TRIP1 (the EN block then reads TRIP1), and a small chain at row y = 344
builds TRIP = (1 - EN) OR Force, which is what the Trip export/pgb and the FRC instrument need.

usage: python stage5/add_force_or.py --pscx C:\\PSCAD_work\\ib4hv.pscx
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
NEW_ID = [1350000901]


def nid():
    NEW_ID[0] += 1
    return str(NEW_ID[0])


def params(el):
    pl = el.find("paramlist")
    return {p.get("name"): p.get("value") for p in pl.findall("param")} if pl is not None else {}


def grid(el):
    try:
        return (int(el.get("x")) // G, int(el.get("y")) // G)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    d = [x for x in root.find("definitions") if x.get("name") == "RES_Plant"][0]
    sch = d.find("schematic")

    # 1) block 1's latch label -> TRIP1 (two copies: the driver and the EN block's reader)
    renamed = 0
    for c in sch:
        if c.tag != "User" or not (c.get("defn") or "").endswith(":datalabel"):
            continue
        if grid(c) not in ((36, 152), (82, 46)):
            continue
        for q in c.find("paramlist").findall("param"):
            if q.get("name") == "Name" and q.get("value") == "TRIP":
                q.set("value", "TRIP1")
                renamed += 1
    print(f"  TRIP -> TRIP1 labels: {renamed}")

    # 2) prototypes to clone (same definition, so ports/params match)
    proto = {}
    for c in sch:
        if c.tag != "User":
            continue
        defn = c.get("defn") or ""
        p = params(c)
        if defn == "master:sumjct" and "proto_sum" not in proto:
            proto["proto_sum"] = c
        if defn == "master:compare" and c.get("x") and "proto_cmp" not in proto:
            proto["proto_cmp"] = c
        if defn == "master:datalabel" and "proto_lab" not in proto:
            proto["proto_lab"] = c

    def place(kind, x, y, name=None, **p):
        el = copy.deepcopy(proto[kind])
        el.set("id", nid())
        el.set("x", str(x * G))
        el.set("y", str(y * G))
        pl = el.find("paramlist")
        vals = {"Name": name} if name is not None else {}
        vals.update(p)
        for q in pl.findall("param"):
            if q.get("name") in vals:
                q.set("value", str(vals.pop(q.get("name"))))
        for k, v in vals.items():
            ET.SubElement(pl, "param", {"name": k, "value": str(v)})
        sch.append(el)
        return el

    # 3) TRIP = (1 - EN) OR Force  at y = 344
    place("proto_sum", 10, 344, D="1", F="-1", A="0", B="0", C="0", E="0", G="0")
    place("proto_lab", 8, 344, name="ONE")
    place("proto_lab", 10, 346, name="EN")
    place("proto_lab", 12, 344, name="TRIP0")
    place("proto_sum", 18, 344, A="1", F="1", B="0", C="0", D="0", E="0", G="0")
    place("proto_lab", 16, 344, name="TRIP0")
    place("proto_lab", 18, 346, name="Force")
    place("proto_lab", 20, 344, name="TRIPSUM")
    place("proto_lab", 22, 344, name="TRIPSUM")
    place("proto_cmp", 24, 344, X="0.5", OL="0", OH="1")
    place("proto_lab", 26, 344, name="TRIP")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} (TRIP = (1-EN) OR Force)")


if __name__ == "__main__":
    main()
