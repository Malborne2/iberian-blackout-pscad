"""Dump one canvas of a .pscx (offline, read-only): components with coords and wires with vertices."""
import sys
import xml.etree.ElementTree as ET

G = 18
path = sys.argv[1]
canvas = sys.argv[2] if len(sys.argv) > 2 else "Main"

root = ET.parse(path).getroot()
for d in root.iter("Definition"):
    if d.get("name") != canvas:
        continue
    sch = d.find("schematic")
    users = sch.findall("User")
    wires = sch.findall("Wire")
    print(f"users {len(users)} wires {len(wires)}")
    for u in users:
        pl = u.find("paramlist")
        nm = ""
        at = f"({int(u.get('x'))//G},{int(u.get('y'))//G})"
        if pl is not None:
            for p in pl.findall("param"):
                if p.get("name") == "Name":
                    nm = p.get("value") or ""
        print(f"{u.get('defn'):<24} {nm:<12} {at:<10} orient={u.get('orient')}")
    print("--- wires")
    for w in wires:
        x0, y0 = int(w.get("x")) // G, int(w.get("y")) // G
        pts = [(x0 + int(v.get("x")) // G, y0 + int(v.get("y")) // G) for v in w.findall("vertex")]
        print("   " + " -> ".join(f"({a},{b})" for a, b in pts))
