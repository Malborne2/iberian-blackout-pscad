r"""S26: apply a dispatch trim to the five SyncUnit `Pmec` values (WP7(c)).

`Pmec` is the dispatch trim in pu of the machine's Sbase, ramped in over TREL..TREL+2 s and then a
plain additive term on the turbine power (`TRIM = Pmec*ramp`, `PMT = PMH + TRIM`).  From a snapshot
(t > TREL+2) the ramp is already 1, so a change is a step.

usage:
  python stage12\set_pmec_trim.py --pscx C:\PSCAD_work\s25\ib6.pscx --show
  python stage12\set_pmec_trim.py --pscx ... --mw 30:-12.5,31:-14.1,32:-15.0,37:-13.4,FR:+380 --apply
The project must be UNLOADED when --apply is given (P12).
"""
import argparse, xml.etree.ElementTree as ET

IID = {"30": "993049547", "31": "1404126973", "32": "489869766", "37": "650097263", "FR": "1766995819"}
SB = {"30": 6113.0, "31": 13548.0, "32": 15292.0, "37": 12838.0, "FR": 200000.0}


def load(path):
    r = ET.parse(path)
    root = r.getroot()
    D = {d.get("name"): d for d in root.iter("Definition")}
    S = D["Main"].find("schematic")
    out = {}
    for c in S:
        for b, i in IID.items():
            if c.get("id") == i:
                for q in c.find("paramlist").findall("param"):
                    if q.get("name") == "Pmec":
                        out[b] = (c, q)
    return r, out


ap = argparse.ArgumentParser()
ap.add_argument("--pscx", required=True)
ap.add_argument("--show", action="store_true")
ap.add_argument("--mw", default=None)
ap.add_argument("--apply", action="store_true")
a = ap.parse_args()

tree, M = load(a.pscx)
print("current Pmec [pu of Sbase] (x Sbase = MW of trim):")
for b in IID:
    if b in M:
        v = float(M[b][1].get("value") or 0.0)
        print(f"  {b:>2}: {v:+.6f} pu  x {SB[b]:.0f} = {v*SB[b]:+8.1f} MW")
    else:
        print(f"  {b:>2}: NOT FOUND")

if a.mw:
    print("\napplying:")
    for kv in a.mw.split(","):
        b, mw = kv.split(":")
        c, q = M[b]
        old = float(q.get("value") or 0.0)
        new = old + float(mw) / SB[b]
        q.set("value", f"{new:.6f}")
        print(f"  {b:>2}: {float(mw):+8.1f} MW -> Pmec {old:+.6f} -> {new:+.6f} pu")

if not a.apply:
    print("(dry run; add --apply with the project unloaded)")
    raise SystemExit(0)
tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
print(f"written {a.pscx}")
