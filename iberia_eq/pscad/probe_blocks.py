r"""Print port names/offsets and parameters of the master control blocks used by the replay logic (S30 sec 16).

usage: python iberia_eq\pscad\probe_blocks.py      (uses a throw-away copy of the lt6 template in C:\PSCAD_work\probe)
"""
import os, sys
import mhi.pscad

WORK = r"C:\PSCAD_work\probe"; os.makedirs(WORK, exist_ok=True); PSCX = os.path.join(WORK, "pr.pscx")
t = open(r"C:\PSCAD_work\lt6\lt6_template.pscx", encoding="utf-8").read().replace("lt6:", "pr:").replace('name="lt6"', 'name="pr"')
open(PSCX, "w", encoding="utf-8").write(t)
BLK = ["compare", "integral", "mult", "div", "sumjct", "upramp", "time-sig", "const", "max", "min", "hardlimit", "realpole", "and",
       "trig", "pgb", "datalabel", "delay", "sr_flip_flop", "monostable"]
pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60)
try:
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    pscad.load(PSCX); cv = pscad.project("pr").canvas("Main")
    for k, nm in enumerate(BLK):
        x, y = 10 + 15 * (k % 6), 10 + 12 * (k // 6)
        try:
            c_ = cv.add_component("master", nm, x, y, 0)
        except Exception as e:
            print(f"{nm:12s} NOT FOUND ({e.__class__.__name__})"); continue
        P = c_.ports()
        print(f"{nm:12s} ports", {p: (v.x - x, v.y - y) for p, v in P.items()})
        print(f"{'':12s} params", {k_: v_ for k_, v_ in c_.parameters().items() if k_ not in ("Dim",)})
finally:
    pscad.quit()
