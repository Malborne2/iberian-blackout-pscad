"""WP2 - flatten the `T<a>_<b>` PI line modules of iberia4 onto Main.

For every requested line module instance on `Main`, the script

  1. takes the `master:pi_section` component out of the module definition (with its exact
     parameter list) and places a copy on `Main` at the instance's anchor, with the instance's
     orientation - so its two electrical ports sit 1 grid unit either side of the anchor instead
     of the module's 2;
  2. adds a 1-grid stub wire from each module port coordinate to the new pi_section port, so the
     existing network wires still land on a node;
  3. deletes the instance element (the definition is left in place, unused, until the build
     proves the page count).

Port coordinates are NOT derived from geometry guesses alone: every instance's two port
coordinates are read from `line_ports.json`, which was produced with `pscad_get_ports` on the
live project (rule "never assume, always read back"), and the script asserts that the coordinates
it computes from the definition `<graphics>` ports and the instance orientation agree with it.

Rule B1: this is a bulk structural edit, done on the .pscx with the project unloaded (skill P12).

Usage
-----
    python stage1\\flatten_lines.py --pscx C:\\PSCAD_work\\iberia4.pscx \\
        --lines T13_14,T17_18,T23_24 [--dry]

    --lines all   flattens every remaining instance
"""
import argparse
import copy
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
PORTS = os.path.join(HERE, "line_ports.json")

# orient code -> mapping of a local (dx, dy) offset, in 1/18 grid units, to the canvas offset
ORIENT = {
    0: lambda dx, dy: (dx, dy),
    1: lambda dx, dy: (-dy, dx),     # 90 deg, in at the bottom (measured: T23_24)
    2: lambda dx, dy: (-dx, -dy),
    3: lambda dx, dy: (dy, -dx),     # 90 deg, in at the top (measured: T13_14, T2_25)
}

NAME_RE = re.compile(r"^T\d+_\d+$")


def all_ids(root):
    ids = set()
    for e in root.iter():
        v = e.get("id")
        if v and v.lstrip("-").isdigit():
            ids.add(int(v))
    return ids


class IdGen:
    def __init__(self, used):
        self.used = set(used)
        self.n = 1600000000

    def next(self):
        while self.n in self.used:
            self.n += 1
        v = self.n
        self.used.add(v)
        self.n += 1
        return v


def port_pairs(defn):
    """Map each port name to its local offset (1/18 grid units), from the definition.

    The <graphics> Port elements carry no name, so they are paired with the <schematic> xnodes
    that define the port names by *sorted position* (both are drawn left to right). Pairing by
    document order is wrong: T17_18 has them in the opposite order.
    """
    g = defn.find("graphics")
    if g is None:
        raise SystemExit(f"definition {defn.get('name')}: no <graphics>")
    ports = sorted((p for p in g if p.tag == "Port"),
                   key=lambda p: (int(p.get("x")), int(p.get("y"))))
    xnodes = sorted((u for u in defn.find("schematic")
                     if u.tag == "User" and u.get("defn") == "master:xnode"),
                    key=lambda u: (int(u.get("x")), int(u.get("y"))))
    if len(ports) != len(xnodes):
        raise SystemExit(f"{defn.get('name')}: {len(ports)} ports vs {len(xnodes)} xnodes")
    out = {}
    for p, x in zip(ports, xnodes):
        nm = x.find("paramlist").find("param").get("value")
        out[nm] = (int(p.get("x")), int(p.get("y")))
    return out


def pi_ports(defn):
    """Local offsets of the pi_section's two electrical ports, from master.pslx conventions."""
    # master:pi_section has ports at local (-18, 0) and (+18, 0) [seen in master.pslx].
    return (-18, 0), (18, 0)


