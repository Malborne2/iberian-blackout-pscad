"""Dump the geometry around one bus: elements within a grid-unit window."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
x0, x1, y0, y1 = (int(v) for v in sys.argv[2:6])
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")


def params(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


for e in sc:
    x, y = int(e.get("x") or 0) // 18, int(e.get("y") or 0) // 18
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        continue
    if e.tag in ("Wire", "Bus"):
        vs = [(int(v.get("x")) // 18, int(v.get("y")) // 18) for v in e.findall("vertex")]
        print(f"{e.tag:14} id={e.get('id'):>12} ({x},{y}) verts={vs}")
    elif e.tag == "User":
        p = params(e)
        nm = p.get("Name") or p.get("P") or p.get("Ph") or p.get("Vrms") or ""
        print(f"{e.get('defn'):22} id={e.get('id'):>12} ({x},{y}) orient={e.get('orient')} name={nm!r} "
              f"Es={p.get('Es')} PO={p.get('PO')}")
