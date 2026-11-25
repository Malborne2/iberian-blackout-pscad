"""Build `pv1.pscx` = a clean bench project holding the `RES_Plant1` module definition.

Why a generator and not the MCP tools: the module body is PSCAD's own proven `cv1` plant
(Stage 3, gate G3a), 240-odd objects, and copying it by tool call would be 240 fragile
placements.  The XML is plain, so the *copy* is done here verbatim (no translation: the
definition canvas is set to 100x100, the same grid cv1's Main uses), and everything that
needs port geometry (ammeters, breakout, xnodes, imports, the enable logic, the trip relay)
is added afterwards **through the tools**, where the ports can be read back.

Kept out of the module (measured reasons, see RUNLOG Session 17):
  * the three AC grid sources and their neutral grounds  -> the grid is outside the plant
  * the three C_f capacitors + grounds                    -> one C_f bank per collector bus (PLAN B3)
  * the DC source and the 300 uF DC capacitor             -> the shared rail is outside (PLAN A4)
  * the bench OV-relay stimulus (signalgen/compare/realpole/OV_* labels) -> half torn down in cv1;
                                                            the module gets a real relay on VD
  * VDSET/VQSET unused consts, stray IsrcB/IsrcC recorder wires

Usage:  python build_resplant1.py
"""
from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path

CV1 = Path(r"C:\PSCAD_work\cv1.pscx")          # proven Stage-3 plant (gate G3a)
TPL = Path(r"C:\PSCAD_work\iberia3.pscx")      # holds the SyncUnit definition = XML template
OUT = Path(r"C:\PSCAD_work\pv1.pscx")
XDIR = Path(__file__).resolve().parents[1] / "stage3" / "shells"

DEF_NAME = "RES_Plant1"
DEF_ID = "1300000401"

# ---- components removed from cv1's Main ------------------------------------------------
EXCLUDE = {
    # AC grid sources + their neutral grounds
    566509220, 1730879637, 798985137,
    1450047213, 1916018016, 403942788,
    # C_f capacitors (per collector bus, not per plant) + grounds
    2090806476, 1834721816, 588434843,
    817192576, 2103680270, 1719780337,
    # DC source + DC capacitor
    616798506, 1489860207,
    # bench OV-relay stimulus group (signalgen, compare x2, realpole, VTEST x2,
    # OV_THR x2, OV_DLY x2, OVTRIP label, OVTRIP pgb)
    1311829617, 621056949, 265540723, 1159721490,
    299328971, 1869347433, 1609245735, 908726511,
    1321924807, 2009234536, 410213344, 750956065,
    # stray recorder labels with no pgb
    976900775, 833827770,
    # VDSET/VQSET leftovers of the open-loop bench
    824396612, 132955250, 35834131, 1115391785, 1482574426, 1994777452,
}

# ---- wires removed (ids) ---------------------------------------------------------------
EXCLUDE_W = {
    510917522, 1519903495, 1087696430,   # source neutral -> ground
    2127096284, 401465078, 1378123106,   # C_f feed wires
    8222049,                              # DC capacitor, top
    954020183,                            # DC capacitor, bottom  (replaced below, shortened)
    935248492, 931846009,                 # stray recorder wires
    1329553828,                           # OVTRIP label -> pgb
    83354760, 355219603,                  # VDSET/VQSET gain feeds
}

# the lower DC rail wire, shortened so it ends at the rail instead of at the removed capacitor
FIX_WIRE = {
    954020183: [(13, 45), (13, 47), (28, 47)],
}

# ---- module parameters: name, description, unit, default, type --------------------------
PARAMS = [
    ("Sbase",  "Rated MVA (P/Q channel scaling)",       "MVA", "300.0",        "Real"),
    ("Kv",     "Voltage pu gain = 1/(Vbase*sqrt2/sqrt3) [1/kV]", "1/kV",
                                                               "0.0030618624819579755", "Real"),
    ("Ki",     "Current pu gain = sqrt3*Vbase/(sqrt2*Sbase) [1/kA]", "1/kA",
                                                               "1.6329943237117308", "Real"),
    ("Kmod",   "Modulation constant -Vbase_pk/(Vdc/2)",  "pu",  "-0.8164965",   "Real"),
    ("Kpf",    "Q/P ratio = tan(acos(pf))",              "pu",  "0.17525",      "Real"),
    ("CarrPh", "Carrier phase offset (stagger plants)",  "deg", "0.0",          "Real"),
    ("Vt_1",   "Overvoltage trip threshold",             "pu",  "1.10",         "Real"),
    ("Tt_1",   "Overvoltage trip delay",                 "s",   "0.001",        "Real"),
]

