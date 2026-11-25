"""Add a droop governor + turbine lag and exposed AVR gains to the `SyncUnit` definition (Session 17, WP1).

Reads the canonical SyncUnit definition from --src (default C:\\PSCAD_work\\iberia4.pscx, the one
that passed G2b and carries the Wspd/THETA channels added in Session 10), patches it, and writes it
into every --dst project (replacing that project's SyncUnit, keeping the dst definition id so the
instances' cached port list stays valid; the port list itself is unchanged: `T` only).
Projects must NOT be loaded in PSCAD while this runs (skill P12).

Governor (decided in PLAN_v0.7 D6 -- PSCAD's hy_gov/hy_tur could not be initialised in S2-S5):

    Wspd [rad/s] -> x 1/314.159 -> (1 - w_pu) -> x Kgov -> realpole(Tgov, limits +-GovLim) -> + Pmec -> tmech
                                                                        (label DPGOV)          (label TMECH)

  Kgov = 1/droop (pu power per pu speed on the unit's own Sbase); Kgov = 0 = no primary response.
  realpole initialises from its t = 0 input (S16 trap 1); at t = 0 the speed is synchronous, so the
  governor starts at exactly 0 and the unit's initialisation (Pmec = P0/Sbase) is untouched.

AVR (`Vctl` in PLAN B4): instead of a 0/1 switch, the three gains that set the AC1C speed are now
parameters bound to the exciter's own `Constant` fields: KA -> KA_1, KF -> KF_1, TF -> TF_1.
Defaults are the proven values (400, 0.03, 1.0), so the baseline is unchanged.

usage: python add_governor.py --dst C:\\PSCAD_work\\su2.pscx [--dst ...] [--src ...]
"""
from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

G = 18
NEW_PARAMS = [  # name, desc, unit, default
    ("Kgov", "Governor gain = 1/droop (0 = none)", "pu/pu", "0.0"),
    ("Tgov", "Governor-turbine time constant", "s", "5.0"),
    ("GovLim", "Governor output limit (+/-)", "pu", "0.3"),
    ("KA", "AVR gain KA (excac AC1C KA_1)", "", "400.0"),
    ("KF", "AVR rate feedback KF (KF_1)", "", "0.03"),
    ("TF", "AVR rate feedback TF (TF_1)", "s", "1.0"),
]
PARAM_XML = ('<parameter desc="{d}" name="{n}" group="" unit="{u}" min="-1e+308" max="+1e+308" '
             'content_type="Constant" type="Real" helpmode="Append" intent="Input" dim="1" '
             'animate="false"><value>{v}</value><cond /><help /><vis /></parameter>')
_id = [1_370_000_000]


def nid():
    _id[0] += 1
    return str(_id[0])


def user(defn, x, y, params, w=72, h=36):
    el = ET.Element("User", {"classid": "UserCmp", "id": nid(), "name": defn, "defn": defn,
                             "x": str(x * G), "y": str(y * G), "w": str(w), "h": str(h), "z": "10",
                             "orient": "0", "link": "-1", "q": "4", "disable": "false"})
    pl = ET.SubElement(el, "paramlist", {"name": "", "link": "-1", "crc": "0"})
    for k, v in params.items():
        ET.SubElement(pl, "param", {"name": k, "value": str(v)})
    return el


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


