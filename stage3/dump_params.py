"""Print full parameter lists of chosen elements (by id) in a project's Main."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1]
IDS = set(sys.argv[2].split(","))
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
for e in main.find("schematic"):
    if e.tag == "User" and e.get("id") in IDS:
        pl = e.find("paramlist")
        print(e.get("defn"), e.get("id"), e.get("x"), e.get("y"))
        print("   ", {p.get("name"): p.get("value") for p in pl.findall("param")})
