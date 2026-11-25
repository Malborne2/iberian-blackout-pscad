"""Set the French-end dispatch on SyncUnit[5] (bus 39): P0 and Pmec each -1,000 MW.

usage: python stage5\set_french_end.py --pscx C:\PSCAD_work\ib4hv.pscx [--drop 1000] [--show]
"""
import argparse
import xml.etree.ElementTree as ET

SB = 200000.0
IID = "1766995819"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--drop", type=float, default=1000.0)
    ap.add_argument("--restore", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    hit = [c for c in main.find("schematic") if c.get("id") == IID]
    if not hit:
        raise SystemExit(f"SyncUnit {IID} not found")
    pl = hit[0].find("paramlist")
    cur = {q.get("name"): q.get("value") for q in pl.findall("param")}
    if a.show:
        print(f"  France SyncUnit {IID}: P0 {cur.get('P0')} Pmec {cur.get('Pmec')}")
    if not a.restore and not a.show:
        d = -a.drop if a.restore else a.drop
        p0 = float(cur["P0"]) - d
        pm = float(cur["Pmec"]) - d / SB
        for q in pl.findall("param"):
            if q.get("name") == "P0":
                print(f"  P0  {q.get('value')} -> {p0:.1f}")
                q.set("value", f"{p0:.1f}")
            if q.get("name") == "Pmec":
                print(f"  Pmec {q.get('value')} -> {pm:.6f}")
                q.set("value", f"{pm:.6f}")
        tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
        print(f"written: {a.pscx}")


if __name__ == "__main__":
    main()
