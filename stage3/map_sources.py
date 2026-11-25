"""Map the remaining ideal sources to their buses: multimeter names, source P/Q names, positions."""
import sys
import xml.etree.ElementTree as ET

PSCX = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
main = [e for e in root.find("definitions") if e.get("name") == "Main"][0]
sc = main.find("schematic")


def params(e):
    pl = e.find("paramlist")
    if pl is None:
        return {}
    return {p.get("name"): p.get("value") for p in pl.findall("param")}


print("== source3 ==")
for e in sc:
    if e.tag == "User" and e.get("defn") == "master:source3":
        p = params(e)
        print(f"  id={e.get('id')} x={int(e.get('x'))//18} y={int(e.get('y'))//18} "
              f"P={p.get('P')!r} Q={p.get('Q')!r} Es={p.get('Es')} Ph={p.get('Ph')} Vm={p.get('Vm')} F={p.get('F')}")

print("== multimeter ==")
for e in sc:
    if e.tag == "User" and e.get("defn") == "master:multimeter":
        p = params(e)
        print(f"  id={e.get('id')} x={int(e.get('x'))//18} y={int(e.get('y'))//18} "
              f"Name={p.get('Name')!r} S={p.get('S')}")

print("== fixed_load (bus, P) ==")
for e in sc:
    if e.tag == "User" and e.get("defn") == "master:fixed_load":
        p = params(e)
        po = float(p.get("PO") or 0)
        print(f"  id={e.get('id')} x={int(e.get('x'))//18} y={int(e.get('y'))//18} PO={po:.2f} QO={p.get('QO')}")

print("== nodelabels ==")
for e in sc:
    if e.tag == "User" and e.get("defn") == "master:nodelabel":
        p = params(e)
        print(f"  id={e.get('id')} x={int(e.get('x'))//18} y={int(e.get('y'))//18} Name={p.get('Name')!r}")
