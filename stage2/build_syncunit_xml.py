"""Generate the *filled* `SyncUnit` definition XML (machine + AVR + reference chain).

Every component body, parameter set and wire comes from PSCAD's own `sb17.pscx` Main canvas
(the gate-G2a bench), so nothing is re-typed. This script produces a definition that is
correct in one step -- the four findings that each cost a build cycle on 2026-11-16 are
built in:

  1. an `xnode` whose Name is the port name (`T`) inside the canvas  -> else
     "Port 'T' has no matching 'SyncUnit' tag component";
  2. `master:import` for every parameter (PLAN F3c rule 2);
  3. no `const` value bound to a parameter -- `const.Value` is literal: "Conversion of 'V0'
     to a finite number was not resolved".  The AVR reference is instead PSCAD's own
     sample-and-hold chain (VREFO -> sandh -> VREF), as in PSCAD's sync_exciter_governor;
  4. mechanical torque is a *parameter* (`Pmec`, pu) published as a signal and wired straight
     into `tmech` -- a fixed const made every instance deliver the same MW regardless of P0.

Parameters (all `Constant`, all published):
    Sbase  MVA | Vbase kV (LL) | VbaseLN kV (LN = Vbase/sqrt3) | Ibase kA
    H s | P0 MW | Q0 Mvar | V0 pu | Ph0 rad | Vctl 0/1 | Tstart s | Pmec pu

The machine's base set must satisfy 3*VbaseLN*Ibase = Sbase (RUNLOG Session 7b); the two
extra parameters exist only because a field cannot be an expression.

Usage:  python build_syncunit_xml.py [name] [id]
"""
from __future__ import annotations

import copy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SHELL = Path(r"C:\PSCAD_work\iberia3.pscx")   # holds the empty shell (port T, form, symbol)
SB17 = Path(r"C:\PSCAD_work\sb17.pscx")       # holds the proven group
OUT_DIR = Path(__file__).with_name("shells")

# ---- sb17 components to keep (ids verified with probe_sb17_wires.py) -----------------------
USERS = [
    "1280433174",  # sync_machine
    "974437483",   # excac_2016_2
    "1113511637",  # time-sig
    "1953895728",  # upramp -> ExInit
    "1606233046", "1496725110",   # label/pgb EFD0ch
    "2100692511", "1370009762",   # label/pgb VREFO
    "214393605", "533856334",     # label/pgb VIT
    "1599307815", "1082654537",   # label/pgb ExInit
    "1533546260", "333178226",    # label/pgb POUT
    "1542274353", "1315857209",   # label/pgb QOUT
]

# ---- sb17 wires to keep (absolute endpoints from probe_sb17_wires.py) ----------------------
WIRES = [
    ([(22, 24), (22, 26)]),      # exciter VIT <- machine mvit
    ([(22, 25), (28, 25)]),      # VIT tap
    ([(28, 25), (31, 25)]),      # label -> pgb
    ([(16, 26), (16, 24)]),      # exciter EFD0 <- machine efo
    ([(16, 24), (10, 24)]),      # EFD0 -> label
    ([(10, 24), (13, 24)]),      # label -> pgb
    ([(18, 20), (14, 20)]),      # VREFO -> label
    ([(14, 20), (11, 20)]),      # label -> pgb
    ([(18, 50), (24, 50)]),      # upramp -> ExInit label
    ([(24, 50), (27, 50)]),      # label -> pgb
    ([(44, 40), (47, 40)]),      # POUT label -> pgb
    ([(44, 44), (47, 44)]),      # QOUT label -> pgb
]

NS_OFFSET = (2, 0)   # machine `NS` is 2 grid units right of the component origin
XNODE = (25, 21)     # module port T (from the shell)

PARAMS = [
    ("Sbase",   "Rated MVA",                          "MVA",  "300.0",                "Real"),
    ("Vbase",   "Rated line-to-line kV",              "kV",   "18.0",                 "Real"),
    ("VbaseLN", "Rated RMS line-to-neutral kV",       "kV",   "10.392304845413264",   "Real"),
    ("Ibase",   "Rated stator current kA",            "kA",   "9.622504486493764",    "Real"),
    ("H",       "Inertia constant",                   "s",    "3.117",                "Real"),
    ("P0",      "Initial active power",               "MW",   "60.0",                 "Real"),
    ("Q0",      "Initial reactive power",             "Mvar", "2.4",                  "Real"),
    ("V0",      "Initial terminal voltage",           "pu",   "1.0",                  "Real"),
    ("Ph0",     "Initial rotor angle",                "rad",  "0.0",                  "Real"),
    ("Vctl",    "0 = slow AVR (baseline), 1 = fast",  "",     "0",                    "Integer"),
    ("Tstart",  "Exciter release time",               "s",    "0.5",                  "Real"),
    ("Pmec",    "Mechanical torque, pu (= P0/Sbase)", "pu",   "0.2",                  "Real"),
]

