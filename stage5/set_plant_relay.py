"""WP5 parameter edits on an unloaded .pscx (skill P12 order: save -> unload -> this -> load -> build).

Two independent edits, both rule-B1 scripted:

  --vt/--tt V        set the relay of every RES_Plant instance (parked-relay setting, Stage 3/4)
  --tap33 ... V      set the collector-transformer tap const of one bus, by its component id
                     (mapping measured in S20 sec. 7: 33:1931291851, 34:2006720080, 35:705661550,
                      36:506809771, 38:1387559265)
  --show             print the current values and exit

Usage:
  python stage5\\set_plant_relay.py --pscx C:\\PSCAD_work\\ib4hv.pscx --vt 1.5 --tt 0.05
  python stage5\\set_plant_relay.py --pscx C:\\PSCAD_work\\ib4hv.pscx --tap 38 1.16 --tap 34 0.912
"""
import argparse
import xml.etree.ElementTree as ET

TAPS = {"33": 1931291851, "34": 2006720080, "35": 705661550,
        "36": 506809771, "38": 1387559265}


def params(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


def set_param(e, name, value):
    pl = e.find("paramlist")
    for p in pl.findall("param"):
        if p.get("name") == name:
            p.set("value", str(value))
            return True
    ET.SubElement(pl, "param", {"name": name, "value": str(value)})
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--vt", type=float)
    ap.add_argument("--tt", type=float)
    ap.add_argument("--tap", nargs=2, action="append", default=[], metavar=("BUS", "VALUE"))
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")

    n = 0
    for c in sch:
        if c.tag == "User" and (c.get("defn") or "").endswith(":RES_Plant"):
            n += 1
            if a.vt is not None:
                set_param(c, "Vt", a.vt)
            if a.tt is not None:
                set_param(c, "Tt", a.tt)
    print(f"RES_Plant instances: {n}")

    for bus, val in a.tap:
        cid = TAPS[bus]
        hit = [c for c in sch if c.get("id") == str(cid)][0]
        old = params(hit).get("Value")
        set_param(hit, "Value", val)
        print(f"tap bus {bus}: const {cid} {old} -> {val}")

    if a.show:
        for c in sch:
            if c.tag == "User" and (c.get("defn") or "").endswith(":RES_Plant"):
                p = params(c)
                print(f"  plant {c.get('id')}: Vt {p.get('Vt')} Tt {p.get('Tt')}")
        for bus, cid in TAPS.items():
            hit = [c for c in sch if c.get("id") == str(cid)]
            if hit:
                pp = params(hit[0])
                print(f"  tap bus {bus}: {pp.get('Const', pp.get('Value'))}")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx}")

if __name__ == "__main__":
    main()
