"""Stage 9, prevention measure 2: reactive support at the plant collectors (S22).

Five 150 Mvar capacitor banks, one per collector (B33/B34/B35/B36/B38), added to the emergent-cascade
case. Each is a `master:capacitive_load` whose A pin carries the collector's node label and whose G pin
is grounded - the pattern proven in run 83 (300 Mvar at the bus-36 transformer). Node cost: one per bank.

The point of the test is direction, not gain: the emergent cascade is driven by **overvoltage** trips, so
capacitive support is expected to *raise* collector voltage and make the cascade worse. That is a real
prevention result either way.

usage: python stage9/add_collector_caps.py --pscx X [--mvar 150]
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350012001]
COLLECTORS = ["B33", "B34", "B35", "B36", "B38"]


def nid():
    ID[0] += 1
    return str(ID[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--mvar", default="150")
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

    proto_cap = [c for c in walk(sch) if (c.get("defn") or "") == "master:capacitive_load"]
    if not proto_cap:
        raise SystemExit("no master:capacitive_load prototype in Main")
    proto_cap = proto_cap[0]
    proto_lab = [c for c in walk(sch) if (c.get("defn") or "").endswith(":nodelabel")][0]
    proto_gnd = [c for c in walk(sch) if (c.get("defn") or "") == "master:ground"][0]

    for i, net in enumerate(COLLECTORS):
        x, y = 10 + 10 * i, 690
        cap = copy.deepcopy(proto_cap)
        cap.set("id", nid())
        cap.set("x", str(x * G))
        cap.set("y", str(y * G))
        for q in cap.find("paramlist").findall("param"):
            if q.get("name") == "S":
                q.set("value", a.mvar)
            elif q.get("name") == "V":
                q.set("value", "230.94")
            elif q.get("name") == "F":
                q.set("value", "50")
            elif q.get("name") == "SD":
                q.set("value", "STAR")
            elif q.get("name") == "Name":
                q.set("value", f"CAP_{net}")
        sch.append(cap)

        lab = copy.deepcopy(proto_lab)
        lab.set("id", nid())
        lab.set("x", str(x * G))
        lab.set("y", str(y * G))
        for q in lab.find("paramlist").findall("param"):
            if q.get("name") == "Name":
                q.set("value", net)
        sch.append(lab)

        g = copy.deepcopy(proto_gnd)
        g.set("id", nid())
        g.set("x", str(x * G))
        g.set("y", str((y + 2) * G))
        sch.append(g)
        print(f"  {a.mvar} Mvar at {net} (cap at {x},{y}, G grounded)")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - 5 x {a.mvar} Mvar collector banks")


if __name__ == "__main__":
    main()
