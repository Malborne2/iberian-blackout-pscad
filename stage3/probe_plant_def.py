"""What feeds VD/VQ/VDF/VA_PU inside the RES_Plant definition?"""
import xml.etree.ElementTree as ET

PSCX = r"C:\PSCAD_work\iberia4.pscx"
root = ET.parse(PSCX).getroot()
d = [e for e in root.find("definitions") if e.get("name") == "RES_Plant"][0]
sc = d.find("schematic")


def P(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


print("=== pgb / datalabel named V* ===")
for e in sc:
    if e.tag != "User":
        continue
    p = P(e)
    nm = p.get("Name") or ""
    if (e.get("defn") or "") in ("master:pgb", "master:datalabel") and nm.startswith(("V", "I")):
        print(f"  {e.get('defn'):18} ({int(e.get('x')) // 18:3},{int(e.get('y')) // 18:3}) Name={nm!r}")

print("\n=== voltmeters / abcdq0 / breakout / xnode ===")
for e in sc:
    if e.tag != "User":
        continue
    if (e.get("defn") or "") in ("master:voltmeter", "master:abcdq0", "master:breakout", "master:xnode",
                                 "master:const", "master:gain", "master:import"):
        p = P(e)
        keep = {k: v for k, v in p.items() if k not in ("show_grid", "size", "orient", "show_border")}
        print(f"  {e.get('defn'):18} ({int(e.get('x')) // 18:3},{int(e.get('y')) // 18:3}) {keep}")

print("\n=== wires touching the abcdq0 / voltmeter ===")
for e in sc:
    if e.tag == "Wire":
        vs = [(int(v.get("x")) + int(e.get("x"))) // 18 for v in e.findall("vertex")]
        ys = [(int(v.get("y")) + int(e.get("y"))) // 18 for v in e.findall("vertex")]
        if any(abs(y - 34) <= 3 for y in ys):
            print("  wire", int(e.get("x")) // 18, int(e.get("y")) // 18, list(zip(vs, ys)))
