"""WP3 - replace each remaining ideal source with its RES_Plant fleet, one bus at a time.

Bulk structural edit on the .pscx (skill P12: save -> unload -> script -> load -> build).

For one collector bus the script

  1. deletes the bus's ideal `source3`, its `ground`, and the three dead recorder branches
     (`P`/`Q`/`V` datalabel -> wire -> pgb) that would otherwise be "floating input" build errors;
  2. puts a `nodelabel B<bus>` on the source's terminal node, so the plants connect where the
     source was and the bus's `multimeter` keeps measuring the bus->plant current;
  3. places one `iberia4:RES_Plant` instance per plant of the PLAN_OLD B1 table at a slot in a
     verified-empty rectangle, with the labels the module's ports need:
        AC    <- nodelabel B<bus>
        DCP   <- nodelabel RAILP      DCN <- nodelabel RAILN
        Pref  <- datalabel PR<k>      Force <- datalabel FRC
     (the bus-33 group of Session 17 is the template: labels sit ON the ports, no wires);
  4. gives each plant its own `master:upramp` (0.1-0.6 s, Y2 = Pref) fed from a `datalabel TSIG`
     placed on the shared `master:time-sig` output, so no long wires cross the canvas.

Dispatch (PLAN.md WP3): every plant gets Sbase = MW/0.9 rounded up; the cluster/bulk plant of a bus
takes the shortfall so that the bus total equals what its ideal source delivered; one factor
k_bus = target / sum(MW) <= 1.0 scales all Prefs on the bus. Stage 4 sets the real dispatch.

usage:
  python stage3\\place_plants.py --pscx C:\\PSCAD_work\\iberia4.pscx --bus 36 [--dry]
"""
import argparse
import copy
import math
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- plant data (PLAN_OLD B1)

# (name, MW) - the entry whose MW is the string "rest" takes target - sum(the others)
BUSES = {
    36: dict(source="Pg7", target_mw=2465.0, ph="Ph36", fill="CL36",
             plants=[("6a8", 154.0), ("8a", 150.0), ("CL36", 719.0)],
             # 6a8 + 8a named; CL36 = the real 719 MW of sub-blocks, stretched by the bus shortfall
             slots=[(13, 18), (13, 25), (13, 32)],
             phases=[45.0, 135.0, 22.5]),
    34: dict(source="Pg5", target_mw=2299.0, ph="Ph34", fill="CL34",
             plants=[("4a", 582.0), ("4b", 145.0), ("8b-509", 509.0), ("8b-364", 364.0),
                     ("12b-305", 305.0), ("12b-212", 212.4), ("CL34", 1074.3)],
             slots=[(13, 39), (13, 46), (64, 94), (64, 101), (64, 108), (64, 115), (64, 122)],
             phases=[112.5, 67.5, 157.5, 11.25, 101.25, 56.25, 146.25]),
    35: dict(source="Pg6", target_mw=2915.0, ph="Ph35", fill="BULK1",
             plants=[("5a2", 550.0), ("CL35", 116.9), ("BULK1", 0.0)],
             slots=[(79, 94), (79, 101), (79, 108)],
             phases=[33.75, 123.75, 78.75]),
    38: dict(source="Pg9", target_mw=3661.0, ph="Ph38", fill="BULK2",
             plants=[("6b", 530.0), ("12a", 313.0), ("BULK2", 99.2)],
             slots=[(79, 115), (79, 122), (10, 74)],
             phases=[168.75, 5.625, 95.625]),
}

VT_PARKED, TT_PARKED = 1.25, 0.05      # relays parked during Stage 3
BASE_ID = 1700000000


def plant_params(sbase, vbase=400.0, pf=0.985, vt=VT_PARKED, tt=TT_PARKED, carr_ph=0.0, vdc=800.0):
    """Same formulas as stage3\\build_resplant.py (the module is unchanged)."""
    vpk = vbase * math.sqrt(2.0 / 3.0)
    ipk = math.sqrt(2.0) * sbase / (math.sqrt(3.0) * vbase)
    zb = vbase ** 2 / sbase
    return {
        "Sbase": sbase, "Kv": 1.0 / vpk, "Ki": 1.0 / ipk,
        "Lf": 0.15 * zb / (2 * math.pi * 50.0), "Cf": 0.35 * sbase / 300.0,
        "Kmod": -vpk / (vdc / 2.0), "Kpf": -math.tan(math.acos(pf)),
        "CarrPh": carr_ph, "Vt": vt, "Tt": tt,
    }


