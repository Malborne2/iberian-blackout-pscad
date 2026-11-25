"""Add/patch a parameter on every RES_Plant instance of an unloaded .pscx (P12).

usage: python stage3\\set_instance_param.py --pscx C:\\PSCAD_work\\ib4hv.pscx --name RampLim --value 1000000 [--show]
"""
import argparse
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--value", required=True)
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    n = 0
    for c in main.find("schematic"):
        if c.tag != "User" or not (c.get("defn") or "").endswith(":RES_Plant"):
            continue
        pl = c.find("paramlist")
        hit = [p for p in pl.findall("param") if p.get("name") == a.name]
        if hit:
            if a.show:
                print(f"  {c.get('id')}: {a.name} = {hit[0].get('value')}")
            else:
                hit[0].set("value", a.value)
        else:
            if a.show:
                print(f"  {c.get('id')}: {a.name} MISSING")
            else:
                ET.SubElement(pl, "param", {"name": a.name, "value": a.value})
        n += 1
    print(f"  {n} RES_Plant instances")
    if not a.show:
        tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
        print(f"written: {a.pscx}  {a.name} = {a.value}")


if __name__ == "__main__":
    main()