PARAM_XML = (
    '    <parameter desc="{desc}" name="{name}" group="" unit="{unit}" min="{min}"'
    ' max="{max}" content_type="Constant" type="{ptype}" helpmode="Append" intent="Input"'
    ' dim="1" animate="false">\n'
    '      <value>{value}</value>\n      <cond />\n      <help />\n      <vis />\n    </parameter>\n'
)

IMPORT_TMPL = (
    '<User classid="UserCmp" id="{id}" name="master:import" x="{x}" y="{y}" w="79" h="25"'
    ' z="10" orient="0" defn="master:import" link="-1" disable="false">'
    '<paramlist name="" link="-1" crc="117509081"><param name="Name" value="{name}" /></paramlist>'
    "</User>"
)

# ---------- new components the shell needs that sb17 does not contain ----------------------
# PSCAD's own sample-and-hold, exactly as sync_exciter_governor places it (4x3 grid symbol).
SANDH = ('<User classid="UserCmp" id="{id}" name="master:sandhdefn" x="{x}" y="{y}" w="72" h="54"'
         ' z="20" orient="0" defn="master:sandhdefn" link="-1" disable="false">'
         '<paramlist name="" link="-1" crc="0"><param name="Iand" value="1" />'
         '<param name="Name" value="" /></paramlist></User>')
LABEL = ('<User classid="UserCmp" id="{id}" name="master:datalabel" x="{x}" y="{y}" w="38" h="25"'
         ' z="30" orient="0" defn="master:datalabel" link="-1" disable="false">'
         '<paramlist name="" link="-1" crc="0"><param name="Name" value="{name}" />'
         '<param name="animate" value="NONE" /><param name="display" value="CURRENT" />'
         '<param name="datatype" value="REAL" /><param name="index" value="1" />'
         '<param name="Unit" value="" /><param name="ivalue1" value="0" />'
         '<param name="rvalue1" value="0" /><param name="rvalue2" value="0" />'
         '<param name="showani" value="0" /></paramlist></User>')


