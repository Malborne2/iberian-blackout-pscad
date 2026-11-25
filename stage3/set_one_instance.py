"""Patch parameters on ONE component instance of an unloaded .pscx (P12).

usage: python stage3\\set_one_instance.py --pscx F --iid 1700000140 --param Share1=0.3333 --param Vt=1.02
"""
import argparse
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--iid", required=True)
    ap.add_argument("--param", action="append", default=[])
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    defs = root.find("definitions")
    hit = None
    for d in defs:
        for c in d.findall("schematic"):
            for u in c.findall("User"):
                if u.get("id") == a.iid:
                    hit = u
                    break
    if hit is None:
        raise SystemExit(f"component {a.iid} not found")
    pl = hit.find("paramlist")
    cur = {p.get("name"): p.get("value") for p in pl.findall("param")}
    if a.show:
        for k, v in cur.items():
            print(f"  {k} = {v}")
        return
    for item in a.param:
        name, val = item.split("=", 1)
        found = [p for p in pl.findall("param") if p.get("name") == name]
        if found:
            print(f"  {name}: {found[0].get('value')} -> {val}")
            found[0].set("value", val)
        else:
            print(f"  {name}: (new) {val}")
            ET.SubElement(pl, "param", {"name": name, "value": val})
    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx}")


if __name__ == "__main__":
    main()
