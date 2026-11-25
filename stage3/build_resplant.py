"""Generate the `RES_Plant` module definition and a bench project `rp1.pscx` that holds it.

Session 17 (Claude, 2026-11-16). Supersedes the executor's unbuilt `build_resplant1.py`, whose
data ports (`Pref`, `Force`, `Trip`) were `xnode` tags (electrical) and therefore could not work.

The module body is PSCAD's own gate-G3a plant from `C:\\PSCAD_work\\cv1.pscx` (Main canvas),
copied verbatim.  Kept out: the three grid sources + neutral grounds (the grid is outside),
the DC source + 300 uF DC capacitor (the shared rail is outside, PLAN A4), the bench OV-relay
stimulus, the bench P-reference pulse generator, unused VDSET/VQSET leftovers, stray labels.

Kept IN (deviation from PLAN B3 "one C_f per collector bus", decided here): the three C_f
capacitors, bound to parameter `Cf`.  A filter capacitor per plant costs no node (it sits on
the module's AC port node) and scales with each plant's own rating, so a plant tripped by gate
blocking keeps its own filter on the bus exactly as a real plant whose inverters block but
whose main breaker stays closed.

Added (all new logic, coordinates on the 100x100 module canvas, grid units):
  * xnode DCP/DCN on the two rail wire ends (36,31)/(36,35)
  * import Pref at the old pulse-generator spot -> IDREF = Pref (pu of Sbase)
  * gate enable: the six modulator outputs are renamed h1..h6 and multiplied by EN
  * overvoltage relay on VDF (8 ms filtered d-axis voltage = |V| once the PLL is locked):
        VDF - Vt > 0  -> x ARM -> delay(Tt, definite time, resets at once) -> + Force
        -> > 0.5 -> latch (pi_ctlr, GP 0, integrates a 0/1 input, never decreases) -> > 0.5 = TRIP
        EN = ONE - TRIP ;  ARM = delay(ONE, 0.5 s)  (start-up vd spike must not trip the plant)
  * export Trip, pgb TRIP
The three-phase AC port is added afterwards *through the tools* (breakout + node labels),
because its geometry has to be read back (skill P2).

Parameters (all Real, Constant, published by `master:import`):
    Sbase MVA | Kv 1/kV | Ki 1/kA | Lf H | Cf uF | Kmod | Kpf | CarrPh deg | Vt pu | Tt s
Use `plant_params(Sbase, Vbase, pf)` below to compute them for an instance.
"""
from __future__ import annotations

import copy
import math
import xml.etree.ElementTree as ET
from pathlib import Path

CV1 = Path(r"C:\PSCAD_work\cv1.pscx")
TPL = Path(r"C:\PSCAD_work\iberia3.pscx")      # SyncUnit definition = definition skeleton
OUT = Path(r"C:\PSCAD_work\rp1.pscx")
XDIR = Path(__file__).resolve().parent / "shells"
G = 18
DEF_NAME, DEF_ID = "RES_Plant", "1300000501"
VDC = 800.0                                    # shared rail, kV (PLAN B3)


def plant_params(sbase: float, vbase: float = 400.0, pf: float = 0.985,
                 vt: float = 1.10, tt: float = 0.001, carr_ph: float = 0.0,
                 lf_pu: float = 0.15, cf_ref_uF: float = 0.35, sref: float = 300.0,
                 rf_pu: float = 0.02) -> dict:
    """Instance parameter values. C_f scales with rating from the proven 0.35 uF @ 300 MVA.
    Rf is PLAN_OLD B3's "small damping resistor still to be sized", in series with C_f, in pu of
    the plant's own Zbase; 0.02 pu keeps the 350 Hz notch while damping the Lf-Cf resonance."""
    vpk = vbase * math.sqrt(2.0 / 3.0)
    ipk = math.sqrt(2.0) * sbase / (math.sqrt(3.0) * vbase)
    zb = vbase ** 2 / sbase
    return {
        "Sbase": sbase, "Kv": 1.0 / vpk, "Ki": 1.0 / ipk,
        "Lf": lf_pu * zb / (2 * math.pi * 50.0), "Cf": cf_ref_uF * sbase / sref,
        "Rf": rf_pu * zb,
        "Kmod": -vpk / (VDC / 2.0),
        # iq > 0 is reactive INJECTION (measured S17: grid source absorbs Q when iq > 0), so a
        # plant that absorbs Q at fixed PF (PLAN A1/B3) needs Kpf < 0.
        "Kpf": -math.tan(math.acos(pf)),
        "CarrPh": carr_ph, "Vt1": vt, "Tt1": tt,
        # WP6 item 1 (Session 19): hard limit on id_ref, pu of the plant's own Sbase.
        "Imax": 1.1,
        # WP6 item 2 (Session 21): rate limit on the power reference, pu/s.  1e6 = bypass, so the
        # network instances keep their present dynamics (their Pref already comes from a slow upramp).
        "RampLim": 1e6,
        # WP6 item 3: one block by default (blocks 2/3 parked, shares 2/3 zero) -> identical behaviour.
        "Vt1": 1.1, "Vt2": 1.5, "Tt2": 0.001, "Vt3": 1.5, "Tt3": 0.001,
        "Nsub": 1, "Share1": 1.0, "Share2": 0.0, "Share3": 0.0, "MeasSide": 0,
        "Qmode": 0, "Vset": 1.0,
    }


