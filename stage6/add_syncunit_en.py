"""Add a signal EN gate to the SyncUnit definition (S22, machine-side trip path).

Measured geometry (master.pslx, grid units of 18 px): `mult` IN1 = (x-2, y), IN2 = (x, y+2),
OUT = (x+2, y); `import` port N = (x+2, y); `datalabel` port = (x, y).

Inside the definition the mechanical power is the net `TMECH` (= Pmec + DPGOV), read by the machine at
(23,25). The gate is inserted by name, not by geometry:

    TMECH (sources)  ->  mult IN1       mult OUT -> TMECH_g  ->  machine pin (23,25)
    EN    (new port) ->  mult IN2

Nothing else in the definition moves. The new `EN` import becomes a signal port on every SyncUnit
instance, which must then be driven on Main (a second script does that).

usage: python stage6/add_syncunit_en.py --pscx C:\\PSCAD_work\\ib4hv.pscx
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350007001]


def nid():
    ID[0] += 1
    return str(ID[0])


def grid(el):
    try:
        return (int(el.get("x")) // G, int(el.get("y")) // G)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    d = [x for x in root.find("definitions") if x.get("name") == "SyncUnit"][0]
    sch = d.find("schematic")

    def walk(el):
        for c in el:
            yield c
            if c.tag != "User":
                yield from walk(c)

    allc = list(walk(sch))
    if any((c.get("defn") or "") == "master:mult" and grid(c) == (40, 60) for c in allc):
        raise SystemExit("gate already present at (40,60) - refusing to duplicate")

    # 1) the machine's mechanical-power pin becomes the GATED net
    machine_pin = (23, 25)
    hit = [c for c in allc if c.tag == "User" and (c.get("defn") or "").endswith(":datalabel")
           and grid(c) == machine_pin
           and any(p.get("name") == "Name" and p.get("value") == "TMECH"
                   for p in c.find("paramlist").findall("param"))]
    if len(hit) != 1:
        raise SystemExit(f"expected the TMECH label at {machine_pin}, found {len(hit)}")
    for p in hit[0].find("paramlist").findall("param"):
        if p.get("name") == "Name":
            p.set("value", "TMECH_g")

    # 2) multiplier + its three labels (connected by net name)
    # a mult prototype can come from any definition (SyncUnit has none of its own)
    global_users = [c for dd in root.find("definitions") for c in walk(dd.find("schematic"))
                    if c.tag == "User"]
    proto_mult = [c for c in global_users if (c.get("defn") or "") == "master:mult"]
    proto_imp = [c for c in allc if (c.get("defn") or "") == "master:import"][0]
    proto_lab = [c for c in allc if (c.get("defn") or "").endswith(":datalabel")][0]

    def place(proto, x, y, **vals):
        el = copy.deepcopy(proto)
        el.set("id", nid())
        el.set("x", str(x * G))
        el.set("y", str(y * G))
        pl = el.find("paramlist")
        for q in pl.findall("param"):
            if q.get("name") in vals:
                q.set("value", str(vals.pop(q.get("name"))))
        for k, v in vals.items():
            ET.SubElement(pl, "param", {"name": k, "value": str(v)})
        sch.append(el)
        return el

    if proto_mult:
        mult = copy.deepcopy(proto_mult[0])
        mult.set("id", nid())
        mult.set("x", str(40 * G))
        mult.set("y", str(60 * G))
        sch.append(mult)
        src = "cloned"
    else:
        raise SystemExit("no master:mult prototype inside SyncUnit; add one on Main first")
    print(f"  mult placed at (40,60) [{src}]")

    place(proto_lab, 38, 60, Name="TMECH")     # IN1
    place(proto_lab, 40, 62, Name="EN")        # IN2
    place(proto_lab, 42, 60, Name="TMECH_g")   # OUT

    # 3a) declare the EN input on the module's external interface (svg port + graphics Port),
    #     copying RES_Plant's Force declaration (model Transfer, mode Input, dim 1, type Real).
    svg = d.find("svg")
    port = ET.SubElement(svg, "port", {"name": "EN", "model": "Transfer", "dim": "1",
                                       "mode": "Input", "type": "Real", "x": "-54", "y": "0"})
    print("  svg port EN declared")
    gfx = d.find("graphics")
    gport = ET.SubElement(gfx, "Port", {"id": nid(), "classid": "Port", "x": "-54", "y": "0"})
    gpl = ET.SubElement(gport, "paramlist")
    for k, v in (("name", "EN"), ("internal", "false"), ("cond", "true"), ("mode", "1"),
                 ("datatype", "3"), ("electype", "0"), ("dim", "1")):
        ET.SubElement(gpl, "param", {"name": k, "value": v})
    ET.SubElement(gfx, "Gfx", {"classid": "Graphics.Line", "id": nid(), "x": "-36", "y": "0"})
    ET.SubElement(gfx, "Gfx", {"classid": "Graphics.Text", "id": nid(), "x": "-30", "y": "4"})

    # 3) the EN signal port (import with signal content)
    imp = copy.deepcopy(proto_imp)
    imp.set("id", nid())
    imp.set("x", str(50 * G))
    imp.set("y", str(62 * G))
    pl = imp.find("paramlist")
    for q in pl.findall("param"):
        if q.get("name") == "Name":
            q.set("value", "EN")
        if q.get("name") == "content":      # a port-backed import carries no content tag
            q.set("value", "")
    sch.append(imp)
    place(proto_lab, 52, 62, Name="EN")        # import port N = (x+2, y)

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - SyncUnit EN gate on TMECH (mult + signal import)")


if __name__ == "__main__":
    main()
