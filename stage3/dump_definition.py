"""Dump one definition (canvas) from master.pslx or any .pscx: components, params, wires."""
import sys
import xml.etree.ElementTree as ET

G = 18
path = sys.argv[1]
name = sys.argv[2]

root = ET.parse(path).getroot()
for d in root.iter("Definition"):
    if d.get("name") != name:
        continue
    print("definition", name, "id", d.get("id"))
    svg = d.find("svg")
    if svg is not None:
        for p in svg.findall("port"):
            print(f"  port {p.get('name'):<6} dim {p.get('dim'):<3} {p.get('mode'):<8} {p.get('type'):<8} "
                  f"at ({int(p.get('x'))//G},{int(p.get('y'))//G}) cond={p.text}")
    sch = d.find("schematic")
    if sch is None:
        continue
    for u in sch.findall("User"):
        pl = u.find("paramlist")
        nm = ""
        if pl is not None:
            for p in pl.findall("param"):
                if p.get("name") == "Name":
                    nm = p.get("value") or ""
        print(f"  {u.get('defn'):<26} {nm:<10} ({int(u.get('x'))//G},{int(u.get('y'))//G}) orient={u.get('orient')}")
    print("  --- wires")
    for w in sch.findall("Wire"):
        x0, y0 = int(w.get("x")) // G, int(w.get("y")) // G
        pts = [(x0 + int(v.get("x")) // G, y0 + int(v.get("y")) // G) for v in w.findall("vertex")]
        print("    " + " -> ".join(f"({a},{b})" for a, b in pts))
