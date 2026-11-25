"""Report overlaps around every RES_Plant instance on Main (grid units)."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")


def P(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


pts = []          # (x, y, kind, id, name) of every element's reference point
for e in sc:
    if e.tag == "User":
        pts.append((int(e.get("x")) // 18, int(e.get("y")) // 18, e.get("defn"), e.get("id"),
                    P(e).get("Name") or P(e).get("Ph") or ""))
    elif e.tag in ("Wire", "Bus"):
        wx, wy = int(e.get("x")), int(e.get("y"))
        for v in e.findall("vertex"):
            pts.append(((wx + int(v.get("x"))) // 18, (wy + int(v.get("y"))) // 18,
                        e.tag, e.get("id"), ""))

plants = [p for p in pts if p[2] == "iberia4:RES_Plant"]
print(f"{len(plants)} plants")
for px, py, _, pid, _ in plants:
    print(f"\nplant {pid} at ({px},{py})")
    for (x, y, k, i, nm) in pts:
        if k == "iberia4:RES_Plant":
            continue
        if abs(x - px) <= 3 and abs(y - py) <= 2:
            print(f"   IN BOX   ({x},{y}) {k} id={i} {nm!r}")
    for (x, y, k, i, nm) in pts:
        if k == "iberia4:RES_Plant" or not (abs(x - px) <= 4 and abs(y - py) <= 4):
            continue
        if abs(x - px) > 3 or abs(y - py) > 2:
            print(f"   near     ({x},{y}) {k} id={i} {nm!r}")
