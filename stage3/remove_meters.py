"""WP3 node-budget cut #1 (PLAN.md WP3): remove the collector-bus multimeters.

The plan's cut order: "(1) remove the 5 multimeters at the collector buses (3 nodes each; measure
bus voltage inside a plant instead: VA_PU/VDF)".  Measured: a multimeter splits a node, +3 nodes on
a three-phase branch (S17 rule 17), so five meters cost 15 nodes.

A multimeter is in series, so deleting it alone would open the branch: the script joins its two port
points with a wire, then deletes the meter and its `Ph<bus>` recorder branch (datalabel -> wire ->
pgb) which would otherwise be a floating input.

usage: python stage3\\remove_meters.py <pscx> Ph33,Ph34,Ph35,Ph36,Ph38 [--dry]
"""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1]
NAMES = [s.strip() for s in sys.argv[2].split(",") if s.strip()]
DRY = "--dry" in sys.argv
BASE_ID = 1750000000


def params(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


def on_seg(px, py, x1, y1, x2, y2):
    if y1 == y2 == py:
        return min(x1, x2) <= px <= max(x1, x2)
    if x1 == x2 == px:
        return min(y1, y2) <= py <= max(y1, y2)
    return False


root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")
used = {int(e.get("id")) for e in root.iter() if (e.get("id") or "").lstrip("-").isdigit()}
nid = BASE_ID


def next_id():
    global nid
    while nid in used:
        nid += 1
    used.add(nid)
    return nid


dead = []
for name in NAMES:
    m = None
    for e in sc:
        if e.tag == "User" and e.get("defn") == "master:multimeter" and params(e).get("Ph") == name:
            m = e
            break
    if m is None:
        print("!! no multimeter with Ph =", name)
        continue
    x, y = int(m.get("x")), int(m.get("y"))
    # ports are one grid above and below the centre on every collector meter (pscad_get_ports)
    top, bot = (x, y - 18), (x, y + 18)
    inner = {e.get("id"): e for e in sc}[m.get("id")]
    sc.remove(inner)
    w = ET.Element("Wire", {"classid": "WireOrthogonal", "id": str(next_id()), "name": "",
                            "x": str(top[0]), "y": str(top[1]), "w": "10", "h": "46",
                            "orient": "0", "disable": "false"})
    ET.SubElement(w, "vertex", {"x": "0", "y": "0"})
    ET.SubElement(w, "vertex", {"x": "0", "y": str(bot[1] - top[1])})
    sc.append(w)
    print(f"removed multimeter {name} at ({x // 18},{y // 18}); joined ({top[0] // 18},{top[1] // 18})"
          f"-({bot[0] // 18},{bot[1] // 18})")

    # its Ph recorder branch
    for e in list(sc):
        if e.tag == "User" and e.get("defn") == "master:datalabel" and params(e).get("Name") == name:
            dx, dy = int(e.get("x")), int(e.get("y"))
            dead.append(e)
            for wv in list(sc):
                if wv.tag != "Wire":
                    continue
                wx, wy = int(wv.get("x")), int(wv.get("y"))
                vs = [(wx + int(v.get("x")), wy + int(v.get("y"))) for v in wv.findall("vertex")]
                if (dx, dy) not in vs:
                    continue
                dead.append(wv)
                segs = list(zip(vs[:-1], vs[1:])) or [(vs[0], vs[0])]
                for u in list(sc):
                    if u.tag == "User" and u.get("defn") == "master:pgb":
                        p = (int(u.get("x")), int(u.get("y")))
                        if any(on_seg(p[0], p[1], s[0][0], s[0][1], s[1][0], s[1][1]) for s in segs):
                            dead.append(u)

seen = set()
uniq = []
for e in dead:
    if id(e) not in seen:
        seen.add(id(e))
        uniq.append(e)
for e in uniq:
    sc.remove(e)
print(f"removed {len(uniq)} recorder elements for {NAMES}")

if DRY:
    print("dry run: file not written")
    sys.exit(0)
with open(PSCX, "w", encoding="utf-8") as fh:
    fh.write(ET.tostring(root, encoding="unicode"))
print("wrote", PSCX)
