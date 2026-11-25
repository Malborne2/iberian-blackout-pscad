"""Reorder every RES_Plant instance's paramlist to the definition's parameter order.

Measured cause (RUNLOG S21 41-43): blocks 2 and 3 trip with their own Vt2/Tt2, Vt3/Tt3 while block 1
never trips, i.e. Vt/Tt are delivered to the wrong slots. The instance paramlists carry
`... Cf, Kmod, Kpf, CarrPh, Vt, Tt, Rf, Imax ...` while the definition (and the generated .f) is
`... Cf, Rf, Kmod, Kpf, CarrPh, Vt, Tt, Imax ...`. Aligning the order fixes the binding.

usage: python stage3\\fix_param_order.py --pscx C:\\PSCAD_work\\ib4hv.pscx [--show]
Project must be UNLOADED (rule P12).
"""
import argparse
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    defs = root.find("definitions")
    d = [x for x in defs if x.get("name") == "RES_Plant"][0]
    order = [p.get("name") for p in d.find("form").iter("parameter")]
    print(f"  definition order ({len(order)}): {order}")

    main = [x for x in defs if x.get("name") == "Main"][0]
    n = 0
    for c in main.find("schematic"):
        if c.tag != "User" or not (c.get("defn") or "").endswith(":RES_Plant"):
            continue
        pl = c.find("paramlist")
        params = {p.get("name"): p for p in pl.findall("param")}
        before = [p.get("name") for p in pl.findall("param")]
        wanted = [k for k in order if k in params] + [k for k in before if k not in order]
        if before == wanted:
            n += 1
            continue
        for p in list(pl):
            pl.remove(p)
        for k in wanted:
            pl.append(params[k])
        n += 1
        if a.show:
            print(f"  {c.get('id')}: {before} -> {wanted}")
    print(f"  {n} RES_Plant instances reordered")
    if not a.show:
        tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
        print(f"written: {a.pscx}")


if __name__ == "__main__":
    main()