PARAMS = [  # name, desc, unit (defaults = the proven 300 MVA bench)
    ("Sbase", "Rated MVA", "MVA"),
    ("Kv", "Voltage pu gain 1/(Vbase*sqrt(2/3))", "1/kV"),
    ("Ki", "Current pu gain sqrt3*Vbase/(sqrt2*Sbase)", "1/kA"),
    ("Lf", "Filter inductance (0.15 pu)", "H"),
    ("Cf", "Filter capacitance per phase", "uF"),
    ("Rf", "Filter damping resistor in series with Cf (pu of Zbase)", "ohm"),
    ("Kmod", "Modulation constant -Vbase_pk/(Vdc/2)", "pu"),
    ("Kpf", "Q/P = tan(acos(pf))", "pu"),
    ("CarrPh", "Carrier phase offset", "deg"),
    ("Imax", "Hard limit on id_ref (pu of Sbase)", "pu"),
    ("RampLim", "Rate limit on Pref (pu/s; 1e6 = bypass)", "pu/s"),
    # ---- WP6 item 3: sub-block staging.  Block 1 uses Vt/Tt (kept for compatibility), blocks 2 and 3
    #      have their own thresholds and are parked at 1.5 pu by default.  Share_k is block k's share of
    #      the plant rating; the delivered P/Q is scaled by sum_k Share_k * (block k untripped).
    ("Vt1", "Overvoltage trip threshold, block 1 (on VDF)", "pu"),
    ("Tt1", "Overvoltage trip delay, block 1", "s"),
    ("Vt2", "Overvoltage trip threshold, block 2 (on VDF)", "pu"),
    ("Tt2", "Overvoltage trip delay, block 2", "s"),
    ("Vt3", "Overvoltage trip threshold, block 3 (on VDF)", "pu"),
    ("Tt3", "Overvoltage trip delay, block 3", "s"),
    ("Nsub", "Number of sub-blocks in use (1-3, informational)", ""),
    ("Share1", "Share of block 1 (pu of plant rating)", "pu"),
    ("Share2", "Share of block 2 (0 = not in use)", "pu"),
    ("Share3", "Share of block 3 (0 = not in use)", "pu"),
    # WP6 item 4: relay measurement side.  0 = module-internal |V| (VDF); 1 = POI phase-A RMS
    # (pu of Vbase_LN, i.e. ~1/sqrt(2) of VDF for the same bus voltage).
    ("MeasSide", "OV relay measurement: 0 = internal VDF, 1 = POI RMS", ""),
    # WP6 item 5 (design: stage3\design_qmode2.md).  0 = grid-following (PLL + power loop), 2 = grid-forming.
    ("Qmode", "Converter control mode: 0 = grid-following, 2 = grid-forming", ""),
    ("Vset", "Voltage set-point for the Q(V) droop (pu of Vbase)", "pu"),
]

EXCLUDE = {
    566509220, 1730879637, 798985137, 1450047213, 1916018016, 403942788,   # grid sources+gnd
    616798506, 1489860207,                                                 # DC source, DC cap
    520282981, 317322503, 168782114,                                       # VsrcDc meter
    1311829617, 621056949, 265540723, 1159721490, 299328971, 1869347433,   # bench OV relay
    1609245735, 908726511, 1321924807, 2009234536, 410213344, 750956065,
    976900775, 833827770,                                                  # stray IsrcB/C labels
    824396612, 132955250, 35834131, 1115391785, 1482574426, 1994777452,    # VDSET/VQSET
    287323760,                                                             # bench P pulse
}
EXCLUDE_W = {510917522, 1519903495, 1087696430, 8222049, 935248492, 931846009,
             1329553828, 83354760, 355219603}
FIX_WIRE = {954020183: [(13, 45), (13, 47), (28, 47)]}
RENAME = {696349104: "h1", 257215407: "h4", 1446721509: "h3", 1134123493: "h6",
          1926198422: "h5", 1018275995: "h2",
          # the IDREF generator becomes IDREF0, so a hard limiter can sit between it and every
          # consumer of IDREF (WP6 item 1, Session 19)
          1342729048: "IDREF0",
          # the PSET label at the PSET gain output becomes PSET_RAW, so the Pref rate limiter can
          # sit between it and the IDREF chain (WP6 item 2, Session 21)
          159989988: "PSET_RAW",
          # the fixed-PF Q reference becomes IQREF_FF so the Qmode droop selector can own IQREF
          2052997965: "IQREF_FF",
          }
BIND_ID = {
    449091826: ("G", "Kv"), 544532544: ("G", "Kv"), 522463750: ("G", "Kv"),
    1260774915: ("G", "Ki"), 1568943580: ("G", "Ki"), 1820831203: ("G", "Ki"),
    406229768: ("G", "Kmod"), 22338756: ("G", "Kmod"), 211046060: ("G", "Kmod"),
    69787554: ("G", "Kpf"), 1994807559: ("P", "CarrPh"),
}
# master:inductor.L and master:capacitor.C are content_type "Literal" (cannot hold a parameter:
# "Conversion of 'Lf' to a finite number was not resolved", measured 2026-11-16).
# master:rtcbranch has R/L/C of content_type "Constant" and ports at (-1,0)/(+1,0), so it
# replaces them in place, shifted one grid unit along the element's axis.
TO_RTC = {176024523: "L", 1385213037: "L", 829182503: "L",
          2090806476: "C", 1834721816: "C", 588434843: "C"}
RTC_I = {176024523: "ILA", 1385213037: "ILB", 829182503: "ILC",      # branch-current outputs
         2090806476: "ICA", 1834721816: "ICB", 588434843: "ICC"}

_nid = [1_350_000_000]


def nid() -> str:
    _nid[0] += 1
    return str(_nid[0])


def user(defn: str, x: int, y: int, params: dict, orient: int = 0, w: int = 72, h: int = 36):
    el = ET.Element("User", {"classid": "UserCmp", "id": nid(), "name": defn, "defn": defn,
                             "x": str(x * G), "y": str(y * G), "w": str(w), "h": str(h),
                             "z": "10", "orient": str(orient), "link": "-1", "q": "4",
                             "disable": "false"})
    pl = ET.SubElement(el, "paramlist", {"name": "", "link": "-1", "crc": "0"})
    for k, v in params.items():
        ET.SubElement(pl, "param", {"name": k, "value": str(v)})
    return el


