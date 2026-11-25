"""Dump the wire vertices of one T line definition."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1]
NAME = sys.argv[2]
root = ET.parse(PSCX).getroot()
d = [e for e in root.find("definitions") if e.get("name") == NAME][0]
sc = d.find("schematic")
for e in sc:
    if e.tag != "Wire":
        continue
    print("Wire", e.attrib)
    for v in e:
        print("   ", v.tag, v.attrib)
