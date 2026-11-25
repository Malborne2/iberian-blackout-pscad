"""Drive the new SyncUnit EN pins on Main (S22, machine-side trip path).

Measured pin coordinates (pscad_get_ports, this build):
    bus 9    EN (21,16)      bus 31  EN (27,86)      bus 32  EN (37,98)
    bus 37   EN (26,6)       France EN (17,49)

Each pin gets a datalabel `SEN<k>`; the driver sits in a free row and is connected by net name, so no
geometry near the machines changes. Unforced units are held at 1 (gate transparent); forced units get
`compare(time > t)` which drives the gate to 0 and removes that machine's mechanical power.

usage: python stage6/drive_syncunit_en.py --pscx X --bus31 3.0 --bus32 3.3 --bus37 3.6
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350008001]
PINS = {9: (21, 16), 31: (27, 86), 32: (37, 98), 37: (26, 6), 39: (17, 49)}


def nid():
    ID[0] += 1
    return str(ID[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    for b in ("31", "32", "37"):
        ap.add_argument(f"--bus{b}", default="")
    a = ap.parse_args()
    times = {int(b): getattr(a, f"bus{b}") for b in ("31", "32", "37")}

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")

    def walk(el):
        for c in el:
            yield c
            if c.tag != "User":
                yield from walk(c)

    global_users = [c for dd in root.find("definitions") for c in walk(dd.find("schematic"))
                    if c.tag == "User"]
    proto_const = [c for c in global_users if (c.get("defn") or "") == "master:const"][0]
    proto_cmp = [c for c in global_users if (c.get("defn") or "") == "master:compare"][0]
    proto_tsig = [c for c in global_users if (c.get("defn") or "") == "master:time-sig"][0]
    proto_lab = [c for c in global_users if (c.get("defn") or "").endswith(":datalabel")][0]

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

    # net names on the pins
    for bus, (x, y) in PINS.items():
        place(proto_lab, x, y, Name=f"SEN{bus}")

    place(proto_tsig, 6, 580, Name="")            # OUT (8,580)
    place(proto_lab, 8, 580, Name="T7")

    # EN must be 1 in the initial condition, so the trip is an INVERTED compare:
    #   output = OL when input <= X  ->  OL = 1 (time <= t), OH = 0 (time > t).
    # One block, algebraically 1 at t = 0, no summing junction.
    y = 586
    for bus in (9, 39, 31, 32, 37):
        if bus in (9, 39):
            # compare with an unreachable threshold: input <= 1e6 always -> OL = 1 (constant 1)
            place(proto_cmp, 14, y, X="1000000", OL="1", OH="0")
            place(proto_lab, 12, y, Name="T7")
            place(proto_lab, 16, y, Name=f"SEN{bus}")
            print(f"  bus {bus}: EN = 1 (compare X=1e6, OL=1)")
        else:
            t = times[bus]
            place(proto_cmp, 14, y, X=str(t), OL="1", OH="0")     # O (16,y)
            place(proto_lab, 12, y, Name="T7")
            place(proto_lab, 16, y, Name=f"SEN{bus}")
            print(f"  bus {bus}: EN = 1 for t <= {t} s, 0 after")
        y += 8

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - 5 EN drivers (buses {sorted(PINS)})")


if __name__ == "__main__":
    main()
