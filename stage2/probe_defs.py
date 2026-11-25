"""Print one definition out of a .pscx, and/or list all 'import'/'export' users in it."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(sys.argv[1])
NAME = sys.argv[2] if len(sys.argv) > 2 else ""
RAW = "--raw" in sys.argv

tree = ET.parse(SRC)
root = tree.getroot()
for d in root.iter("Definition"):
    if NAME and d.get("name") != NAME:
        continue
    if RAW:
        print(ET.tostring(d, encoding="unicode"))
        continue
    sch = d.find("schematic")
    print("=== DEF", d.get("name"), "id", d.get("id"), "classid", d.get("classid"))
    if sch is None:
        continue
    for u in sch.iter("User"):
        pl = u.find("paramlist")
        params = {p.get("name"): p.get("value") for p in (pl.findall("param") if pl is not None else [])}
        print(f'  {u.get("defn"):<22} x={int(u.get("x"))//18:>3} y={int(u.get("y"))//18:>3} '
              f'Name={params.get("Name", "")!r}')
