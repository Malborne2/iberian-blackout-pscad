r"""S26: list the named bus wires (master:wire with a Name) on Main, with their bounding boxes.

usage: python stage12/list_buses.py <pscx>
"""
import sys, xml.etree.ElementTree as ET

src = sys.argv[1]
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
M = D["Main"].find("schematic")
for c in M:
    if c.tag != "Wire":
        continue
    pl = c.find("paramlist")
    nm = ""
    if pl is not None:
        for q in pl.findall("param"):
            if q.get("name") == "Name":
                nm = q.get("value") or ""
    if not nm:
        continue
    x, y, w, h = (int(c.get(k)) // 18 for k in ("x", "y", "w", "h"))
    vs = [(int(v.get("x")) // 18, int(v.get("y")) // 18) for v in c.findall("vertex")]
    print(f"{nm:8s} id={c.get('id'):>10s} box ({x},{y}) {w}x{h} verts {vs}")
