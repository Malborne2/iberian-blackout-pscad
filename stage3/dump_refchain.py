"""Dump the reference-chain band (y <= 24) of RES_Plant in a project file."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
d = [e for e in root.find("definitions") if e.get("name") == "RES_Plant"][0]
sc = d.find("schematic")


def P(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


for e in sc:
    y = int(e.get("y") or 0) // 18
    if y > 24:
        continue
    if e.tag == "Wire":
        x0, y0 = int(e.get("x")), int(e.get("y"))
        pts = [((x0 + int(v.get("x"))) // 18, (y0 + int(v.get("y"))) // 18) for v in e.findall("vertex")]
        print(f"Wire  id={e.get('id'):>11} {pts}")
    elif e.tag == "User":
        p = P(e)
        keep = {k: v for k, v in p.items() if k in ("Name", "G", "Value", "A", "B", "C", "D", "E", "F", "Dim",
                                                    "Const", "UL", "LL", "GP", "TI")}
        print(f"{e.get('defn'):22} id={e.get('id'):>11} ({int(e.get('x')) // 18:3},{y:3}) orient={e.get('orient')} {keep}")
