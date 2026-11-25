"""Find master-library definitions whose name matches a pattern (for the RES_Plant parts list)."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MASTER = Path(r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx")
pat = re.compile(sys.argv[1] if len(sys.argv) > 1 else "bridge|pwm|pll|carrier", re.I)

root = ET.parse(MASTER).getroot()
for d in root.iter("Definition"):
    name = d.get("name") or ""
    if not pat.search(name):
        continue
    desc = ""
    pl = d.find("paramlist")
    if pl is not None:
        for p in pl.findall("param"):
            if p.get("name") == "Description":
                desc = p.get("value") or ""
    ports = []
    svg = d.find("svg")
    if svg is not None:
        for port in svg.findall("port"):
            ports.append(f'{port.get("name")}:{port.get("dim")}:{port.get("mode")}')
    print(f"{name:<28} {desc[:60]:<60} {','.join(ports)}")
