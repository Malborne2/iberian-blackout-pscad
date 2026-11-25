"""Print the master-library definitions for a list of names (doc string + port semantics)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MASTER = Path(r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx")
WANT = sys.argv[1:] or ["sandhdefn"]

root = ET.parse(MASTER).getroot()
for d in root.iter("Definition"):
    if d.get("name") in WANT:
        print("=" * 70)
        print("DEF", d.get("name"), d.get("id"))
        pl = d.find("paramlist")
        if pl is not None:
            for p in pl.findall("param"):
                print("   param", p.get("name"), "=", (p.get("value") or "")[:400])
        svg = d.find("svg")
        if svg is not None:
            for port in svg.findall("port"):
                print("   port", port.attrib)
        for t in d.iter("text"):
            if (t.text or "").strip():
                print("   text:", t.text.strip()[:100])
