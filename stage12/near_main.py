r"""S26: list Main-canvas objects in a rectangle, with their labels and key params (offline).

usage: python stage12\near_main.py <pscx> x0 x1 y0 y1
"""
import sys, xml.etree.ElementTree as ET

src = sys.argv[1]
x0, x1, y0, y1 = (float(v) for v in sys.argv[2:6])
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
M = D["Main"].find("schematic")
KEEP = ("Name", "Value", "Tap", "PO", "QO", "VBO", "T1", "T2", "Tap1", "Tap2", "Tmva", "Rn", "Xn")


def P(el):
    pl = el.find("paramlist")
    return {} if pl is None else {q.get("name"): q.get("value") for q in pl.findall("param")}


for c in M:
    if c.get("x") is None or c.get("y") is None:
        continue
    gx, gy = int(c.get("x")) / 18.0, int(c.get("y")) / 18.0
    if x0 <= gx <= x1 and y0 <= gy <= y1:
        p = P(c)
        keep = {k: v for k, v in p.items() if k in KEEP}
        print(f"{int(gx):3d},{int(gy):3d}  {(c.get('defn') or 'wire'):24s} id={c.get('id'):>10s} {keep}")