def patch(defn: ET.Element) -> ET.Element:
    d = copy.deepcopy(defn)
    cat = d.find("form").find("category")
    have = {p.get("name") for p in cat.findall("parameter")}
    if "Kgov" in have:
        raise SystemExit("SyncUnit already has a governor (Kgov present) -- refusing to patch twice")
    for n, desc, u, v in NEW_PARAMS:
        cat.append(ET.fromstring(PARAM_XML.format(n=n, d=desc, u=u, v=v)))
    sch = d.find("schematic")
    users = sch.findall("User")
    # templates from the definition itself
    tmpl = {}
    for u in users:
        tmpl.setdefault(u.get("defn"), u)
    label_t = tmpl["master:datalabel"]

    def label(name, x, y):
        el = copy.deepcopy(label_t)
        el.set("id", nid()); el.set("x", str(x * G)); el.set("y", str(y * G))
        for p in el.find("paramlist").findall("param"):
            if p.get("name") == "Name":
                p.set("value", name)
        return el

    # 1. exciter gains -> parameters
    for u in users:
        if u.get("defn") == "master:excac_2016_2":
            for p in u.find("paramlist").findall("param"):
                if p.get("name") in ("KA_1", "KF_1", "TF_1"):
                    p.set("value", p.get("name")[:2])
    # 2. tmech: remove the Pmec -> tmech wire, move the Pmec import to the governor sum
    for w in sch.findall("Wire"):
        if wire_pts(w) == [(18, 28), (23, 28), (23, 25)]:
            sch.remove(w)
            break
    else:
        raise SystemExit("Pmec -> tmech wire not found where expected")
    for u in users:
        if u.get("defn") == "master:import" and any(
                p.get("name") == "Name" and p.get("value") == "Pmec" for p in u.find("paramlist")):
            u.set("x", str(48 * G)); u.set("y", str(52 * G))          # port (50,52)
    add = sch.append
    add(label("TMECH", 23, 25))                                       # machine tmech input
    # 3. governor chain on y = 48 (free area, checked against the dump: nothing below y = 42)
    add(label("Wspd", 34, 48))
    add(user("master:gain", 36, 48, {"G": "0.0031830988618379", "COM": "Gain", "Dim": "1", "DPath": "1"}))
    add(user("master:sumjct", 40, 48, {"DPath": "1", "Dim": "1", "A": "0", "B": "0", "C": "0",
                                       "D": "-1", "E": "0", "F": "1", "G": "0"}))     # 1 - w_pu
    add(user("master:const", 38, 52, {"Value": "1", "Dim": "1"}))                   # out (40,52)
    add(wire([(40, 52), (40, 50)]))
    add(user("master:gain", 44, 48, {"G": "Kgov", "COM": "Gain", "Dim": "1", "DPath": "1"}))
    add(user("master:realpole", 48, 48, {"Limit": "1", "COM": "Real_Pole", "Reset": "0", "YO": "0.0",
                                         "Dim": "1", "G": "1", "T": "Tgov", "Max": "GovLim",
                                         "Min": "-0.3"}))
    add(label("DPGOV", 50, 49))
    add(wire([(50, 48), (50, 49)]))
    add(user("master:sumjct", 52, 48, {"DPath": "1", "Dim": "1", "A": "0", "B": "0", "C": "0",
                                       "D": "1", "E": "0", "F": "1", "G": "0"}))      # + Pmec
    add(wire([(50, 52), (52, 52), (52, 50)]))
    add(label("TMECH", 54, 48))
    # channels
    pgb_t = tmpl["master:pgb"]
    for k, nm in enumerate(("DPGOV", "TMECH")):
        y = 56 + 3 * k
        add(label(nm, 40, y)); add(wire([(40, y), (44, y)]))
        el = copy.deepcopy(pgb_t)
        el.set("id", nid()); el.set("x", str(44 * G)); el.set("y", str(y * G))
        for p in el.find("paramlist").findall("param"):
            if p.get("name") == "Name":
                p.set("value", nm)
            if p.get("name") in ("Max", "Min"):
                p.set("value", "2.0" if p.get("name") == "Max" else "-2.0")
        add(el)
    # 4. publish the new parameters (rule 2 of PLAN F3c)
    imp_t = tmpl["master:import"]
    for k, (n, *_rest) in enumerate(NEW_PARAMS):
        el = copy.deepcopy(imp_t)
        el.set("id", nid()); el.set("x", str(62 * G)); el.set("y", str((31 + 2 * k) * G))
        for p in el.find("paramlist").findall("param"):
            if p.get("name") == "Name":
                p.set("value", n)
        add(el)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=r"C:\PSCAD_work\iberia4.pscx")
    ap.add_argument("--dst", action="append", required=True)
    a = ap.parse_args()
    src = [d for d in ET.parse(a.src).getroot().iter("Definition") if d.get("name") == "SyncUnit"][0]
    new = patch(src)
    for dst in a.dst:
        root = ET.parse(dst).getroot()
        defs = root.find("definitions")
        old = [d for d in defs if d.get("name") == "SyncUnit"]
        nd = copy.deepcopy(new)
        if old:
            nd.set("id", old[0].get("id"))
            defs.remove(old[0])
        defs.append(nd)
        Path(dst).write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
        print("SyncUnit with governor written into", dst)


if __name__ == "__main__":
    main()
