"""Make Granada (psout ch1, 356 MW) forceable by replacing its inert signalgen with a compare.

Measured: the two unforceable plants are driven by dedicated instruments, not by the FRC net -
FRC33 at the Force pin (75,85) from the `signalgen` at (100,48), and FRC34 at (76,122) from the
signalgen at (100,54), both inert (Max = 0.0001). Granada is FRC33.

This script deletes the FRC33 signalgen and drives the same net from `compare(time > t, OL=0, OH=1)`,
so Force is 0 in the initial condition (plant healthy) and 1 after t. FRC34 is left untouched.

usage: python stage7/force_granada.py --pscx X --t 3.0
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350009001]


def nid():
    ID[0] += 1
    return str(ID[0])


def grid(el):
    try:
        return (int(el.get("x")) // G, int(el.get("y")) // G)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--t", default="3.0")
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

    # 1) remove the inert FRC33 signalgen
    gens = [c for c in walk(sch) if c.tag == "User" and (c.get("defn") or "") == "master:signalgen"
            and grid(c) == (100, 48)]
    if len(gens) != 1:
        raise SystemExit(f"expected the FRC33 signalgen at (100,48), found {len(gens)}")
    sch.remove(gens[0])
    print("  removed signalgen at (100,48) (FRC33, Max 0.0001)")

    allc = [c for dd in root.find("definitions") for c in walk(dd.find("schematic"))
            if c.tag == "User"]
    proto_cmp = [c for c in allc if (c.get("defn") or "") == "master:compare"][0]
    proto_tsig = [c for c in allc if (c.get("defn") or "") == "master:time-sig"][0]
    proto_lab = [c for c in allc if (c.get("defn") or "").endswith(":datalabel")][0]

    def place(proto, x, y, **vals):
        el = copy.deepcopy(proto)
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
        return el

    # 2) drive FRC33 from a compare (Force = 0 in the IC, 1 after t)
    place(proto_tsig, 6, 650, Name="")                 # OUT (8,650)
    place(proto_lab, 8, 650, Name="T9")
    place(proto_cmp, 14, 650, X=a.t, OL="0", OH="1")   # I (12,650), O (16,650)
    place(proto_lab, 12, 650, Name="T9")
    place(proto_lab, 16, 650, Name="FRC33")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - FRC33 (Granada) driven by compare(time > {a.t} s)")


if __name__ == "__main__":
    main()