# component field <- module parameter, by component id in cv1
#   the three voltage scaling gains, the three current scaling gains
BIND = {
    449091826: ("G", "Kv"), 544532544: ("G", "Kv"), 522463750: ("G", "Kv"),
    1260774915: ("G", "Ki"), 1568943580: ("G", "Ki"), 1820831203: ("G", "Ki"),
}

PARAM_XML = (
    '    <parameter desc="{desc}" name="{name}" group="" unit="{unit}" min="-1e+308"'
    ' max="+1e+308" content_type="Constant" type="Real" helpmode="Append" intent="Input"'
    ' dim="1" animate="false">\n'
    '      <value>{value}</value>\n      <cond />\n      <help />\n      <vis />\n    </parameter>\n'
)
IMPORT_TMPL = (
    '<User classid="UserCmp" defn="master:import" id="{id}" x="{x}" y="{y}" w="91" h="25"'
    ' z="0" orient="0" link="-1" q="4" disable="false">'
    '<paramlist link="-1" name="" crc="117509081"><param name="Name" value="{name}" /></paramlist>'
    "</User>"
)
XNODE = ('<User classid="UserCmp" name="" defn="master:xnode" id="{id}" x="{x}" y="{y}"'
         ' w="20" h="33" z="1" orient="0" link="-1" q="4" disable="false">'
         '<paramlist link="-1" name="" crc="37312176"><param name="Name" value="{name}" /></paramlist>'
         "</User>")

G = 18


