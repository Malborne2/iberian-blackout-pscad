"""Generate the `HVDC_T` definition (PLAN.md WP4): a second module from the same bridge/PLL/current loop.

Why a separate script: `build_resplant.py` builds the *plant* shell; this one re-uses that shell verbatim
(by importing the generator and calling it into a scratch project), then replaces only the outer references:

  P channel   Pref (pu of Sbase, negative = export) -> PSET -> /ONE -> div out
                                                          |
                                            [select] InA <--+   (A = 1, Ctrl = PMODE)
                                                     InB <-- (th9 - th39) -> x Kang -> realpole(Tang)
                                                     Out --> IDREF0 -> hardlimit -> IDREF
              PMODE = 1 -> constant P (InA);  PMODE = 3 -> AC-emulation angle control (InB)
  Q channel   (Vset - VDF) -> pi_ctlr(GP = Kq, TI = Tq, +Qmax / Qmin) -> IQREF
              (the plant's Kpf gain, its IDREF->IQREF link and the IQREF label are removed)
  relay       the plant's OV latch flipped to *under*-voltage: (Vt - VDF) > 0 with Vt = the UV threshold

Measured facts this design rests on (Sessions 17-19, read back from the live model):
  * `master:select`: `Out = InA if Ctrl == A else InB` (its own Fortran), A is Integer/Constant (S19 §34).
  * `master:sumjct`: the left-middle port is input D, the **top** port is input F (proved twice: the plant's
    VDF - Vt relay has VDF at the left with D=1 and Vt at the top with F=-1; the governor's 1-w has D=-1
    at the left and the const 1 at the top with F=1).
  * `pi_ctlr` GP/TI/YHI/YLO are content_type "Variable" -> they take published parameters.
  * the plant's P chain is  Pref import -> gain -> PSET -> div(/ONE) -> IDREF0  (ids 1350000010, 314251196).
  * module ports: AC (+3,-2), DCP (+3,0), DCN (+3,+2), Pref (-3,-2), Force (-3,0), Trip (-3,+2) grid units
    from the instance anchor.  Th9/Th39 are added at (-3,-4) and (-3,+4).

Ports: AC, DCP, DCN (electrical); Pref, Th9, Force, Th39 (data in); Trip (data out).

usage:  python stage3\\build_hvdc.py --dst C:\\PSCAD_work\\iberia4.pscx [--dst ...] [--xml]
        (the project must NOT be loaded in PSCAD -- skill P12)
"""
from __future__ import annotations

import argparse
import copy
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_resplant as br                                    # noqa: E402  (the plant generator)

DEF_NAME, DEF_ID = "HVDC_T", "1300000601"
SCRATCH = Path(r"C:\PSCAD_work\s19b\_hvdc_shell_base.pscx")
G = 18

KEEP = ["Sbase", "Kv", "Ki", "Lf", "Cf", "Rf", "Kmod", "CarrPh", "Vt", "Tt", "Imax"]
EXTRA = [
    ("Pref", "P reference, pu of Sbase (negative = export)", "pu", "0.0"),
    ("PMODE", "1 = constant P, 3 = AC-emulation angle control", "", "1"),
    ("Kang", "AC-emulation gain, pu per degree (negative)", "pu/deg", "0.0"),
    ("Tang", "AC-emulation lag (report: 50 s)", "s", "50.0"),
    ("Vset", "AC voltage set-point for the Q channel", "pu", "1.025"),
    ("Kq", "Q channel PI gain", "pu/pu", "20.0"),
    ("Tq", "Q channel PI time constant", "s", "0.02"),
    ("Qmax", "Q channel upper limit (pu of Sbase)", "pu", "0.4"),
    ("Qmin", "Q channel lower limit (pu of Sbase)", "pu", "-0.6"),
]
PORTS = [("AC", 54, -36, "3", "Natural", ""), ("DCP", 54, 0, "1", "Natural", ""),
         ("DCN", 54, 36, "1", "Natural", ""),
         ("Th9", -54, -36, "1", "Transfer", "Input"),
         ("Force", -54, 0, "1", "Transfer", "Input"),
         ("Trip", -54, 36, "1", "Transfer", "Output"),
         ("Th39", -54, 72, "1", "Transfer", "Input")]

_id = [1_390_000_000]


def nid() -> str:
    _id[0] += 1
    return str(_id[0])


