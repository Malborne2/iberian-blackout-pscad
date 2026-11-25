"""Expose the AVR voltage reference of the `SyncUnit` definition as a parameter (Session 19b, WP5 step 1).

Why: the exciter (`excac_2016_2`, AC1C) has `OVR = 1`, i.e. it *outputs* the internally computed initial
Vref on its pin at (21,11); PSCAD's own `sync_exciter_governor` pattern samples that once and feeds it back
into the exciter's VREF input (pin (23,11)) through a `sandh`, so the machine starts at exactly its load-flow
operating point.  D19-9 measured that this reference is **not** reachable from outside the module: there was
no parameter and no import on that path, so the four Iberian units' and France's Q set-point could not be
moved at all, which is what the collapsed collector-bus voltage (0.39-0.54 pu) needs.

What this adds (one published Real parameter, one block, no rewiring of anything else):

    sandh.yhold (22,6) --[ wire removed ]            (old: sandh -> exciter VREF)
    sandh.yhold (22,6) -> gain(G = VrefK) at (28,6) -> (30,6) -> (30,8) -> (30,11) -> (23,11)
                                                       |
                                                    datalabel VREF -> pgb VREF   (channel, 0 nodes)

  VrefK = AVR voltage-reference scale, 1.0 = the machine's load-flow operating point (default, so every
  existing instance is unchanged to the digit: multiplication by 1.0).  The absolute reference a unit sees is
  VrefK * V0, where V0 is that instance's initial terminal voltage parameter.

  A *scale* rather than an absolute value is deliberate: a patcher cannot know each instance's V0 when it
  writes the definition, and the default must reproduce the proven G2b/G2c state exactly.

Projects must NOT be loaded in PSCAD while this runs (skill P12).  Refuses to patch twice.

usage:  python stage2\\add_vref.py --pscx C:\\PSCAD_work\\su2.pscx [--pscx ...] [--dry]
"""
from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

G = 18
PARAM = ("VrefK", "AVR voltage-reference scale (1.0 = load-flow point)", "", "1.0")

# the old sandh -> exciter-VREF wire, as measured on the live definition (skill P12: coordinates in grid units,
# the file stores them x18)
OLD_WIRE = [(22, 6), (23, 6), (23, 11)]
NEW_WIRES = [
    [(22, 6), (26, 6)],                       # sandh.yhold -> gain input
    [(30, 6), (30, 8)],                       # gain output -> VREF tap
    [(30, 8), (30, 11), (23, 11)],            # VREF tap -> exciter VREF input
]
GAIN_AT = (28, 6)
LABEL_VREF_AT = (30, 8)
CH_LABEL_AT = (40, 62)                        # free area: the governor chain ends at y = 59
CH_PGB_AT = (44, 62)
IMPORT_AT = (62, 43)                          # after Kgov..TF at (62,31)..(62,41)

PARAM_XML = ('<parameter desc="{d}" name="{n}" group="" unit="{u}" min="-1e+308" max="+1e+308" '
             'content_type="Constant" type="Real" helpmode="Append" intent="Input" dim="1" '
             'animate="false"><value>{v}</value><cond /><help /><vis /></parameter>')
_id = [1_380_000_000]


def nid() -> str:
    _id[0] += 1
    return str(_id[0])


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


def wire_pts(w):
    x0, y0 = int(w.get("x")), int(w.get("y"))
    return [((x0 + int(v.get("x"))) // G, (y0 + int(v.get("y"))) // G) for v in w.findall("vertex")]


def patch(defn: ET.Element) -> ET.Element:
    d = copy.deepcopy(defn)
    cat = d.find("form").find("category")
    if any(p.get("name") == "VrefK" for p in cat.findall("parameter")):
        raise SystemExit("SyncUnit already has VrefK -- refusing to patch twice")
    sch = d.find("schematic")
    tmpl = {}
    for u in sch.findall("User"):
        tmpl.setdefault(u.get("defn"), u)
    old = [w for w in sch.findall("Wire") if wire_pts(w) == OLD_WIRE]
    if len(old) != 1:
        raise SystemExit(f"expected exactly 1 sandh->VREF wire, found {len(old)}")
    sch.remove(old[0])

    cat.append(ET.fromstring(PARAM_XML.format(n=PARAM[0], d=PARAM[1], u=PARAM[2], v=PARAM[3])))

    gain = copy.deepcopy(tmpl["master:gain"])
    gain.set("id", nid())
    gain.set("x", str(GAIN_AT[0] * G)); gain.set("y", str(GAIN_AT[1] * G))
    for p in gain.find("paramlist").findall("param"):
        if p.get("name") == "G":
            p.set("value", PARAM[0])
    sch.append(gain)

    for pts in NEW_WIRES:
        sch.append(wire(pts))

    label_t = tmpl["master:datalabel"]
    pgb_t = tmpl["master:pgb"]
    for at, name in ((LABEL_VREF_AT, "VREF"), (CH_LABEL_AT, "VREF")):
        el = copy.deepcopy(label_t)
        el.set("id", nid()); el.set("x", str(at[0] * G)); el.set("y", str(at[1] * G))
        for p in el.find("paramlist").findall("param"):
            if p.get("name") == "Name":
                p.set("value", name)
        sch.append(el)
    sch.append(wire([CH_LABEL_AT, CH_PGB_AT]))
    pgb = copy.deepcopy(pgb_t)
    pgb.set("id", nid()); pgb.set("x", str(CH_PGB_AT[0] * G)); pgb.set("y", str(CH_PGB_AT[1] * G))
    for p in pgb.find("paramlist").findall("param"):
        if p.get("name") == "Name":
            p.set("value", "VREF")
        elif p.get("name") in ("Max", "Min"):
            p.set("value", "2.0" if p.get("name") == "Max" else "-2.0")
    sch.append(pgb)

    imp = copy.deepcopy(tmpl["master:import"])
    imp.set("id", nid()); imp.set("x", str(IMPORT_AT[0] * G)); imp.set("y", str(IMPORT_AT[1] * G))
    for p in imp.find("paramlist").findall("param"):
        if p.get("name") == "Name":
            p.set("value", PARAM[0])
    sch.append(imp)
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", action="append", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    for dst in a.pscx:
        root = ET.parse(dst).getroot()
        holder = root.find("definitions")
        old = [d for d in holder if d.get("name") == "SyncUnit"]
        if not old:
            raise SystemExit(f"no SyncUnit definition in {dst}")
        new = patch(old[0])
        new.set("id", old[0].get("id"))      # keep the id: the instances' cached port list stays valid
        if a.dry:
            print("would patch", dst, "params ->", [p.get("name") for p in new.find("form").find("category")])
            continue
        holder.remove(old[0])
        holder.append(new)
        Path(dst).write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
        print("SyncUnit with VrefK written into", dst)


if __name__ == "__main__":
    main()
