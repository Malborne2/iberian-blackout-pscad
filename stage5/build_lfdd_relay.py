"""Build the six-step LFDD relay on Main as SIGNAL-ONLY blocks (0 nodes) in an UNLOADED .pscx.

Prototypes (compare / delay / pi_ctlr / datalabel / upramp / const / sumj / gain) are cloned from the
RES_Plant definition, where they are proven, into Main.  The relay is driven by a synthetic frequency ramp
(49.5 -> 47.8 Hz over 2 s) so the thresholds can be gated without a network event.

usage: python stage5/build_lfdd_relay.py --pscx C:\\PSCAD_work\\ib4hv.pscx
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350001001]
STEPS = [("1", 49.0), ("2", 48.8), ("3", 48.6), ("4", 48.4), ("5", 48.2), ("6", 48.0)]
T_DELAY = "0.1"          # definite-time delay per step [s]


def nid():
    ID[0] += 1
    return str(ID[0])


def params(el):
    pl = el.find("paramlist")
    return {p.get("name"): p.get("value") for p in pl.findall("param")} if pl is not None else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    defs = root.find("definitions")
    plant = [d for d in defs if d.get("name") == "RES_Plant"][0]
    main_def = [d for d in defs if d.get("name") == "Main"][0]
    psrc = plant.find("schematic")
    dst = main_def.find("schematic")

    WANT = ("master:compare", "master:delay", "master:pi_ctlr", "master:datalabel", "master:time-sig",
            "master:upramp", "master:const", "master:sumjct", "master:gain", "master:pgb")
    proto = {}
    # prefer the plant definition; fall back to what already exists on Main (e.g. the Pref upramps)
    for src_sch in (psrc, dst):
        for c in src_sch:
            if c.tag != "User":
                continue
            d = c.get("defn") or ""
            if d in WANT and d not in proto:
                proto[d] = c
    missing = [k for k in ("master:compare", "master:delay", "master:pi_ctlr", "master:datalabel",
                           "master:upramp", "master:const", "master:sumjct", "master:gain", "master:pgb")
               if k not in proto]
    if missing:
        raise SystemExit(f"prototypes missing: {missing}")

    def place(kind, x, y, **vals):
        el = copy.deepcopy(proto[kind])
        el.set("id", nid())
        el.set("x", str(x * G))
        el.set("y", str(y * G))
        pl = el.find("paramlist")
        for q in pl.findall("param"):
            if q.get("name") in vals:
                q.set("value", str(vals.pop(q.get("name"))))
        for k, v in vals.items():
            ET.SubElement(pl, "param", {"name": k, "value": str(v)})
        dst.append(el)
        return el

    # --- synthetic frequency, arranged to avoid a summing junction -------------------
    #     ramp goes 0 -> -1.7 over 0.5..2.5 s, so f = 49.5 + ramp falls 49.5 -> 47.8 Hz.
    #     "f < threshold" is equivalent to "(-ramp) > 49.5 - threshold", so the compares are
    #     against shifted constants and no sum/offset block is needed.
    # the upramp's input is the TIME signal (the plants feed theirs from master:time-sig);
    # feeding a constant makes it a one-shot, not a ramp - measured in S22 run 76.
    place("master:time-sig", 6, 364, Name="")                    # O at (8,364) = upramp input
    place("master:upramp", 10, 364, Name="", X1="0.5", X2="2.5", Y2="-1.7",
          COM="Up_Ramp_X-fer_Func", Dim="1")
    place("master:datalabel", 12, 364, Name="FRAMP")            # upramp O (10+2)
    place("master:gain", 16, 364, Name="", G="-1", Dim="1")
    place("master:datalabel", 14, 364, Name="FRAMP")            # gain IN (16-2)
    place("master:datalabel", 18, 364, Name="RPOS")             # gain O (16+2)

    for i, (k, th) in enumerate(STEPS):
        y = 368 + 4 * i
        place("master:compare", 26, y, X=f"{49.5 - th:.2f}", OL="0", OH="1")
        place("master:datalabel", 24, y, Name="RPOS")            # compare IN (26-2)
        w = ET.Element("Wire", {"classid": "WireOrthogonal", "name": "", "x": str(28 * G), "y": str(y * G),
                                "w": str(2 * G), "h": "0", "orient": "0", "layer": "", "id": nid(),
                                "disable": "false"})
        ET.SubElement(w, "vertex", {"x": "0", "y": "0"})
        ET.SubElement(w, "vertex", {"x": str(2 * G), "y": "0"})
        dst.append(w)
        place("master:delay", 32, y, Name="", T=T_DELAY, INTR="0")
        place("master:pi_ctlr", 36, y, GP="0.0", TI="0.001", YHI="10", YLO="0", YINIT="0.0",
              Mthd="0", INTR="0", compat="0", Dim="1")
        place("master:datalabel", 38, y, Name=f"S{k}")           # latch O (36+2)
        place("master:pgb", 44, y, Name=f"S{k}", Units="", Max="1.5", Min="-0.5")
        place("master:datalabel", 44, y, Name=f"S{k}")           # pgb input (its own pin)

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - LFDD relay, {len(STEPS)} steps, T = {T_DELAY} s")


if __name__ == "__main__":
    main()