def param_xml(name, desc, unit, value, ptype="Real"):
    lo, hi = ("-1e+308", "+1e+308") if ptype == "Real" else ("-2147483648", "2147483647")
    return (f'<parameter desc="{desc}" name="{name}" group="" unit="{unit}" min="{lo}" max="{hi}" '
            f'content_type="Constant" type="{ptype}" helpmode="Append" intent="Input" dim="1" '
            f'animate="false"><value>{value}</value><cond /><help /><vis /></parameter>')


def hvdc_params(p0_mw=1000.0, sbase=1000.0, vbase=400.0, dc_kv=None, pmode=1,
                k_mw_per_deg=360.0, tang=50.0, vset=1.025, kq=20.0, tq=0.02, qmax=0.4, qmin=-0.6,
                vt=0.90, tt=0.05, carr_ph=0.0):
    """Instance parameters for one HVDC pole (1,000 MW / 1,000 MVA unless overridden).

    `dc_kv` defaults to the plant module's own rail constant (br.VDC = 800 kV); pass it to scale Kmod
    for a different DC voltage.
    """
    p = br.plant_params(sbase, vbase, pf=0.985, vt=vt, tt=tt, carr_ph=carr_ph)
    p.pop("Kpf", None)
    if dc_kv is not None:
        p["Kmod"] = -(vbase * math.sqrt(2.0 / 3.0)) / (dc_kv / 2.0)
    p.update({
        "Pref": -p0_mw / sbase,
        "PMODE": pmode,
        "Kang": -k_mw_per_deg / sbase,      # id_ref = -K * (th9 - th39): negative, pu per degree
        "Tang": tang, "Vset": vset, "Kq": kq, "Tq": tq, "Qmax": qmax, "Qmin": qmin,
    })
    return p


def plant_shell() -> ET.Element:
    """The gate-proven RES_Plant definition, built by the plant generator itself (nothing re-typed)."""
    br.OUT = SCRATCH
    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    br.main()
    root = ET.parse(SCRATCH).getroot()
    return copy.deepcopy([d for d in root.iter("Definition") if d.get("name") == "RES_Plant"][0])


def setp(u, **kv):
    for p in u.find("paramlist").findall("param"):
        if p.get("name") in kv:
            p.set("value", str(kv[p.get("name")]))


