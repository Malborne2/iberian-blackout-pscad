r"""S26: list the breaker/relay `compare` blocks on Main by their row (y in grid units).

usage: python stage12\list_trips.py <pscx>
Prints id, x, y, X (trip time or threshold), OL/OH, and the datalabel names within 3 grid units
(the signal the compare drives), so the breaker trip rows can be set without guessing.
"""
import sys, xml.etree.ElementTree as ET

src = sys.argv[1]
r = ET.parse(src).getroot()
D = {d.get("name"): d for d in r.iter("Definition")}
M = D["Main"].find("schematic")


def P(el):
    return {q.get("name"): q.get("value") for q in el.find("paramlist").findall("param")}


labs = []
for c in M:
    if (c.get("defn") or "").split(":")[-1] == "datalabel" and c.get("x"):
        labs.append((int(c.get("x")) / 18.0, int(c.get("y")) / 18.0, P(c).get("Name")))

for c in M:
    d = (c.get("defn") or "").split(":")[-1]
    if d not in ("compare", "delay", "pi_ctlr", "const") or not c.get("x"):
        continue
    y = int(c.get("y")) / 18.0
    if y < 380:
        continue
    p = P(c)
    near = sorted(labs, key=lambda z: abs(z[0] - int(c.get("x")) / 18.0) + abs(z[1] - y))[:3]
    print(f"{d:10s} id={c.get('id'):>10s} x={int(c.get('x'))/18:5.0f} y={y:5.0f} "
          f"X={p.get('X')} OH={p.get('OH')} OL={p.get('OL')} T={p.get('T')} | "
          + ", ".join(f"{n}@({x:.0f},{yy:.0f})" for x, yy, n in near))
