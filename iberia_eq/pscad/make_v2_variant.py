r"""Copy a built v2 case into its own folder and change module-instance parameters (S30 sec 9, parallel runs).

usage: python iberia_eq\pscad\make_v2_variant.py --src C:\PSCAD_work\v2 --dst C:\PSCAD_work\v2_kd2 Kdrp=4.0:2.0 [Kiq=0.005:0.01 ...]
  NAME=OLD:NEW  replaces value OLD by NEW in every instance parameter NAME (only instances holding OLD change, so the
                embedded units' Kdrp 0 stays 0); OLD = * matches any value. Prints how many instances changed; fails if none did.
Each variant has its own build folder, so up to 8 can run at once (AGENTS.md sec 2).
"""
import argparse, os, re, shutil

ap = argparse.ArgumentParser(); ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True)
ap.add_argument("sets", nargs="*"); a = ap.parse_args()
os.makedirs(a.dst, exist_ok=True)
t = open(os.path.join(a.src, "v2.pscx"), encoding="utf-8").read()
for s in a.sets:
    name, ov = s.split("="); old, new = ov.split(":")
    pat = re.compile(rf'(<param name="{re.escape(name)}" value=")({"[^\"]*" if old == "*" else re.escape(old)})(" />)')
    t, n = pat.subn(rf"\g<1>{new}\g<3>", t)
    if n == 0: raise SystemExit(f"{name}={old}: no instance found")
    print(f"{name}: {old} -> {new} in {n} instances")
open(os.path.join(a.dst, "v2.pscx"), "w", encoding="utf-8").write(t)
print("written", os.path.join(a.dst, "v2.pscx"))
