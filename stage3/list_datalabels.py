"""All datalabels of Main with positions, and what sits on their port."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")


def params(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


users = []
for e in sc:
    if e.tag == "User":
        users.append((int(e.get("x")), int(e.get("y")), e.get("defn"), e.get("id"), params(e)))

for x, y, d, i, p in sorted(users):
    if d == "master:datalabel":
        print(f"datalabel {p.get('Name')!r:8} at ({x // 18},{y // 18}) id={i}")