def transform(d: ET.Element) -> ET.Element:
    d.set("name", DEF_NAME)
    d.set("id", DEF_ID)
    for k in ("crc", "date", "instances"):
        d.set(k, "0")
    pl = d.find("paramlist")
    for p in list(pl):
        pl.remove(p)
    ET.SubElement(pl, "param", {"name": "Description", "value":
                  "HVDC voltage-source terminal: 2-level bridge, SRF-PLL, dq current control, "
                  "constant-P or AC-emulation P reference, Q(V) channel, UV blocking latch"})
    form = d.find("form")
    form.set("name", DEF_NAME)
    cat = form.find("category")
    cat.set("name", "HVDC")
    for p in list(cat):
        cat.remove(p)
    defaults = hvdc_params()
    plant_desc = {n: (ds, u) for n, ds, u in br.PARAMS}
    for name in KEEP:
        ds, un = plant_desc.get(name, ("", ""))
        cat.append(ET.fromstring(param_xml(name, ds, un, f"{defaults[name]:.10g}")))
    for name, desc, unit, val in EXTRA:
        cat.append(ET.fromstring(param_xml(name, desc, unit, val,
                                           "Integer" if name == "PMODE" else "Real")))

    sch = d.find("schematic")
    # 1. the plant's Kpf branch goes: gain (46,4), the IDREF label feeding it (44,4), the wire
    #    (48,4)-(50,4) and the IQREF label (50,4).  IQREF then has exactly one driver: the Q PI.
    for u in list(sch.findall("User")):
        if u.get("id") in {"69787554", "2097544485", "2052997965", "1342729048"}:
            sch.remove(u)
    # ... and the Kpf *parameter publisher*: build_resplant publishes every plant parameter, Kpf included.
    for u in list(sch.findall("User")):
        if u.get("defn") == "master:import" and any(
                p.get("name") == "Name" and p.get("value") == "Kpf"
                for p in u.find("paramlist").findall("param")):
            sch.remove(u)
    for w in list(sch.findall("Wire")):
        if w.get("id") in {"1349006006", "314251196"}:      # Kpf output wire; div -> IDREF0 label
            sch.remove(w)
    tmpl = {}
    for u in sch.findall("User"):
        tmpl.setdefault(u.get("defn"), u)
    label_t, imp_t = tmpl["master:datalabel"], tmpl["master:import"]

    def label(name, x, y):
        el = copy.deepcopy(label_t)
        el.set("id", nid()); el.set("x", str(x * G)); el.set("y", str(y * G))
        setp(el, Name=name)
        return el

    def imp(name, x, y):
        el = copy.deepcopy(imp_t)
        el.set("id", nid()); el.set("x", str(x * G)); el.set("y", str(y * G))
        setp(el, Name=name)
        return el

    def sumj(x, y, **coef):
        el = copy.deepcopy(tmpl["master:sumjct"])
        el.set("id", nid()); el.set("x", str(x * G)); el.set("y", str(y * G))
        c = {k: "0" for k in "ABCDEFG"}
        c.update({k: str(v) for k, v in coef.items()})
        setp(el, **c)
        return el

    add = sch.append
    # 2. P channel: select at (42,4), in the free stretch of the plant's own y = 4 row.
    #    A = 1, Ctrl = PMODE -> PMODE 1 picks InA (the constant-P reference = Pref/Sbase ... /ONE).
    add(label("IDREF0P", 38, 4))                             # the div's output = constant-P reference
    add(br.user("master:select", 42, 4, {"Name": "", "A": "1", "DPath": "1", "COM": "Selector",
                                         "Dim": "1"}))
    add(br.wire([(36, 4), (38, 4), (38, 2), (40, 2)]))       # div out -> InA (left-lower)
    add(label("IDANG", 40, 4))                               # -> InB (left-middle), by name
    add(br.wire([(44, 4), (46, 4)]))                         # Out -> IDREF0
    add(label("IDREF0", 46, 4))
    add(imp("PMODE", 42, 8))                                 # port (44,8)
    add(br.wire([(44, 8), (42, 8), (42, 6)]))                # -> Ctrl (top)

    # 3.-4. the two outer references live *beyond* the 100x100 module canvas (x >= 102, measured empty;
    #       skill P2: coordinates above 100 work).  They reach the module's nets through label names.
    #       Angle branch, row y = 10:  (Th9 - Th39) -> x Kang -> realpole(Tang) -> IDANG
    add(imp("Th9", 102, 10))                                 # port (104,10)
    add(sumj(110, 10, D=1, F=-1))                            # left = D = Th9, top = F = -Th39
    add(br.wire([(104, 10), (108, 10)]))
    add(imp("Th39", 102, 14))                                # port (104,14)
    add(br.wire([(104, 14), (110, 14), (110, 12)]))
    add(br.user("master:gain", 116, 10, {"G": "Kang", "COM": "Gain", "Dim": "1", "DPath": "1"}))
    add(br.wire([(112, 10), (114, 10)]))
    add(br.user("master:realpole", 122, 10, {"Limit": "0", "COM": "Real_Pole", "Reset": "0",
                                             "YO": "0.0", "Dim": "1", "G": "1", "T": "Tang",
                                             "Max": "10.0", "Min": "-10.0"}))
    add(br.wire([(118, 10), (120, 10)]))
    add(label("IDANG", 124, 10))

    #       Q channel, row y = 18:  (Vset - VDF) -> PI(Kq, Tq, +Qmax/Qmin) -> IQREF
    add(imp("Vset", 102, 18))                                # port (104,18)
    add(sumj(110, 18, D=1, F=-1))
    add(br.wire([(104, 18), (108, 18)]))
    add(label("VDF", 110, 20))                               # the plant's VDF net -> top (F)
    add(br.user("master:pi_ctlr", 116, 18, {"GP": "Kq", "TI": "Tq", "YHI": "Qmax", "YLO": "Qmin",
                                            "YINIT": "0.0", "Mthd": "0", "INTR": "0", "compat": "0",
                                            "Dim": "1"}))
    add(br.wire([(112, 18), (114, 18)]))
    add(label("IQREF", 118, 18))

    # 5. relay: OV -> UV.  The plant's sumjct (VDF - Vt) at (66,34) becomes (Vt - VDF).
    for u in sch.findall("User"):
        if u.get("defn") == "master:sumjct" and int(u.get("x")) // G == 66 and int(u.get("y")) // G == 34:
            setp(u, D="-1", F="1")

    # 5b. constant-power: the plant's own divider (34,4) already computes PSET / <input at (34,6)>.
    #     Feeding it VDF instead of the constant ONE turns `Pref` (a power, pu of Sbase) into a *current*
    #     reference  id = Pref / V  -- which is what "1,000 MW constant power" means (PLAN.md WP4 gate,
    #     and PLAN_OLD A: the report's HVDC is constant power).  With the current reference it was, it
    #     would deliver V x Pref: -1,020 MW at 1.02 pu, -970 MW at 0.97 pu.
    for u in sch.findall("User"):
        if u.get("defn") == "master:datalabel" and int(u.get("x")) // G == 34 and int(u.get("y")) // G == 6:
            setp(u, Name="VDF")

    # 6. publish every parameter that has no import yet (rule 2 of P8)
    have = {p.get("value") for u in sch.findall("User") if u.get("defn") == "master:import"
            for p in u.find("paramlist").findall("param") if p.get("name") == "Name"}
    y = 24
    for name, *_ in EXTRA:
        if name in have:
            continue
        add(imp(name, 102, y))
        y += 2

    # 7. <graphics> is what an instance reads for its ports: rebuild it with the eight ports
    gr = d.find("graphics")
    for c in list(gr):
        if c.tag != "paramlist":
            gr.remove(c)
    gid = [1_395_000_000]

    def gline(x1, y1, x2, y2):
        gid[0] += 1
        el = ET.SubElement(gr, "Gfx", {"classid": "Graphics.Line", "id": str(gid[0]),
                                       "x": str(x1), "y": str(y1)})
        ET.SubElement(el, "vertex", {"x": "0", "y": "0"})
        ET.SubElement(el, "vertex", {"x": str(x2 - x1), "y": str(y2 - y1)})
        pl_ = ET.SubElement(el, "paramlist")
        for k, v in (("color", "Black"), ("dasharray", "0"), ("thickness", "0"), ("port", ""),
                     ("cond", "true"), ("lock", "false")):
            ET.SubElement(pl_, "param", {"name": k, "value": v})

    def gtext(x, y, t, anchor):
        gid[0] += 1
        el = ET.SubElement(gr, "Gfx", {"classid": "Graphics.Text", "id": str(gid[0]),
                                       "x": str(x), "y": str(y)})
        pl_ = ET.SubElement(el, "paramlist")
        for k, v in (("color", "Black"), ("font_size", "0"), ("full_font", "Tahoma, 12world"),
                     ("anchor", anchor), ("cond", "true"), ("text", t), ("lock", "false"),
                     ("angle", "0")):
            ET.SubElement(pl_, "param", {"name": k, "value": v})

    for n, x, y_, dim, model, mode in PORTS:
        gid[0] += 1
        el = ET.SubElement(gr, "Port", {"id": str(gid[0]), "classid": "Port", "x": str(x), "y": str(y_)})
        pl_ = ET.SubElement(el, "paramlist")
        m = {"": "3", "Input": "1", "Output": "2"}[mode]
        for k, v in (("name", n), ("internal", "false"), ("cond", "true"), ("mode", m),
                     ("datatype", "0" if mode == "" else "3"), ("electype", "0"), ("dim", dim)):
            ET.SubElement(pl_, "param", {"name": k, "value": v})
        gline(36 if x > 0 else -36, y_, x, y_)
        gtext(30 if x > 0 else -30, y_ + 4, n, "2" if x > 0 else "0")
    for a in ((-36, -108, 36, -108), (36, -108, 36, 108), (36, 108, -36, 108), (-36, 108, -36, -108)):
        gline(*a)
    gtext(0, -114, "HVDC_T", "1")
    svg = d.find("svg")
    if svg is not None:
        for c in list(svg):
            if c.tag in ("port", "line", "text"):
                svg.remove(c)
        for n, x, y_, dim, model, mode in PORTS:
            typ = "NonRemovable" if model == "Natural" else "Real"
            svg.append(ET.fromstring(f'<port model="{model}" name="{n}" x="{x}" y="{y_}" dim="{dim}" '
                                     f'mode="{mode or "Electrical"}" type="{typ}">true</port>'))
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dst", action="append", required=True)
    ap.add_argument("--xml", action="store_true")
    a = ap.parse_args()
    new = transform(plant_shell())
    for dst in a.dst:
        root = ET.parse(dst).getroot()
        defs = root.find("definitions")
        old = [d for d in defs if d.get("name") == DEF_NAME]
        if old:
            new.set("id", old[0].get("id"))
            defs.remove(old[0])
        defs.append(new)
        Path(dst).write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
        print("HVDC_T written into", dst)
    if a.xml:
        out = HERE / "shells" / f"{DEF_NAME}.xml"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(ET.tostring(new, encoding="unicode"), encoding="utf-8")
        print("shell ->", out)
    print("defaults:", {k: round(v, 6) for k, v in hvdc_params().items()})


if __name__ == "__main__":
    main()
