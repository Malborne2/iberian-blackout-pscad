"""Dump Main elements in a window (file units, 1/18 grid), to copy the plant-group pattern."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
YMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 400
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")
for e in sc:
    if e.tag in ("Wire", "Bus"):
        y = int(e.get("y"))
        if y > YMAX:
            continue
        vs = [(v.get("x"), v.get("y")) for v in e.findall("vertex")]
        print(f"{e.tag:16} id={e.get('id'):>12} x={e.get('x'):>5} y={e.get('y'):>5} w={e.get('w'):>4} h={e.get('h'):>4} verts={vs}")
    elif e.tag == "User" and int(e.get("y")) <= YMAX:
        pl = e.find("paramlist")
        nm = ""
        if pl is not None:
            for p in pl.findall("param"):
                if p.get("name") in ("Name", "name"):
                    nm = p.get("value")
        print(f"USER {e.get('defn'):22} id={e.get('id'):>12} x={e.get('x'):>5} y={e.get('y'):>5} "
              f"w={e.get('w')} h={e.get('h')} orient={e.get('orient')} name={nm!r}")