def grid(el):
    return (int(el.get("x")) // G, int(el.get("y")) // G)


def main():
    src = ET.parse(CV1).getroot()
    tpl_root = ET.parse(TPL).getroot()

    main_def = [d for d in src.iter("Definition") if d.get("name") == "Main"][0]
    main_sch = main_def.find("schematic")

    # ---------------------------------------------------------------- definition skeleton
    shell = None
    for d in tpl_root.iter("Definition"):
        if d.get("name") == "SyncUnit":
            shell = copy.deepcopy(d)
    if shell is None:
        raise SystemExit("SyncUnit template not found in iberia3")
    shell.set("name", DEF_NAME)
    shell.set("id", DEF_ID)
    shell.set("crc", "0")
    shell.set("date", "0")
    shell.set("instances", "0")
    pl = shell.find("paramlist")
    for p in list(pl):
        pl.remove(p)
    ET.SubElement(pl, "param", {"name": "Description",
                                "value": "Switching converter plant (2-level IGBT bridge, "
                                         "SRF-PLL + decoupled dq current control, fixed PF)"})

    form = shell.find("form")
    form.set("name", DEF_NAME)
    form.set("w", "340")
    form.set("h", "420")
    cat = form.find("category")
    cat.set("name", "Plant")
    for p in list(cat):
        cat.remove(p)
    for name, desc, unit, value, ptype in PARAMS:
        cat.append(ET.fromstring(PARAM_XML.format(
            name=name, desc=desc, unit=unit, value=value, ptype=ptype)))

    # ---------------------------------------------------------------- symbol ports
    svg = shell.find("svg")
    for p in list(svg.findall("port")):
        svg.remove(p)
    ports = [
        ('<port model="Natural" name="AC" x="54" y="0" dim="3" mode="" type="NonRemovable">true</port>'),
        ('<port model="Natural" name="DCP" x="54" y="-20" dim="1" mode="" type="NonRemovable">true</port>'),
        ('<port model="Natural" name="DCN" x="54" y="20" dim="1" mode="" type="NonRemovable">true</port>'),
        ('<port model="Transfer" name="Pref" x="-54" y="-12" dim="1" mode="Input" type="Real">true</port>'),
        ('<port model="Transfer" name="Force" x="-54" y="12" dim="1" mode="Input" type="Real">true</port>'),
        ('<port model="Transfer" name="Trip" x="-54" y="30" dim="1" mode="Output" type="Real">true</port>'),
    ]
    for i, p in enumerate(ports):
        svg.insert(i, ET.fromstring(p))
    # a few simple connector lines so the symbol shows where the ports are
    for x1, y1, x2, y2 in [(36, 0, 54, 0), (36, -20, 54, -20), (36, 20, 54, 20),
                           (-54, -12, -36, -12), (-54, 12, -36, 12), (-54, 30, -36, 30)]:
        svg.append(ET.fromstring(
            '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="Black" stroke-dasharray="none"'
            ' stroke-width="0.4" port="" />' % (x1, y1, x2, y2)))
    svg.append(ET.fromstring(
        '<text x="0" y="-40" stroke="Black" fill="Black" font-size="Small"'
        ' text-anchor="Middle">RES_Plant1</text>'))

    # ---------------------------------------------------------------- canvas
    sch = shell.find("schematic")
    for child in list(sch):
        if child.tag != "paramlist":
            sch.remove(child)
    for p in sch.find("paramlist").findall("param"):
        if p.get("name") == "size":
            p.set("value", "5")          # 100x100, same as cv1's Main

    # port tags + published parameters
    sch.append(ET.fromstring(XNODE.format(id=1300001001, name="AC", x=10 * G, y=4 * G)))
    sch.append(ET.fromstring(XNODE.format(id=1300001002, name="DCP", x=36 * G, y=31 * G)))
    sch.append(ET.fromstring(XNODE.format(id=1300001003, name="DCN", x=36 * G, y=35 * G)))
    sch.append(ET.fromstring(XNODE.format(id=1300001004, name="Pref", x=30 * G, y=88 * G)))
    sch.append(ET.fromstring(XNODE.format(id=1300001005, name="Force", x=30 * G, y=92 * G)))
    sch.append(ET.fromstring(XNODE.format(id=1300001006, name="Trip", x=90 * G, y=56 * G)))

    n = 0
    for name, *_ in PARAMS:
        n += 1
        sch.append(ET.fromstring(IMPORT_TMPL.format(
            id=1300002000 + n, x=94 * G, y=(6 + 2 * n) * G, name=name)))

    # ---------------------------------------------------------------- the copied group
    kept_users = 0
    for u in main_sch.findall("User"):
        if int(u.get("id")) in EXCLUDE:
            continue
        u = copy.deepcopy(u)
        plist = u.find("paramlist")
        if plist is not None:
            for p in plist.findall("param"):
                if p.get("name") == "Name" and (p.get("value") or "").startswith("VDSET"):
                    p.set("value", "")
        sch.append(u)
        kept_users += 1

    kept_wires = 0
    for w in main_sch.findall("Wire"):
        wid = int(w.get("id"))
        if wid in EXCLUDE_W:
            continue
        w = copy.deepcopy(w)
        if wid in FIX_WIRE:
            pts = FIX_WIRE[wid]
            for v in list(w.findall("vertex")):
                w.remove(v)
            x0 = min(p[0] for p in pts)
            y0 = min(p[1] for p in pts)
            w.set("x", str(x0 * G))
            w.set("y", str(y0 * G))
            w.set("w", str((max(p[0] for p in pts) - x0) * G + 10))
            w.set("h", str((max(p[1] for p in pts) - y0) * G + 10))
            for x, y in pts:
                ET.SubElement(w, "vertex", {"x": str((x - x0) * G), "y": str((y - y0) * G)})
        sch.append(w)
        kept_wires += 1

    # ---------------------------------------------------------------- parameter bindings
    bound = 0
    for u in sch.findall("User"):
        uid = int(u.get("id"))
        b = BIND.get(uid)
        if not b:
            continue
        field, param = b
        plist = u.find("paramlist")
        for p in (plist.findall("param") if plist is not None else []):
            if p.get("name") == field:
                p.set("value", param)
                bound += 1
    # modulator gains (Kmod) and the PF gain (Kpf) and the carrier phase (CarrPh)
    explicit = {
        (28, 82): ("G", "Kmod"), (36, 90): ("G", "Kmod"), (80, 82): ("G", "Kmod"),
        (46, 4): ("G", "Kpf"),
        (8, 90): ("P", "CarrPh"),
    }
    for u in sch.findall("User"):
        pos = (int(u.get("x")) // G, int(u.get("y")) // G)
        if pos in explicit:
            field, param = explicit[pos]
            plist = u.find("paramlist")
            for p in (plist.findall("param") if plist is not None else []):
                if p.get("name") == field:
                    p.set("value", param)
                    bound += 1

    # ---------------------------------------------------------------- write
    out_root = copy.deepcopy(src)
    # empty Main of the bench project
    for d in out_root.iter("Definition"):
        if d.get("name") == "Main":
            s = d.find("schematic")
            for child in list(s):
                if child.tag in ("User", "Wire"):
                    s.remove(child)
    defs = out_root.find("definitions")
    defs.append(shell)
    OUT.write_text(ET.tostring(out_root, encoding="unicode"), encoding="utf-8")

    XDIR.mkdir(parents=True, exist_ok=True)
    (XDIR / f"{DEF_NAME}.xml").write_text(ET.tostring(shell, encoding="unicode"),
                                          encoding="utf-8")
    print("written:", OUT)
    print("written:", XDIR / f"{DEF_NAME}.xml")
    print("group users kept:", kept_users, " wires kept:", kept_wires)
    print("parameter fields bound:", bound)
    print("parameters:", [p[0] for p in PARAMS])


if __name__ == "__main__":
    main()