def wire(parent, x18, y18, dx, dy, idg, before):
    w = ET.Element("Wire", {
        "classid": "WireOrthogonal", "id": str(idg.next()), "name": "",
        "x": str(x18), "y": str(y18), "w": str(abs(dx) + 10), "h": str(abs(dy) + 10),
        "orient": "0", "disable": "false",
    })
    ET.SubElement(w, "vertex", {"x": "0", "y": "0"})
    ET.SubElement(w, "vertex", {"x": str(dx), "y": str(dy)})
    idx = list(parent).index(before) if before is not None else len(list(parent))
    parent.insert(idx, w)
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--lines", default="all", help="'all' or a comma-separated list like T13_14,T4_5")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    root = ET.parse(a.pscx).getroot()
    defs = root.find("definitions")
    main_def = [d for d in defs if d.get("name") == "Main"][0]
    sc = main_def.find("schematic")

    measured = {e["defn"]: e for e in json.load(open(PORTS, encoding="utf-8"))["instances"]}

    inst_el = {}
    for e in sc:
        if e.tag == "User" and (e.get("defn") or "").startswith("iberia4:"):
            nm = e.get("defn").split(":", 1)[1]
            if NAME_RE.match(nm):
                inst_el[nm] = e

    todo = sorted(inst_el) if a.lines == "all" else [s.strip() for s in a.lines.split(",") if s.strip()]
    missing = [t for t in todo if t not in inst_el]
    if missing:
        raise SystemExit(f"no instance on Main for: {missing}")

    idg = IdGen(all_ids(root))
    grouping = sc.find("grouping")
    before = grouping if grouping is not None else None

    # keep the new elements tidy: insert before <grouping>, else append
    for name in todo:
        e = inst_el[name]
        d = [x for x in defs if x.get("name") == name][0]
        ax, ay = int(e.get("x")), int(e.get("y"))            # 1/18 grid units
        orient = int(e.get("orient") or 0)

        m = measured[name]
        if [ax // 18, ay // 18] != list(m["loc"]):
            raise SystemExit(f"{name}: anchor {ax // 18},{ay // 18} != measured {m['loc']}")

        # 1. check the port coordinates we compute against the ones measured with the tool
        pp = port_pairs(d)
        for pn in ("in", "out"):
            dx, dy = pp[pn]
            ox, oy = ORIENT[orient](dx, dy)
            got = ((ax + ox) // 18, (ay + oy) // 18)
            want = tuple(m[pn])
            if got != want:
                raise SystemExit(f"{name}.{pn}: computed {got} != measured {want}")

        # 2. copy the pi_section from the definition, re-anchor it, keep its parameters verbatim
        pi_src = [u for u in d.find("schematic") if u.tag == "User" and u.get("defn") == "master:pi_section"][0]
        pi = copy.deepcopy(pi_src)
        pi.set("id", str(idg.next()))
        pi.set("x", str(ax))
        pi.set("y", str(ay))
        pi.set("orient", str(orient))
        if "layer" not in pi.attrib:
            pi.set("layer", "")
        if "q" not in pi.attrib:
            pi.set("q", "4")
        if before is not None:
            sc.insert(list(sc).index(before), pi)
        else:
            sc.append(pi)

        # 3. stubs: module port -> pi_section port
        (p1, p2) = pi_ports(d)
        for pn, local in (("in", p1), ("out", p2)):
            ox, oy = ORIENT[orient](local[0], local[1])
            tx, ty = ax + ox, ay + oy
            mx, my = m[pn][0] * 18, m[pn][1] * 18
            wire(sc, mx, my, tx - mx, ty - my, idg, before)
            print(f"  {name:8} {pn:3} ({mx // 18},{my // 18}) -> ({tx // 18},{ty // 18})")

        # 4. delete the instance
        sc.remove(e)
        print(f"  {name:8} pi_section at ({ax // 18},{ay // 18}) orient {orient}; instance {e.get('id')} removed")

    if a.dry:
        print("dry run: file not written")
        return

    with open(a.pscx, "w", encoding="utf-8") as fh:
        fh.write(ET.tostring(root, encoding="unicode"))
    print(f"wrote {a.pscx}: {len(todo)} line module(s) flattened")


if __name__ == "__main__":
    sys.exit(main())