def grid(el, tags=("x", "y")):
    for t in tags:
        el.set(t, str(int(el.get(t))))


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "SyncUnit"
    def_id = sys.argv[2] if len(sys.argv) > 2 else "1200000301"

    root = ET.parse(SHELL).getroot()
    shell = None
    for d in root.iter("Definition"):
        if d.get("name") == "SyncUnit":
            shell = copy.deepcopy(d)
    if shell is None:
        raise SystemExit("shell SyncUnit not found in ibeira3")

    shell.set("name", name)
    shell.set("id", def_id)
    shell.set("crc", "0")
    shell.set("date", "0")
    shell.set("instances", "0")
    form = shell.find("form")
    form.set("name", name)
    cat = form.find("category")
    for p in list(cat):
        cat.remove(p)
    for pname, desc, unit, value, ptype in PARAMS:
        # NB: an Integer parameter whose min/max is a float literal ('-1e+308') makes
        # mhi's FormCodec raise int('-1e+308'); keep integers integer-bounded (measured).
        lo, hi = ("0", "1") if pname == "Vctl" else (
            ("-2147483648", "2147483647") if ptype == "Integer" else ("-1e+308", "+1e+308"))
        cat.append(ET.fromstring(PARAM_XML.format(
            name=pname, desc=desc, unit=unit, value=value, ptype=ptype, min=lo, max=hi)))

    sch = shell.find("schematic")
    for child in list(sch):
        if child.tag != "paramlist":
            sch.remove(child)

    # 1. the port tag
    sch.append(ET.fromstring(
        '<User classid="UserCmp" name="" defn="master:xnode" id="1385483548" x="450" y="378"'
        ' w="20" h="33" z="1" orient="0" link="-1" q="4" disable="false">'
        '<paramlist link="-1" name="" crc="37312176"><param name="Name" value="T" /></paramlist>'
        "</User>"))

    # 2. the group, translated so machine NS lands on the xnode
    sb17 = ET.parse(SB17).getroot()
    main_def = [d for d in sb17.iter("Definition") if d.get("name") == "Main"][0]
    src = main_def.find("schematic")
    users = {u.get("id"): u for u in src.findall("User")}
    mach = users["1280433174"]
    ns = (int(mach.get("x")) // 18 + NS_OFFSET[0], int(mach.get("y")) // 18 + NS_OFFSET[1])
    dx, dy = XNODE[0] - ns[0], XNODE[1] - ns[1]

    BIND = {  # component field -> module parameter (a field may hold a parameter name)
        "1280433174": {"MVA": "Sbase", "VbaseLL": "Vbase", "Vbase": "VbaseLN",
                       "Ibase": "Ibase", "H": "H", "P0": "P0", "Q0": "Q0",
                       "VT": "V0", "Pheta": "Ph0"},
        "1953895728": {"X1": "Tstart"},          # upramp: release at Tstart
    }

    n = 0
    for uid in USERS:
        u = copy.deepcopy(users[uid])
        n += 1
        u.set("id", str(1_310_000_000 + n))
        u.set("x", str(int(u.get("x")) + dx * 18))
        u.set("y", str(int(u.get("y")) + dy * 18))
        pl = u.find("paramlist")
        for p in (pl.findall("param") if pl is not None else []):
            if p.get("name") == "Name" and p.get("value") in ("SyncUnit1",):
                p.set("value", "")
            for field, param in BIND.get(uid, {}).items():
                if p.get("name") == field:
                    p.set("value", param)
        sch.append(u)

    # 3. wires
    n = 0
    for pts in WIRES:
        pts = [(x + dx, y + dy) for x, y in pts]
        n += 1
        sch.append(make_wire(1_320_000_000 + n, pts))

    # 4. the AVR reference chain: VREFO -> sandh.xsampl, sandh.yhold -> VREF, ExInit -> nhold1
    sch.append(ET.fromstring(SANDH.format(id=1_330_000_001, x=20 * 18, y=6 * 18)))
    sch.append(ET.fromstring(LABEL.format(id=1_330_000_002, name="ExInit", x=20 * 18, y=9 * 18)))
    sch.append(make_wire(1_330_000_003, [(21, 11), (21, 10), (16, 10), (16, 6), (18, 6)]))
    sch.append(make_wire(1_330_000_004, [(22, 6), (23, 6), (23, 11)]))
    sch.append(make_wire(1_330_000_005, [(20, 8), (20, 9)]))

    # 5. mechanical torque: the published parameter `Pmec` wired straight into `tmech`
    #    (an `import` port sits 2 grid units right of its placement point: measured)
    sch.append(ET.fromstring(IMPORT_TMPL.format(
        id=1_330_000_006, x=16 * 18, y=28 * 18, name="Pmec")))
    sch.append(make_wire(1_330_000_007, [(18, 28), (23, 28), (23, 25)]))

    # 6. publish every parameter (rule 2 of F3c); Pmec is already published above
    n = 0
    for pname, *_ in PARAMS:
        if pname == "Pmec":
            continue
        n += 1
        sch.append(ET.fromstring(IMPORT_TMPL.format(
            id=1_340_000_000 + n, x=62 * 18, y=(7 + 2 * n) * 18, name=pname)))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{name}.xml"
    out.write_text(ET.tostring(shell, encoding="unicode"), encoding="utf-8")
    print("written:", out)
    print(f"translate ({dx},{dy}) grid")
    print("parameters:", [p[0] for p in PARAMS])
    print("users:", len(USERS) + 2, " wires:", len(WIRES) + 5, " imports:", len(PARAMS) + 1)


def make_wire(wid: int, pts: list[tuple[int, int]]) -> ET.Element:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    el = ET.Element("Wire", {
        "classid": "WireOrthogonal", "id": str(wid), "name": "",
        "x": str(min(xs) * 18), "y": str(min(ys) * 18),
        "w": str((max(xs) - min(xs)) * 18 + 10), "h": str((max(ys) - min(ys)) * 18 + 10),
        "orient": "0", "disable": "false",
    })
    x0, y0 = min(xs), min(ys)
    for x, y in pts:
        ET.SubElement(el, "vertex", {"x": str((x - x0) * 18), "y": str((y - y0) * 18)})
    return el


if __name__ == "__main__":
    main()
