r"""Set parameters on selected module instances of a v2 .pscx (S30 sec 18). Project must not be loaded.

usage: python iberia_eq\pscad\set_unit_params.py --pscx <v2.pscx> --defn SyncUnit --match P0=1045.0 --set Ttrip=112.702 Ptrip=-0.855
       (several --match/--set groups: repeat the whole command)
Selects every instance of v2:<defn> whose parameters equal all --match values (string compare after float formatting),
sets the --set values, prints how many instances changed and fails if none matched.
Parameter-only changes keep the build map, so a snapshot of the same case stays valid (skill P10.4).
"""
import argparse, re

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); ap.add_argument("--defn", required=True)
ap.add_argument("--match", nargs="+", required=True); ap.add_argument("--set", nargs="+", required=True); a = ap.parse_args()
def num(v):
    try: return f"{float(v):.6g}"
    except ValueError: return v
M = {k: num(v) for k, v in (s.split("=", 1) for s in a.match)}; S = dict(s.split("=", 1) for s in a.set)
t = open(a.pscx, encoding="utf-8").read(); n = 0
def edit(m):
    global n
    blk = m.group(0); P = dict(re.findall(r'<param name="(\w+)" value="([^"]*)"', blk))
    if all(num(P.get(k, "")) == v for k, v in M.items()):
        for k, v in S.items():
            blk, c = re.subn(rf'(<param name="{re.escape(k)}" value=")[^"]*(")', rf"\g<1>{v}\g<2>", blk)
            if c == 0: raise SystemExit(f"parameter {k} not found on the matched instance")
        n += 1
    return blk
t = re.sub(rf'<User [^>]*defn="v2:{re.escape(a.defn)}".*?</User>', edit, t, flags=re.S)
if n == 0: raise SystemExit(f"no v2:{a.defn} instance matches {M}")
open(a.pscx, "w", encoding="utf-8").write(t); print(f"{a.defn}: {n} instance(s) matching {M} set {S}")
