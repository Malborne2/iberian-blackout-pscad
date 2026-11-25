"""G8 counterfactual 3: eight 250 MVA synchronous condensers (S22, Stage 8).

The report says eight 250 MVA condensers prevent the collapse (p.310). This script clones the case's own
`SyncUnit` - which is what a condenser is here: a machine with **P0 = 0**, an exciter holding its
terminal voltage, and H = 2.5 s of inertia - and attaches eight of them to the plant collector nets
(B33/B34/B35/B36/B38, exposed as node labels), distributed 2/2/2/1/1.

Measured geometry: a `SyncUnit` placed at (x, y) has its electrical pin **T at (x+3, y)**, so the node
label is written there.

usage: python stage8/add_condensers.py --pscx X [--count 8] [--mva 250]
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350010001]
COLLECTORS = ["B33", "B34", "B35", "B36", "B38"]


def nid():
    ID[0] += 1
    return str(ID[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--mva", default="250")
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

    units = [c for c in walk(sch) if c.tag == "User" and (c.get("defn") or "").endswith(":SyncUnit")]
    if not units:
        raise SystemExit("no SyncUnit instance to clone")
    proto = units[0]
    proto_lab = [c for c in walk(sch) if c.tag == "User" and (c.get("defn") or "").endswith(":nodelabel")][0]

    for i in range(a.count):
        el = copy.deepcopy(proto)
        el.set("id", nid())
        x = 10 + 16 * (i % 4)
        y = 700 + 16 * (i // 4)
        el.set("x", str(x * G))
        el.set("y", str(y * G))
        net = COLLECTORS[i % len(COLLECTORS)]
        for q in el.find("paramlist").findall("param"):
            n = q.get("name")
            if n == "Sbase":
                q.set("value", a.mva)
            elif n in ("P0", "Q0", "Ph0"):
                q.set("value", "0")
            elif n == "V0":
                q.set("value", "1.05")
            elif n == "Vctl":
                q.set("value", "1.05")
            elif n == "H":
                q.set("value", "2.5")
        sch.append(el)

        lab = copy.deepcopy(proto_lab)
        lab.set("id", nid())
        lab.set("x", str((x + 3) * G))
        lab.set("y", str(y * G))
        for q in lab.find("paramlist").findall("param"):
            if q.get("name") == "Name":
                q.set("value", net)
        sch.append(lab)
        print(f"  condenser {i+1}: {a.mva} MVA at ({x},{y}) -> net {net}")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - {a.count} x {a.mva} MVA synchronous condensers")


if __name__ == "__main__":
    main()
