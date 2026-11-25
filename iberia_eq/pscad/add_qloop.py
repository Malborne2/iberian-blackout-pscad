r"""Patch the SyncUnit definition of a .pscx with v2 change A (RUNLOG S29 sec 11): line-drop compensation + slow outer Q loop.

usage: python iberia_eq\pscad\add_qloop.py --pscx C:\PSCAD_work\<case>.pscx [--pscx ...] [--dry]
The project must NOT be loaded in PSCAD (skill P12). Refuses to patch twice.

What it adds (three published Real parameters, all defaulting to 0 = the old behaviour to the digit):
  XCc  : exciter load-compensation reactance XC (pu, machine base). Negative = regulate a point inside the step-up
         (line-drop compensation; IEEE 421.5: Vc = |Vt + (Rc + jXc) It|). v2: about -0.8 x X_T. Sign to be proven on
         the bench before use.
  Kdrp : outer-loop droop, pu Q per pu V (machine base). Q target = QH - Kdrp * (VIT - VH), where QH/VH are QOUT/VIT
         sampled at rotor release (L2N, t = 5 s) -- the same sample-and-hold pattern as PMH, so no unit conversion.
  Kiq  : integral gain of the outer loop, pu VREF per (pu Q x s). 0 = loop off. The integrator is held in reset until
         t = 5 s and limited to +-0.15 pu of VREF.
Signal chain (all inside the module, free area x 66..92, y 10..52; existing blocks untouched except one wire):
  e   = (QH - QOUT) - Kdrp*(VIT - VH)
  DVR = integral(Kiq * e), reset while t < 5 s
  VREF = sandh(ExInit) + DVR          (replaces the wire sandh.yhold (22,6) -> exciter VREF (23,11))
Channels: DVR, QERR (pgb).
"""
from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

G = 18
PARAMS = [("XCc", "exciter load compensation XC (pu machine base, negative = line-drop compensation)", "0.0"),
          ("Kdrp", "outer Q loop droop (pu Q per pu V)", "0.0"),
          ("Kiq", "outer Q loop integral gain (pu VREF per pu Q s); 0 = off", "0.0")]
OLD_WIRE = [(22, 6), (23, 6), (23, 11)]
PARAM_XML = ('<parameter desc="{d}" name="{n}" group="" unit="" min="-1e+308" max="+1e+308" '
             'content_type="Constant" type="Real" helpmode="Append" intent="Input" dim="1" '
             'animate="false"><value>{v}</value><cond /><help /><vis /></parameter>')
INTEGRAL_XML = ('<User classid="UserCmp" id="0" name="master:integral" x="0" y="0" w="80" h="61" z="-1" orient="0" '
                'defn="master:integral" link="-1" disable="false"><paramlist name="" link="-1" crc="0">'
                '<param name="Name" value="" /><param name="Extrn" value="0" /><param name="Reset" value="1" />'
                '<param name="Mthd" value="0" /><param name="INTR" value="0" /><param name="INTCLR" value="0" />'
                '<param name="Dim" value="1" /><param name="T" value="1.0" /><param name="Yo" value="0.0" />'
                '<param name="YRst" value="0.0" /><param name="YHi" value="0.15" /><param name="YLo" value="-0.15" />'
                '</paramlist></User>')
DATATAP_XML = ('<User classid="UserCmp" name="" defn="master:datatap" id="0" x="0" y="0" w="28" h="26" z="-1" orient="0" '
               'link="-1" disable="false"><paramlist link="-1" name="" crc="0"><param name="Index" value="1" />'
               '<param name="Dim" value="1" /><param name="Type" value="2" /><param name="Style" value="0" />'
               '<param name="Disp" value="1" /><param name="Name" value="" /></paramlist></User>')   # input A at (x-1,y-1), output B at (x,y)
_id = [1_390_000_000]


def nid() -> str:
    _id[0] += 1
    return str(_id[0])


