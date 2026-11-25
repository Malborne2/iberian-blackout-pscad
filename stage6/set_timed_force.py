"""Replace the constant FRC driver with a TIME-TRIGGERED force (S22, Stage 5 G5 clause 3).

The S22 run with `FRC = 1` from t = 0 aborted at start-up (no valid initial condition: every
converter is blocked at the first solve). This script swaps the `master:const` at (84,8) for
`compare(time > t_force)` so the loss happens inside the run, after a healthy pre-event window.

Cloned from the LFDD relay's own (proven) `time-sig` and `compare` blocks; signal only, 0 nodes.

usage: python stage6/set_timed_force.py --pscx C:\\PSCAD_work\\ib4hv.pscx --t 0.5
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350004001]


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
    ap.add_argument("--t", default="0.5")
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

    allc = list(walk(sch))
    const = [c for c in allc
             if c.tag == "User" and (c.get("defn") or "") == "master:const"
             and grid(c) == (84, 8)]
    tsig = [c for c in allc if c.tag == "User" and (c.get("defn") or "") == "master:time-sig"]
    cmp_ = [c for c in allc if c.tag == "User" and (c.get("defn") or "") == "master:compare"]
    if len(const) != 1 or not tsig or not cmp_:
        raise SystemExit(f"prototypes: const={len(const)} time-sig={len(tsig)} compare={len(cmp_)}")

    # 1) remove the constant that held FRC at 0 (its output pin carried the FRC datalabel)
    sch.remove(const[0])

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

    # 2) time-sig at (78,8), output pin (80,8); compare at (84,8): input (82,8), output (86,8)
    place(tsig[0], 78, 8, Name="")
    place(cmp_[0], 84, 8, X=str(a.t), OL="0", OH="1")

    # 3) one net carries time from the source to the comparator
    proto_lab = [c for c in allc if c.tag == "User" and (c.get("defn") or "").endswith(":datalabel")][0]
    for x, y in ((80, 8), (82, 8)):
        place(proto_lab, x, y, Name="T6")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - FRC = (time > {a.t} s), 0 nodes")


if __name__ == "__main__":
    main()