def params(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


def set_param(e, name, value):
    pl = e.find("paramlist")
    for p in pl.findall("param"):
        if p.get("name") == name:
            p.set("value", str(value))
            return
    ET.SubElement(pl, "param", {"name": name, "value": str(value)})


def ids_in(root):
    out = set()
    for e in root.iter():
        v = e.get("id")
        if v and v.lstrip("-").isdigit():
            out.add(int(v))
    return out


class IdGen:
    def __init__(self, used):
        self.used, self.n = set(used), BASE_ID

    def next(self):
        while self.n in self.used:
            self.n += 1
        v = self.n
        self.used.add(v)
        self.n += 1
        return v


def wire(parent, x18, y18, dx, dy, idg):
    w = ET.Element("Wire", {"classid": "WireOrthogonal", "id": str(idg.next()), "name": "",
                            "x": str(x18), "y": str(y18), "w": str(abs(dx) + 10),
                            "h": str(abs(dy) + 10), "orient": "0", "disable": "false"})
    ET.SubElement(w, "vertex", {"x": "0", "y": "0"})
    ET.SubElement(w, "vertex", {"x": str(dx), "y": str(dy)})
    parent.append(w)
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--bus", type=int, required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--pref-zero", action="store_true",
                    help="diagnostic: add the plants with Pref = 0 (current reference zero)")
    ap.add_argument("--keep-source", action="store_true",
                    help="diagnostic: keep the ideal source and its recorders")
    ap.add_argument("--only", default="",
                    help="diagnostic: place only these plant names (comma separated)")
    a = ap.parse_args()
    bus = BUSES[a.bus]

    root = ET.parse(a.pscx).getroot()
    defs = root.find("definitions")
    main_def = [d for d in defs if d.get("name") == "Main"][0]
    sc = main_def.find("schematic")
    idg = IdGen(ids_in(root))

    # ---- templates (copied from the bus-33 group so the encoding is exactly PSCAD's)
    tpl_plant = next(e for e in sc if e.tag == "User" and e.get("defn") == "iberia4:RES_Plant")
    tpl_ramp = next(e for e in sc if e.tag == "User" and e.get("defn") == "master:upramp")
    tpl_dlab = next(e for e in sc if e.tag == "User" and e.get("defn") == "master:datalabel")
    tpl_nlab = next(e for e in sc if e.tag == "User" and e.get("defn") == "master:nodelabel")
    time_sig = next(e for e in sc if e.tag == "User" and e.get("defn") == "master:time-sig")

    # ---- 1. the source, its ground, its recorders
    src = None
    for e in sc:
        if e.tag == "User" and e.get("defn") == "master:source3" and params(e).get("P") == bus["source"]:
            src = e
            break
    if src is None:
        raise SystemExit(f"no source3 with P={bus['source']} on Main")
    sx, sy = int(src.get("x")), int(src.get("y"))          # 1/18 grid units
    sp = params(src)
    # N (1-ph) is at (0,+2), N3 (3-ph) at (0,-2) for orient 5; find the ground on the same point
    n3 = (sx, sy - 36) if int(src.get("orient")) == 5 else (sx, sy + 36)
    grd = None
    for e in sc:
        if e.tag == "User" and e.get("defn") == "master:ground" and (int(e.get("x")), int(e.get("y"))) in (
                (sx, sy + 36), (sx, sy - 36)):
            grd = e
            break
    print(f"source {bus['source']} at ({sx // 18},{sy // 18}) id={src.get('id')}; "
          f"N3 node ({n3[0] // 18},{n3[1] // 18}); ground id={grd.get('id') if grd is not None else None}")
    if a.keep_source:
        print("  -- keep-source: the ideal source and its recorders stay")

    # dead recorder branches: datalabel -> wire -> pgb, for P, Q and V. The pgb sits *on* the wire
    # (not at its end), so it is found by testing each orthogonal segment.
    def on_seg(px, py, x1, y1, x2, y2):
        if y1 == y2 == py:
            return min(x1, x2) <= px <= max(x1, x2)
        if x1 == x2 == px:
            return min(y1, y2) <= py <= max(y1, y2)
        return False

    dead = []
    for key in ("P", "Q", "V"):
        name = sp.get(key)
        if not name or a.keep_source:
            continue
        for e in list(sc):
            if e.tag == "User" and e.get("defn") == "master:datalabel" and params(e).get("Name") == name:
                dx, dy = int(e.get("x")), int(e.get("y"))
                dead.append(e)
                for w in list(sc):
                    if w.tag != "Wire":
                        continue
                    wx, wy = int(w.get("x")), int(w.get("y"))
                    vs = [(wx + int(v.get("x")), wy + int(v.get("y"))) for v in w.findall("vertex")]
                    if (dx, dy) not in vs:
                        continue
                    dead.append(w)
                    segs = list(zip(vs[:-1], vs[1:])) or [(vs[0], vs[0])]
                    for u in list(sc):
                        if u.tag == "User" and u.get("defn") == "master:pgb":
                            p = (int(u.get("x")), int(u.get("y")))
                            if any(on_seg(p[0], p[1], s[0][0], s[0][1], s[1][0], s[1][1]) for s in segs):
                                dead.append(u)
    seen = set()
    uniq = []
    for e in dead:
        if id(e) not in seen:
            seen.add(id(e))
            uniq.append(e)
    dead = uniq
    for e in dead:
        sc.remove(e)
    print(f"removed {len(dead)} dead recorder elements for {[sp.get(k) for k in ('P', 'Q', 'V')]}")

    # ---- 2. the bus label where the source was
    lab = copy.deepcopy(tpl_nlab)
    lab.set("id", str(idg.next()))
    lab.set("x", str(n3[0]))
    lab.set("y", str(n3[1]))
    set_param(lab, "Name", f"B{a.bus}")
    sc.append(lab)
    if not a.keep_source:
        sc.remove(src)
        if grd is not None:
            sc.remove(grd)

    # ---- 3. a TSIG label on the shared time signal (once)
    if not any(e.tag == "User" and e.get("defn") == "master:datalabel" and params(e).get("Name") == "TSIG"
               for e in sc):
        t = copy.deepcopy(tpl_dlab)
        t.set("id", str(idg.next()))
        t.set("x", str(int(time_sig.get("x")) + 36))     # its OUT port is at +2 grid
        t.set("y", str(int(time_sig.get("y"))))
        set_param(t, "Name", "TSIG")
        sc.append(t)
        print("placed TSIG label on the time-sig output")

    # ---- 4. the plants
    mws = {n: mw for n, mw in bus["plants"]}
    target = bus["target_mw"]
    fill = bus["fill"]
    others = sum(m for n, m in mws.items() if n != fill)
    mws[fill] = round(max(mws[fill], target - others), 1)
    total = sum(mws.values())
    k_bus = min(1.0, target / total)
    print(f"bus {a.bus}: target {target:.1f} MW, plant ratings {total:.1f} MW, k_bus {k_bus:.4f}"
          f"  [{fill} = {mws[fill]:.1f} MW]")
    if k_bus > 1.0:
        raise SystemExit("k_bus > 1: add the shortfall to the cluster plant")

    next_pr = 1 + max([int(params(e).get("Name")[2:]) for e in sc
                       if e.tag == "User" and e.get("defn") == "master:datalabel"
                       and (params(e).get("Name") or "").startswith("PR")
                       and params(e).get("Name")[2:].isdigit()] or [0])

    only = [s.strip() for s in a.only.split(",") if s.strip()]
    for i, (name, _) in enumerate(bus["plants"]):
        if only and name not in only:
            continue
        px, py = bus["slots"][i]
        mw = mws[name]
        sbase = float(math.ceil(mw / 0.9))
        pref = 0.0 if a.pref_zero else k_bus * mw / sbase
        ph = bus["phases"][i]
        p = plant_params(sbase, carr_ph=ph)
        print(f"  {name:8} {mw:7.1f} MW  Sbase {sbase:7.0f}  Pref {pref:.4f}  CarrPh {ph:7.3f}  "
              f"at ({px},{py})")

        # instance
        inst = copy.deepcopy(tpl_plant)
        inst.set("id", str(idg.next()))
        inst.set("x", str(px * 18))
        inst.set("y", str(py * 18))
        for k, val in p.items():
            set_param(inst, k, val if k != "Sbase" else f"{val:.1f}")
        sc.append(inst)

        # port labels (identical pattern to the bus-33 group)
        for dxy, kind, nm in (((3, -2), "node", f"B{a.bus}"),
                              ((3, 0), "node", "RAILP"),
                              ((3, 2), "node", "RAILN"),
                              ((-3, -2), "data", f"PR{next_pr}"),
                              ((-3, 0), "data", "FRC")):
            t = copy.deepcopy(tpl_nlab if kind == "node" else tpl_dlab)
            t.set("id", str(idg.next()))
            t.set("x", str((px + dxy[0]) * 18))
            t.set("y", str((py + dxy[1]) * 18))
            set_param(t, "Name", nm)
            sc.append(t)

        # its own ramp, fed from the TSIG label
        ry = py - 4
        r = copy.deepcopy(tpl_ramp)
        r.set("id", str(idg.next()))
        r.set("x", str(px * 18))
        r.set("y", str(ry * 18))
        set_param(r, "Y2", f"{pref:.6f}")
        sc.append(r)
        for dxy, nm in (((-2, 0), "TSIG"), ((2, 0), f"PR{next_pr}")):
            t = copy.deepcopy(tpl_dlab)
            t.set("id", str(idg.next()))
            t.set("x", str((px + dxy[0]) * 18))
            t.set("y", str((ry + dxy[1]) * 18))
            set_param(t, "Name", nm)
            sc.append(t)
        next_pr += 1

    if a.dry:
        print("dry run: file not written")
        return
    with open(a.pscx, "w", encoding="utf-8") as fh:
        fh.write(ET.tostring(root, encoding="unicode"))
    print(f"wrote {a.pscx}: bus {a.bus} = {len(bus['plants'])} plants")


if __name__ == "__main__":
    main()
