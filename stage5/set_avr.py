"""Set a parameter on every SyncUnit instance of an unloaded .pscx (rule B1, skill P12).

usage:
  python stage5\\set_avr.py --pscx C:\\PSCAD_work\\ib4hv.pscx --set KA 80
  python stage5\\set_avr.py --pscx C:\\PSCAD_work\\ib4hv.pscx --set KA 80 --only 1 4
  python stage5\\set_avr.py --pscx C:\\PSCAD_work\\ib4hv.pscx --show

--only takes document-order instance numbers (1..5) if a per-unit change is wanted.
"""
import argparse
import xml.etree.ElementTree as ET


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
    ap.add_argument("--set", nargs=2, action="append", default=[], metavar=("PARAM", "VALUE"))
    ap.add_argument("--only", nargs="+", type=int, default=None)
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")

    n = 0
    for c in sch:
        if c.tag == "User" and (c.get("defn") or "").endswith(":SyncUnit"):
            n += 1
            if a.only and n not in a.only:
                continue
            for name, val in a.set:
                set_param(c, name, val)

    if a.show or not a.set:
        for c in sch:
            if c.tag == "User" and (c.get("defn") or "").endswith(":SyncUnit"):
                p = params(c)
                print(f"  SyncUnit {c.get('id')} Sbase {p.get('Sbase')}: "
                      f"KA {p.get('KA')} KF {p.get('KF')} TF {p.get('TF')} V0 {p.get('V0')} "
                      f"Kgov {p.get('Kgov')}")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} ({n} SyncUnit instances)")


if __name__ == "__main__":
    main()
