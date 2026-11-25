r"""S26: dump ALL parameters of the blocks whose defn matches, plus nearby datalabel names.

usage: python stage12\dump_block.py <pscx> <definition> <shortdefn> [x0 x1 y0 y1]
"""
import sys, xml.etree.ElementTree as ET

src, defn, short = sys.argv[1], sys.argv[2], sys.argv[3]
box = [float(v) for v in sys.argv[4:8]] if len(sys.argv) > 7 else None
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
S = D[defn].find("schematic")


def gx(el):
    return int(el.get("x")) / 18.0, int(el.get("y")) / 18.0


labs = []
for x in S:
    if (x.get("defn") or "").split(":")[-1] == "datalabel":
        p = {q.get("name"): q.get("value") for q in x.find("paramlist").findall("param")}
        labs.append((gx(x), p.get("Name")))

for x in S:
    if (x.get("defn") or "").split(":")[-1] != short:
        continue
    g = gx(x)
    if box and not (box[0] <= g[0] <= box[1] and box[2] <= g[1] <= box[3]):
        continue
    p = {q.get("name"): q.get("value") for q in x.find("paramlist").findall("param")}
    print(f"--- {short} id={x.get('id')} at {g[0]:.0f},{g[1]:.0f}")
    for k, v in p.items():
        print(f"    {k:12s} = {v}")
    near = sorted(labs, key=lambda z: (abs(z[0][0] - g[0]) + abs(z[0][1] - g[1])))[:6]
    print("    near labels: " + ", ".join(f"{n}@({q[0]:.0f},{q[1]:.0f})" for q, n in near))