def wire(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    el = ET.Element("Wire", {"classid": "WireOrthogonal", "id": nid(), "name": "",
                             "x": str(min(xs) * G), "y": str(min(ys) * G),
                             "w": str((max(xs) - min(xs)) * G + 10), "h": str((max(ys) - min(ys)) * G + 10),
                             "orient": "0", "disable": "false"})
    for x, y in pts:
        ET.SubElement(el, "vertex", {"x": str((x - min(xs)) * G), "y": str((y - min(ys)) * G)})
    return el


def wire_pts(w):
    x0, y0 = int(w.get("x")), int(w.get("y"))
    return [((x0 + int(v.get("x"))) // G, (y0 + int(v.get("y"))) // G) for v in w.findall("vertex")]


def place(tmpl, at, **pv):
    el = copy.deepcopy(tmpl)
    el.set("id", nid()); el.set("x", str(at[0] * G)); el.set("y", str(at[1] * G))
    for p in el.find("paramlist").findall("param"):
        if p.get("name") in pv:
            p.set("value", str(pv[p.get("name")]))
    return el


def patch(defn: ET.Element) -> ET.Element:
    d = copy.deepcopy(defn)
    cat = d.find("form").find("category")
    if any(p.get("name") == "Kiq" for p in cat.findall("parameter")):
        raise SystemExit("SyncUnit already has the Q loop -- refusing to patch twice")
    sch = d.find("schematic")
    T = {}
    for u in sch.findall("User"):
        T.setdefault(u.get("defn"), u)
    for need in ("master:sumjct", "master:gain", "master:datalabel", "master:sandhdefn", "master:time-sig",
                 "master:compare", "master:import", "master:pgb"):
        if need not in T: raise SystemExit(f"template {need} missing in SyncUnit")
    T["master:integral"] = ET.fromstring(INTEGRAL_XML); T["master:datatap"] = ET.fromstring(DATATAP_XML)
    old = [w for w in sch.findall("Wire") if wire_pts(w) == OLD_WIRE]
    if len(old) != 1: raise SystemExit(f"expected exactly 1 sandh->VREF wire, found {len(old)}")
    sch.remove(old[0])
    # exciter XC -> XCc
    exc = [u for u in sch.findall("User") if u.get("defn") == "master:excac_2016_2"]
    if len(exc) != 1: raise SystemExit("expected one excac_2016_2")
    for p in exc[0].find("paramlist").findall("param"):
        if p.get("name") == "XC": p.set("value", "XCc")
    for n, ds, v in PARAMS:
        cat.append(ET.fromstring(PARAM_XML.format(n=n, d=ds, v=v)))
    add = sch.append
    lab = lambda at, nm: add(place(T["master:datalabel"], at, Name=nm))
    # VREF = sandh + DVR : sumjct S4 at (26,6), D (24,6) + F (26,8) both ADD, out (28,6)
    add(place(T["master:sumjct"], (26, 6), D="1", F="1", A="0", B="0", E="0", G="0"))
    add(wire([(22, 6), (24, 6)])); lab((26, 9), "DVR"); add(wire([(26, 9), (26, 8)]))
    add(wire([(28, 6), (28, 10), (23, 10), (23, 11)]))
    # QH, VH: sample and hold at L2N (pattern of PMH: label at the control pin y+2)
    for y, src, dst in ((12, "QOUT", "QH"), (18, "VIT", "VH")):
        if src == "VIT":                                    # VIT is the exciter's 3-element vector: element 1 = |Vt| (pu)
            lab((66, y - 1), "VIT"); add(place(T["master:datatap"], (67, y))); add(wire([(67, y), (70, y)]))
        else:
            lab((68, y), src); add(wire([(68, y), (70, y)]))
        add(place(T["master:sandhdefn"], (72, y))); lab((72, y + 2), "L2N")
        add(wire([(74, y), (76, y)])); lab((76, y), dst)
    # dV = VIT - VH -> *Kdrp -> KDV
    lab((66, 25), "VIT"); add(place(T["master:datatap"], (67, 26))); add(wire([(67, 26), (70, 26)]))
    add(place(T["master:sumjct"], (72, 26), D="1", F="-1", A="0", B="0", E="0", G="0"))
    lab((72, 29), "VH"); add(wire([(72, 29), (72, 28)]))
    add(wire([(74, 26), (76, 26)])); add(place(T["master:gain"], (78, 26), G="Kdrp"))
    add(wire([(80, 26), (82, 26)])); lab((82, 26), "KDV")
    # E1 = QH - QOUT
    lab((68, 34), "QH"); add(wire([(68, 34), (70, 34)]))
    add(place(T["master:sumjct"], (72, 34), D="1", F="-1", A="0", B="0", E="0", G="0"))
    lab((72, 37), "QOUT"); add(wire([(72, 37), (72, 36)]))
    add(wire([(74, 34), (76, 34)])); lab((76, 34), "QE1")
    # e = QE1 - KDV -> QERR -> *Kiq -> integral (reset while t < 5 s) -> DVR
    lab((68, 42), "QE1"); add(wire([(68, 42), (70, 42)]))
    add(place(T["master:sumjct"], (72, 42), D="1", F="-1", A="0", B="0", E="0", G="0"))
    lab((72, 45), "KDV"); add(wire([(72, 45), (72, 44)]))
    add(wire([(74, 42), (76, 42)])); lab((76, 42), "QERR")
    lab((76, 46), "QERR"); add(wire([(76, 46), (78, 46)]))
    add(place(T["master:gain"], (80, 46), G="Kiq")); add(wire([(82, 46), (84, 46)]))
    add(place(T["master:integral"], (86, 46))); add(wire([(88, 46), (90, 46)])); lab((90, 46), "DVR")
    lab((86, 49), "RQ"); add(wire([(86, 49), (86, 48)]))
    # RQ = 1 while t < 5 s (compare: OL 1 below X, OH 0 above), pattern of the S2M/L2N comparators
    add(place(T["master:time-sig"], (80, 54))); add(place(T["master:compare"], (84, 54), X="5.0", OL="1", OH="0"))
    lab((86, 54), "RQ")
    # channels
    for y, nm in ((60, "DVR"), (63, "QERR")):
        lab((80, y), nm); add(wire([(80, y), (84, y)]))
        add(place(T["master:pgb"], (84, y), Name=nm, Max="2.0", Min="-2.0"))
    # publish the parameters
    for k, (n, _, _) in enumerate(PARAMS):
        add(place(T["master:import"], (62, 43 + 2 * k), Name=n))
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", action="append", required=True); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    for dst in a.pscx:
        root = ET.parse(dst).getroot(); holder = root.find("definitions")
        old = [d for d in holder if d.get("name") == "SyncUnit"]
        if not old: raise SystemExit(f"no SyncUnit definition in {dst}")
        new = patch(old[0]); new.set("id", old[0].get("id"))
        if a.dry:
            print("would patch", dst, "params ->", [p.get("name") for p in new.find("form").find("category")]); continue
        holder.remove(old[0]); holder.append(new)
        Path(dst).write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
        print("SyncUnit with XCc / Kdrp / Kiq written into", dst)


if __name__ == "__main__":
    main()