def wire(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    el = ET.Element("Wire", {"classid": "WireOrthogonal", "id": nid(), "name": "",
                             "x": str(min(xs) * G), "y": str(min(ys) * G),
                             "w": str((max(xs) - min(xs)) * G + 10),
                             "h": str((max(ys) - min(ys)) * G + 10),
                             "orient": "0", "disable": "false"})
    for x, y in pts:
        ET.SubElement(el, "vertex", {"x": str((x - min(xs)) * G), "y": str((y - min(ys)) * G)})
    return el


def main() -> None:
    src = ET.parse(CV1).getroot()
    main_sch = [d for d in src.iter("Definition") if d.get("name") == "Main"][0].find("schematic")
    users = {int(u.get("id")): u for u in main_sch.findall("User")}

    # templates for block types that have no port data in master.pslx: copy cv1's own XML
    def clone(uid, x, y, **params):
        el = copy.deepcopy(users[uid])
        el.set("id", nid())
        el.set("x", str(x * G))
        el.set("y", str(y * G))
        pl = el.find("paramlist")
        for p in pl.findall("param"):
            if p.get("name") in params:
                p.set("value", str(params.pop(p.get("name"))))
        for k, v in params.items():
            ET.SubElement(pl, "param", {"name": k, "value": str(v)})
        return el

    T_LABEL, T_MULT, T_SUM, T_CMP = 1496205002, 1743874159, 350708649, 1939611475
    T_PI, T_PGB = 1920789180, 1322672703

    def label(name, x, y):
        return clone(T_LABEL, x, y, Name=name)

    def sumj(x, y, **coef):
        c = {k: "0" for k in "ABCDEFG"}
        c.update({k: str(v) for k, v in coef.items()})
        return clone(T_SUM, x, y, **c)

    # ---- definition skeleton from the SyncUnit definition
    shell = copy.deepcopy([d for d in ET.parse(TPL).getroot().iter("Definition")
                           if d.get("name") == "SyncUnit"][0])
    for k, v in {"name": DEF_NAME, "id": DEF_ID, "crc": "0", "date": "0", "instances": "0"}.items():
        shell.set(k, v)
    pl = shell.find("paramlist")
    for p in list(pl):
        pl.remove(p)
    ET.SubElement(pl, "param", {"name": "Description", "value":
                  "Switching converter plant: 2-level IGBT bridge, SRF-PLL, decoupled dq "
                  "current control, fixed PF, OV relay, gate blocking, shared DC rail"})
    form = shell.find("form")
    form.set("name", DEF_NAME)
    cat = form.find("category")
    cat.set("name", "Plant")
    for p in list(cat):
        cat.remove(p)
    defaults = plant_params(300.0)
    for name, desc, unit in PARAMS:
        cat.append(ET.fromstring(
            f'<parameter desc="{desc}" name="{name}" group="" unit="{unit}" min="-1e+308" '
            f'max="+1e+308" content_type="Constant" type="Real" helpmode="Append" '
            f'intent="Input" dim="1" animate="false"><value>{defaults[name]:.10g}</value>'
            f'<cond /><help /><vis /></parameter>'))

    svg = shell.find("svg")
    for c in list(svg):
        svg.remove(c)
    ports = [("AC", 54, -36, "3", "Natural", ""), ("DCP", 54, 0, "1", "Natural", ""),
             ("DCN", 54, 36, "1", "Natural", ""),
             ("Pref", -54, -36, "1", "Transfer", "Input"),
             ("Force", -54, 0, "1", "Transfer", "Input"),
             ("Trip", -54, 36, "1", "Transfer", "Output")]
    for n, x, y, dim, model, mode in ports:
        typ = "NonRemovable" if model == "Natural" else "Real"
        svg.append(ET.fromstring(f'<port model="{model}" name="{n}" x="{x}" y="{y}" dim="{dim}" '
                                 f'mode="{mode or "Electrical"}" type="{typ}">true</port>'))
        x2 = 36 if x > 0 else -36
        svg.append(ET.fromstring(f'<line x1="{x2}" y1="{y}" x2="{x}" y2="{y}" stroke="Black" '
                                 f'stroke-dasharray="none" stroke-width="0.4" port="" />'))
        tx = 30 if x > 0 else -30
        anchor = "End" if x > 0 else "Start"
        svg.append(ET.fromstring(f'<text x="{tx}" y="{y + 4}" stroke="Black" fill="Black" '
                                 f'font-size="Small" text-anchor="{anchor}">{n}</text>'))
    svg.append(ET.fromstring('<rect x="-36" y="-54" width="72" height="108" stroke="Black" '
                             'stroke-dasharray="none" stroke-width="0.4" fill-style="Hollow" '
                             'fill-fg="Black" fill-bg="" port="" />'))
    svg.append(ET.fromstring('<text x="0" y="-60" stroke="Black" fill="Black" font-size="Small" '
                             'text-anchor="Middle">RES_Plant</text>'))

    # ---- <graphics> is what PSCAD reads for the instance's ports (the <svg> is only a cache):
    #      mode 1 = input, 2 = output, 3 = electrical; datatype 3 = Real, 0 = electrical
    gr = shell.find("graphics")
    for c in list(gr):
        if c.tag != "paramlist":
            gr.remove(c)
    gid = [1_360_000_000]

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

    for n, x, y, dim, model, mode in ports:
        gid[0] += 1
        el = ET.SubElement(gr, "Port", {"id": str(gid[0]), "classid": "Port", "x": str(x), "y": str(y)})
        pl_ = ET.SubElement(el, "paramlist")
        m = {"": "3", "Input": "1", "Output": "2"}[mode]
        for k, v in (("name", n), ("internal", "false"), ("cond", "true"), ("mode", m),
                     ("datatype", "0" if mode == "" else "3"), ("electype", "0"), ("dim", dim)):
            ET.SubElement(pl_, "param", {"name": k, "value": v})
        gline(36 if x > 0 else -36, y, x, y)
        gtext(30 if x > 0 else -30, y + 4, n, "2" if x > 0 else "0")
    for a in ((-36, -54, 36, -54), (36, -54, 36, 54), (36, 54, -36, 54), (-36, 54, -36, -54)):
        gline(*a)
    gtext(0, -60, "RES_Plant", "1")

    sch = shell.find("schematic")
    for c in list(sch):
        if c.tag != "paramlist":
            sch.remove(c)
    for p in sch.find("paramlist").findall("param"):
        if p.get("name") == "size":
            p.set("value", "5")

    # ---- copied plant
    n_u = n_w = 0
    for u in main_sch.findall("User"):
        uid = int(u.get("id"))
        if uid in EXCLUDE:
            continue
        if uid in TO_RTC:
            x, y, o = int(u.get("x")) // G, int(u.get("y")) // G, int(u.get("orient"))
            dx, dy = {0: (1, 0), 1: (0, 1)}[o]
            kind = TO_RTC[uid]
            sch.append(user("master:rtcbranch", x + dx, y + dy,
                            {"Name": "", "ER": "1" if kind == "C" else "0",
                             "EL": "0" if kind == "C" else "1",
                             "EC": "1" if kind == "C" else "0",
                             "R": "Rf" if kind == "C" else "1.0",
                             "L": "Lf" if kind == "L" else "0.1",
                             "C": "Cf" if kind == "C" else "5.0", "I": RTC_I[uid]},
                            orient=o))
            n_u += 1
            continue
        u = copy.deepcopy(u)
        upl = u.find("paramlist")
        for p in (upl.findall("param") if upl is not None else []):
            if uid in RENAME and p.get("name") == "Name":
                p.set("value", RENAME[uid])
            if uid in BIND_ID and p.get("name") == BIND_ID[uid][0]:
                p.set("value", BIND_ID[uid][1])
        sch.append(u)
        n_u += 1
    for w in main_sch.findall("Wire"):
        wid = int(w.get("id"))
        if wid in EXCLUDE_W:
            continue
        x0, y0 = int(w.get("x")), int(w.get("y"))
        pts = [((x0 + int(v.get("x"))) // G, (y0 + int(v.get("y"))) // G) for v in w.findall("vertex")]
        if all(60 <= x <= 82 and 63 <= y <= 68 for x, y in pts):      # bench OV-relay wiring
            continue
        sch.append(wire(FIX_WIRE[wid]) if wid in FIX_WIRE else copy.deepcopy(w))
        n_w += 1

    add = sch.append
    # ---- ports on the DC rail ends, P reference
    xn = lambda n, x, y: user("master:xnode", x, y, {"Name": n}, w=20, h=33)
    add(xn("DCP", 36, 31))
    add(xn("DCN", 36, 35))
    add(user("master:import", 18, 4, {"Name": "Pref"}, w=79, h=25))       # port (20,4)

    # ---- gate enable: g_k = h_k * EN
    for k, y in zip(range(1, 7), (4, 8, 12, 16, 20, 24)):
        add(label(f"h{k}", 74, y))
        add(clone(T_MULT, 76, y))
        add(label("EN", 76, y + 2))
        add(label(f"g{k}", 78, y))

    # ---- arming: ARM = ONE delayed 0.5 s
    add(label("ONE", 66, 42))
    add(user("master:delay", 68, 42, {"Name": "", "T": "0.5", "INTR": "0"}))
    add(label("ARM", 70, 42))

    # ---- WP6 item 1: current limit.  IDREF = hardlimit(IDREF0, +Imax / -1.1)
    #      The generator label of IDREF is renamed IDREF0 (RENAME above); every consumer of IDREF
    #      (the dq PI and the Kpf -> IQREF branch) therefore sees the limited value. UL/LL are
    #      content_type "Variable", so UL takes the published parameter Imax; LL cannot hold
    #      "-Imax" (a field cannot take a negative parameter), so it is the literal -1.1.
    #      master:hardlimit ports: I at (-2,0), O at (+2,0); "Limit" stays 0 = internal.
    add(label("IDREF0", 50, 7))
    add(user("master:hardlimit", 52, 7, {"Name": "", "UL": "Imax", "LL": "-1.1", "COM": "", "Dim": "1"}))
    add(label("IDREF_L", 54, 7))

    # ---- WP6 item 2: rate limit on Pref.  PSET_RAW (the gain output at (26,4)) -> ratelimit ->
    #      PSET (consumed by the div at (34,4)).  IR/DR are published as RampLim, so an instance can
    #      set 0.2 pu/s; the network instances keep 1e6 (bypass).  master:ratelimit ports I/O at -2/+2.
    add(user("master:ratelimit", 28, 4, {"Name": "", "IR": "RampLim", "DR": "RampLim",
                                         "COM": "Rate_Limiter", "Dim": "1"}))
    add(label("PSET", 30, 4))

    # ---- WP6 item 3: sub-block staging.
    #      Block 1 is the chain above (Vt/Tt) and its untripped indicator is EN = ONE - TRIP.
    #      Blocks 2 and 3 are built here: compare(VDF > Vtk) -> xARM -> delay(Ttk) -> latch -> TRIPk,
    #      then u_k = ONE - TRIPk.  SHARE = Share1*EN + Share2*u2 + Share3*u3, and the P and Q
    #      references are multiplied by SHARE, so a tripped block removes exactly its share.
    #      (Geometry copied from the proven chains: compare/latch inputs at (x-2,y), delay at (x-2,y),
    #       sumj inputs at (x-2,y) and (x,y+2), everything 2 units in/out.  The module canvas is
    #       800x800 and only the top-left 100x100 was used, so this fits with no node cost.)
    # ---- WP6 item 4: relay measurement side (MeasSide).
    #      VMEAS = VDF + MeasSide * (VPOIRMS - VDF): 0 -> internal |V|, 1 -> POI phase-A RMS.
    #      The parameter is carried as a signal by const 1.0 -> hardlimit(UL = MeasSide, LL = -1)
    #      (clamp(1.0, [-1, MeasSide]) = MeasSide; UL = LL would pass the input through - measured).
    add(user("master:const", 10, 100, {"Name": "", "Value": "1.0"}))
    add(label("MSC", 12, 100))
    add(label("MSC", 14, 100))
    add(user("master:hardlimit", 16, 100, {"Name": "", "UL": "MeasSide", "LL": "-1",
                                           "COM": "", "Dim": "1"}))
    add(label("MS", 18, 100))
    add(label("VA_PU", 22, 100))
    add(user("master:rms-inst", 24, 100, {"Name": "", "Type": "ANALOG", "Ts": "0.02", "Scale": "1",
                                          "freq": "50", "NSAM": "64", "Vinit": "0"}))
    add(label("VPOIRMS", 26, 100))
    add(sumj(32, 100, D=1, F=-1))                                          # VPOIRMS - VDF
    add(label("VPOIRMS", 30, 100))
    add(label("VDF", 32, 102))
    add(label("DV", 34, 100))
    add(clone(T_MULT, 40, 100))                                            # MS * DV
    add(label("MS", 38, 100))
    add(label("DV", 40, 102))
    add(label("DVS", 42, 100))
    add(sumj(48, 100, D=1, F=1))                                           # VDF + DVS
    add(label("VDF", 46, 100))
    add(label("DVS", 48, 102))
    add(label("VMEAS", 50, 100))

    for k, y in ((1, 152), (2, 120), (3, 136)):
        add(label("VMEAS" if k == 1 else "VDF", 12, y))
        add(clone(T_CMP, 14, y, X=f"Vt{k}", OL="0", OH="1"))
        add(clone(T_MULT, 18, y))
        add(label("ARM", 18, y + 2))
        add(user("master:delay", 22, y, {"Name": "", "T": f"Tt{k}", "INTR": "0"}))
        add(clone(T_CMP, 26, y, X="0.5", OL="0", OH="1"))
        add(clone(T_PI, 30, y, GP="0.0", TI="0.001", YHI="10", YLO="0", YINIT="0.0"))
        add(clone(T_CMP, 34, y, X="0.5", OL="0", OH="1"))
        tname = "TRIP" if k == 1 else f"TRIP{k}"
        add(label(tname, 36, y))
        add(label(tname, 32, y + 4))
        add(sumj(34, y + 4, D=-1, F=1))                                    # ONE - TRIPk
        add(label("ONE", 34, y + 6))
        add(label(f"STGU{k}", 36, y + 4))

    # shares: STGk = Share_k * u_k.
    # master:gain cannot carry a published parameter without exposing an IN:Dim port, and
    # master:const is literal-only; master:hardlimit with UL = LL = Share_k turns a literal 1.0 into the
    # parameter value (its UL/LL are "Variable" content type - proven by UL="Imax").
    # Rows 150/158/166 keep clear of the two relay chains (rows 120/136).
    for k, y, u in ((1, 150, "STGU1"), (2, 158, "STGU2"), (3, 166, "STGU3")):
        add(user("master:const", 34, y, {"Name": "", "Value": "1.0"}))
        add(label(f"STG{k}C", 36, y))
        add(label(f"STG{k}C", 38, y))
        add(user("master:hardlimit", 40, y, {"Name": "", "UL": f"Share{k}", "LL": f"Share{k}",
                                            "COM": "", "Dim": "1"}))
        add(label(f"STG{k}H", 42, y))
        add(label(f"STG{k}H", 44, y))
        add(clone(T_MULT, 46, y))
        add(label(u, 46, y + 2))
        add(label(f"STG{k}", 48, y))
    # STGSH = STG1 + STG2 + STG3
    add(sumj(54, 158, D=1, F=1))
    add(label("STG1", 52, 158))
    add(label("STG2", 54, 160))
    add(label("STG12", 56, 158))
    add(sumj(62, 158, D=1, F=1))
    add(label("STG12", 60, 158))
    add(label("STG3", 62, 160))
    add(label("STGSH", 64, 158))
    # (EN = ONE - TRIP is the snapshot's own block further down the page; block 1's latch drives the
    #  label TRIP, so nothing else is needed here.)
    # channel for the staging gate (no node cost): SHARE steps as blocks trip
    add(label("STGSH", 68, 166))
    add(wire([(68, 166), (72, 166)]))
    add(clone(T_PGB, 72, 166, Name="SHARE", Units="", Max="1.5", Min="-0.5"))
    # scale the P and Q references by STGSH
    add(clone(T_MULT, 70, 182))
    add(label("IDREF_L", 68, 182))
    add(label("STGSH", 70, 184))
    add(label("IDREF_PP", 72, 182))


    # ---- Force input port (D21-21: the inherited SyncUnit relay chain is retired; block 1 is
    #      now the third copy of the block-2 chain at row 152.  Force drives the trip output below.)
    add(user("master:import", 74, 30, {"Name": "Force"}, w=79, h=25))      # port (76,30) - the import
    # names the signal "Force" itself; a label on the same pin would be a second source (measured).
    # ---- EN and TRIP (single block; an earlier TRIP1-based copy was removed)
    #      TRIP = TRIP1 OR Force : the exported trip and its channel (Force keeps the FRC instrument working)
    #      EN = ONE - TRIP : this is what the six gate multipliers read.
    add(label("TRIP", 82, 46))
    add(sumj(84, 46, D=-1, F=1))
    add(label("ONE", 84, 48))
    add(label("EN", 86, 46))
    #      export port + channel
    add(user("master:export", 94, 40, {"Name": "Trip"}, w=79, h=25))       # port (96,40)
    add(label("TRIP", 96, 40))
    add(label("TRIP", 24, 68))
    add(wire([(24, 68), (28, 68)]))
    add(clone(T_PGB, 28, 68, Name="TRIP", Units="", Max="1.5", Min="-0.5"))

    # ---- WP6 item 5, stage 2 (stage3\design_qmode2.md): P/Q measurement and the droop integrator.
    #      Not connected to anything yet - the selectors come in stage 4 after the loops are proven.
    #      Rows 200+ are free (the relay chains use 120-166, MeasSide 100).
    add(label("VD", 12, 200))
    add(clone(T_MULT, 14, 200))
    add(label("ID", 14, 202))
    add(label("PD1", 16, 200))
    add(label("VQ", 22, 200))
    add(clone(T_MULT, 24, 200))
    add(label("IQ", 24, 202))
    add(label("PD2", 26, 200))
    add(sumj(32, 200, D=1, F=1))                                            # P = VD*ID + VQ*IQ
    add(label("PD1", 30, 200))
    add(label("PD2", 32, 202))
    add(label("PMEAS", 34, 200))
    add(label("VD", 42, 200))
    add(clone(T_MULT, 44, 200))
    add(label("IQ", 44, 202))
    add(label("QD1", 46, 200))
    add(label("VQ", 52, 200))
    add(clone(T_MULT, 54, 200))
    add(label("ID", 54, 202))
    add(label("QD2", 56, 200))
    add(sumj(62, 200, D=1, F=-1))                                           # Q = VD*IQ - VQ*ID
    add(label("QD1", 60, 200))
    add(label("QD2", 62, 202))
    add(label("QMEAS", 64, 200))
    add(sumj(72, 200, D=1, F=-1))                                           # Pref - PMEAS
    add(label("Pref", 70, 200))
    add(label("PMEAS", 72, 202))
    add(label("DP", 74, 200))
    add(user("master:gain", 80, 200, {"Name": "", "G": "2.0", "Dim": "1"}))     # Kp_gf [rad/s per pu]
    add(label("DP", 78, 200))
    add(label("WDROOP", 82, 200))
    # (the theta_GF integrator is built below, with W0 included and a 2*pi limit)



    # ---- WP6 item 5a: Qmode = 1, Q(V) droop (PLAN.md WP6 table: "Qmode = 1 Q(V) droop, M1,
    #      +/-5 % V step: Q follows the droop within 2 %").
    #      IQDROOP = Kq_q * (Vset - VDF);  IQREF = IQREF_FF + QM1 * (IQDROOP - IQREF_FF) with QM1 = 1
    #      for Qmode >= 1, so Qmode = 0 reproduces the grid-following reference exactly.
    #      Kq_q is a literal gain (the published-parameter carriers are all used up on the import column).
    add(label("Vset", 14, 252))
    add(sumj(16, 252, D=1, F=-1))
    add(label("VDF", 16, 254))
    add(label("DVQ2", 18, 252))
    add(user("master:gain", 24, 252, {"Name": "", "G": "2.0", "Dim": "1"}))     # Kq_q [pu/pu]
    add(label("DVQ2", 22, 252))
    add(label("IQDROOP", 26, 252))
    # QM = Qmode (0..2) via the proven const -> hardlimit carrier, then QM1 = (QM > 0.5)
    add(user("master:const", 10, 262, {"Name": "", "Value": "1.0"}))
    add(label("QMC", 12, 262))
    add(label("QMC", 14, 262))
    add(user("master:hardlimit", 16, 262, {"Name": "", "UL": "Qmode", "LL": "-1", "COM": "", "Dim": "1"}))
    add(label("QM", 18, 262))
    add(label("QM", 22, 262))
    add(clone(T_CMP, 24, 262, X="0.5", OL="0", OH="1"))
    add(label("QM1", 26, 262))
    # selector on IQREF
    add(sumj(36, 252, D=1, F=-1))
    add(label("IQDROOP", 34, 252))
    add(label("IQREF_FF", 36, 254))
    add(label("DIQD", 38, 252))
    add(clone(T_MULT, 44, 252))
    add(label("QM1", 42, 252))
    add(label("DIQD", 44, 254))
    add(label("DIQM", 46, 252))
    add(sumj(52, 252, D=1, F=1))
    add(label("IQREF_FF", 50, 252))
    add(label("DIQM", 52, 254))
    add(label("IQREF_Q1", 54, 252))

    # ---- WP6 item 5b: Qmode = 2, grid-forming v1 (voltage-source control).
    #      Voltage PIs give the GF current references; QM2 = (Qmode > 1.5) selects them, so
    #      Qmode 0/1 keep the grid-following / droop references bit-identically.
    #      The angle droop (synthetic inertia) is still stage 5 of the mini-plan.
    add(label("Vset", 14, 280))
    add(sumj(16, 280, D=1, F=-1))                                          # Vset - VD
    add(label("VD", 16, 282))
    add(label("DVD2", 18, 280))
    add(clone(T_PI, 24, 280, GP="1.0", TI="0.1", YHI="1.1", YLO="-1.1", YINIT="0.0"))
    add(label("DVD3", 22, 280))
    add(label("IDGF", 26, 280))
    add(user("master:const", 6, 292, {"Name": "", "Value": "0.0"}))
    add(label("ZZ", 8, 292))
    add(label("ZZ", 14, 292))
    add(sumj(16, 292, D=1, F=-1))                                          # 0 - VQ
    add(label("VQ", 16, 294))
    add(label("DVQ3", 18, 292))
    add(clone(T_PI, 24, 292, GP="1.0", TI="0.1", YHI="1.1", YLO="-1.1", YINIT="0.0"))
    add(label("DVQ4", 22, 292))
    add(label("IQGF", 26, 292))
    # QM2 = (Qmode > 1.5).  The QM carrier above is clamp(1.0, [-1, Qmode]) = min(1, Qmode), so it can
    # never exceed 1 - a second carrier with input 2.0 is needed to detect Qmode = 2 (measured: the
    # "grid-forming" runs were actually the droop, IQ = 2*(Vset - VDF) matched to 0.001).
    add(user("master:const", 10, 288, {"Name": "", "Value": "2.0"}))
    add(label("Q2C", 12, 288))
    add(label("Q2C", 14, 288))
    add(user("master:hardlimit", 16, 288, {"Name": "", "UL": "Qmode", "LL": "-1", "COM": "", "Dim": "1"}))
    add(label("Q2", 18, 288))
    add(label("Q2", 32, 286))
    add(clone(T_CMP, 34, 286, X="1.5", OL="0", OH="1"))
    add(label("QM2", 36, 286))
    # IDREF selector
    add(sumj(46, 280, D=1, F=-1))
    add(label("IDGF", 44, 280))
    add(label("IDREF_FF", 46, 282))
    add(label("DIF2", 48, 280))
    add(clone(T_MULT, 54, 280))
    add(label("QM2", 52, 280))
    add(label("DIF2", 54, 282))
    add(label("DIF2Q", 56, 280))
    add(sumj(62, 280, D=1, F=1))
    add(label("IDREF_FF", 60, 280))
    add(label("DIF2Q", 62, 282))
    add(label("IDREF", 64, 280))
    # IQREF selector
    add(sumj(46, 292, D=1, F=-1))
    add(label("IQGF", 44, 292))
    add(label("IQREF_Q1", 46, 294))
    add(label("DIQ2", 48, 292))
    add(clone(T_MULT, 54, 292))
    add(label("QM2", 52, 292))
    add(label("DIQ2", 54, 294))
    add(label("DIQ2Q", 56, 292))
    add(sumj(62, 292, D=1, F=1))
    add(label("IQREF_Q1", 60, 292))
    add(label("DIQ2Q", 62, 294))
    add(label("IQREF", 64, 292))

    # ---- WP6 item 5c: grid-forming angle droop (mini-plan stage 5).
    #      omega = W0 + Kp*(Pref - P)  (WDROOP already carries the droop term)
    #      theta_GF = integral(omega), limited to +/-2*pi
    #      THETA = THETA_FF + QM2*(theta_GF - THETA_FF)   (THETA_FF = the PLL angle)
    #    The angle is a *deviation* from the PLL angle (bumpless at t = 0, which the absolute
    #    integrator of the first attempt lacked - it collapsed the bus, S21 60):
    #        theta_dev = integral( Kp*(Pref - P) ), limited to +/-0.5 rad
    #        THETA     = THETA_FF + QM2 * theta_dev
    add(clone(T_PI, 28, 304, GP="0.0", TI="1.0", YHI="0.5", YLO="-0.5", YINIT="0.0"))
    add(label("WDROOP", 26, 304))
    add(label("DTHETA", 30, 304))
    add(clone(T_MULT, 48, 304))
    add(label("QM2", 46, 304))
    add(label("DTHETA", 48, 306))
    add(label("DTHQ", 50, 304))
    add(sumj(56, 304, D=1, F=1))
    add(label("THETA_FF", 54, 304))
    add(label("DTHQ", 56, 306))
    add(label("THETA", 58, 304))

    # ---- WP6 item 5c support: virtual impedance on the grid-forming voltage references.
    #      Vd_ref = Vset - VD - Rv*ID ,  Vq_ref = -VQ - Rv*IQ   (Rv = 0.06 pu of Zbase)
    #      So the reference backs off as the current rises and the PIs stop demanding more current
    #      than the converter can deliver - the failure mode of the first two angle-droop attempts
    #      (runs 64/65: ID and IQ pinned at 1.1, bus collapsed).
    add(label("ID", 8, 316))
    add(user("master:gain", 10, 316, {"Name": "", "G": "0.06", "Dim": "1"}))
    add(label("RD", 12, 316))
    add(sumj(20, 316, D=1, F=-1))
    add(label("DVD2", 18, 316))
    add(label("RD", 20, 318))
    add(label("DVD3", 22, 316))
    add(label("IQ", 8, 320))
    add(user("master:gain", 10, 320, {"Name": "", "G": "0.06", "Dim": "1"}))
    add(label("RQ", 12, 320))
    add(sumj(20, 320, D=1, F=-1))
    add(label("DVQ3", 18, 320))
    add(label("RQ", 20, 322))
    add(label("DVQ4", 22, 320))

    # ---- WP6 item 6: POD (power oscillation damping).  A washout on the plant's own power gives
    #      a zero-steady-state oscillation signal, added to the power reference (active in every mode):
    #        Pdev = PMEAS - lag(PMEAS, T = 0.5 s)
    #        PSET_T = PSET + Kpod*Pdev        (the div now reads PSET_T)
    add(label("PMEAS", 8, 336))
    add(user("master:realpole", 10, 336, {"Name": "", "Limit": "0", "COM": "Real_Pole", "Reset": "0",
                                          "YO": "0.0", "Dim": "1", "G": "1", "T": "0.5",
                                          "Max": "10.0", "Min": "-10.0"}))
    add(label("PLAG", 12, 336))
    add(sumj(18, 336, D=1, F=-1))
    add(label("PMEAS", 16, 336))
    add(label("PLAG", 18, 338))
    add(label("PDEV", 20, 336))
    add(user("master:gain", 26, 336, {"Name": "", "G": "0.5", "Dim": "1"}))          # Kpod
    add(label("PDEV", 24, 336))
    add(label("PODP", 28, 336))
    # POD injection: IDREF_FF = IDREF_PP (grid-following) + PODP (washout term)
    add(sumj(78, 190, D=1, F=1))
    add(label("IDREF_PP", 76, 190))
    add(label("PODP", 78, 192))
    add(label("IDREF_FF", 80, 190))
    # POD is injected on IDREF_FF below (a single-driver point); the power-reference chain is untouched.

    # ---- three-phase AC port: xnode AC -> breakout -> electrical node labels to the 3 POI nodes
    #      (geometry read back with pscad_get_ports on 2026-11-16: breakout at (64,12) has
    #       N (64,12) dim 3, N1 (66,10), N2 (66,12), N3 (66,14))
    add(user("master:xnode", 61, 12, {"Name": "AC"}, w=20, h=33))
    add(wire([(61, 12), (64, 12)]))
    add(user("master:breakout", 64, 12, {"Dis": "0", "Com": "0"}, w=44, h=80))
    nl = lambda n, x, y: user("master:nodelabel", x, y, {"Name": n, "MeasV": "0", "PU": "0",
                                                          "VName": "VNode", "VBase": "1"}, w=20, h=23)
    # The plant's current feedback IsrcA/B/C was the *grid sources'* `Ia` output in cv1; the
    # sources are gone, so three ammeters (N1 (0,0) -> N2 (+2,0), master.pslx) now measure it at
    # the POI, positive from the POI node towards the module terminal (= current into the grid).
    # Session 17 measured: an ammeter at the POI costs 3 nodes per plant (NODES 8 -> 11), which
    # 18 plants cannot afford. The rtcbranch current outputs cost none, and on the same run
    # ammeter(grid->POI) = ILx - ICx to 1 mA in 325 mA. The plant current used by the
    # controller is therefore IsrcX = ICx - ILx  (+ve from the POI towards the grid = export),
    # which keeps Ki > 0 exactly as in cv1 (whose source1 `Ia` had that sign).
    for n, (bx, by), py in (("PA", (66, 10), 12), ("PB", (66, 12), 20), ("PC", (66, 14), 28)):
        add(nl(n, bx, by))
        add(nl(n, 12, py))
    for ph, y in zip("ABC", (58, 64, 70)):
        add(label(f"IC{ph}", 84, y))
        add(sumj(86, y, D=1, F=-1))
        add(label(f"IL{ph}", 86, y + 2))
        add(label(f"Isrc{ph}", 88, y))

    # ---- extra channels: per-unit POI voltage / current of phase A (P, Q reporting)
    for k, nm in enumerate(("VA_PU", "IA_PU", "VDF")):
        y = 56 + 3 * k
        add(label(nm, 72, y))
        add(wire([(72, y), (76, y)]))
        add(clone(T_PGB, 76, y, Name=nm, Units="pu", Max="2", Min="-2"))

    # ---- publish parameters (Vt is already imported above)
    k = 0
    for name, *_ in PARAMS:
        if name == "Vt":
            continue
        k += 1
        add(user("master:import", 88, 6 + 2 * k, {"Name": name}, w=79, h=25))

    import sys
    if "--update" in sys.argv:          # replace only the definition in an existing project
        target = Path(sys.argv[sys.argv.index("--update") + 1])
        troot = ET.parse(target).getroot()
        tdefs = troot.find("definitions")
        for d in list(tdefs):
            if d.get("name") == DEF_NAME:
                shell.set("id", d.get("id"))
                tdefs.remove(d)
        # the fixed-PF Q reference must not own the name IQREF: the Qmode droop selector does.
        # (RENAME keys are template ids and do not match this label, so rename by coordinate.)
        for c in shell.find("schematic"):
            if c.tag != "User" or not (c.get("defn") or "").endswith(":datalabel"):
                continue
            try:
                xy = (int(c.get("x")) // 18, int(c.get("y")) // 18)
            except (TypeError, ValueError):
                continue
            if xy != (50, 4):
                continue
            pl = c.find("paramlist")
            for q in pl.findall("param"):
                if q.get("name") == "Name":
                    print("  IQREF driver renamed to IQREF_FF at", xy)
                    q.set("value", "IQREF_FF")

        tdefs.append(shell)

        # ---- D21-22: a separate grid-forming definition.  A byte copy of RES_Plant for now (no behaviour
        #      change, unused), with its own name/id so the GF loops can be built inside it without the
        #      label contention that blocked grafting them onto RES_Plant.
        for d in list(tdefs):
            if d.get("name") == "RES_GFM":
                tdefs.remove(d)
        gfm = copy.deepcopy(shell)
        gfm.set("name", "RES_GFM")
        gfm.set("id", "1300000701")
        tdefs.append(gfm)

        target.write_text(ET.tostring(troot, encoding="unicode"), encoding="utf-8")
        print("updated definition in", target, "(RES_Plant + RES_GFM copy)")
        return

    # ---- write bench project (Main emptied; instances are placed through the tools)
    out = copy.deepcopy(src)
    out.set("name", "rp1")
    for d in out.iter("Definition"):
        if d.get("name") == "Main":
            s = d.find("schematic")
            for c in list(s):
                if c.tag in ("User", "Wire"):
                    s.remove(c)
    defs = out.find("definitions")
    for d in list(defs):
        if d.get("name", "").startswith("TestShell"):
            defs.remove(d)
    defs.append(shell)
    for call in out.iter("call"):
        call.set("name", call.get("name").replace("cv1:", "rp1:"))
    OUT.write_text(ET.tostring(out, encoding="unicode").replace("cv1:", "rp1:"), encoding="utf-8")
    XDIR.mkdir(parents=True, exist_ok=True)
    (XDIR / f"{DEF_NAME}.xml").write_text(ET.tostring(shell, encoding="unicode"), encoding="utf-8")
    print("written", OUT, "| copied users", n_u, "wires", n_w)
    print("defaults", {k: round(v, 6) for k, v in defaults.items()})


if __name__ == "__main__":
    main()
