r"""Place library components in a scratch copy of the lt6 template and print their ports and parameters (skill P2).

usage: python iberia_eq\pscad\probe_ports.py master:datatap [master:other ...] [--orient 0]
Works in C:\PSCAD_work\probe\probe.pscx (overwritten each time); runs its own PSCAD instance.
"""
import os, sys
import mhi.pscad

names = [a for a in sys.argv[1:] if not a.startswith("--")]
orient = int(sys.argv[sys.argv.index("--orient") + 1]) if "--orient" in sys.argv else 0
W = r"C:\PSCAD_work\probe"; os.makedirs(W, exist_ok=True)
t = open(r"C:\PSCAD_work\lt6\lt6_template.pscx", encoding="utf-8").read().replace("lt6:", "probe:").replace('name="lt6"', 'name="probe"')
open(os.path.join(W, "probe.pscx"), "w", encoding="utf-8").write(t)
pscad = mhi.pscad.launch(minimize=False, splash=False, timeout=60)   # visible (owner request, S30)
try:
    if not pscad.licensed():
        c = pscad.get_available_certificates(); c = next(iter(c.values())) if isinstance(c, dict) else c[0]; pscad.get_certificate(c)
    pscad.load(os.path.join(W, "probe.pscx")); cv = pscad.project("probe").canvas("Main")
    for k, n in enumerate(names):
        lib, nm = n.split(":")
        c = cv.add_component(lib, nm, 20, 20 + 10 * k, orient)
        print(n, "at", (20, 20 + 10 * k), "orient", orient, "ports", {p: (v.x, v.y, getattr(v, "dim", "?"), getattr(v, "mode", "?")) for p, v in c.ports().items()})
        print("   params", c.parameters())
finally:
    pscad.quit()
