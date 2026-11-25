"""Set the bench's start-up timing and initial operating point, then measure.

Identifies which timer publishes S2M and which publishes LRR by looking at the
datalabel sitting on each timer's iout port, restores the example's timing
(S2M 0.3 s, LRR 0.4 s), sets the machine's P0/Q0/Pheta, builds, runs 5 s and
prints P, Q, V, speed and mechanical torque in source mode and at the end.

Run: python op_point.py sb11 0.363 [P0] [Q0]
"""
import sys
import time

import pscad_ops as P

PRJ = sys.argv[1]
PHETA = float(sys.argv[2]) if len(sys.argv) > 2 else 0.363
P0 = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
Q0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

P.connect()
objs = P.list_canvas_objects(PRJ)["objects"]


def ports(iid):
    return {p["name"]: p for p in P.get_ports(PRJ, iid)["ports"]}


# --- which timer is which
labels = [(o, ports(o["iid"])["A"]) for o in objs if o["defn_name"] == "master:datalabel"]
for o in objs:
    if o["defn_name"] != "master:timerdefn":
        continue
    iout = ports(o["iid"])["iout"]
    name = None
    for lab, p in labels:
        if (p["x"], p["y"]) == (iout["x"], iout["y"]):
            name = P.get_component_parameters(PRJ, lab["iid"])["parameters"].get("Name")
    if name in ("S2M", "LRR"):
        t = 0.3 if name == "S2M" else 0.4
        P.set_component_parameters(PRJ, o["iid"], {"Timsw": t})
        print(f"timer {o['iid']} publishes {name} -> Timsw = {t}")

machine = [o for o in objs if o["defn_name"] == "master:sync_machine"][0]["iid"]
P.set_component_parameters(PRJ, machine, {"P0": P0, "Q0": Q0, "Pheta": PHETA})
print("machine:", {k: v for k, v in P.get_component_parameters(PRJ, machine)["parameters"].items()
                   if k in ("P0", "Q0", "Pheta", "VT", "OMO", "MVA", "VbaseLL", "Igov", "Iexc",
                            "machsw", "Enab", "Ospd")})
P.save(PRJ)

n0 = len(P.messages(PRJ)["messages"])
P.app().project(PRJ).build()
errs = [x["text"] for x in P.messages(PRJ)["messages"][n0:] if x["status"].startswith("error")]
if errs:
    for e in errs[:6]:
        print("E:", e.encode("ascii", "replace").decode())
    sys.exit("build failed")

P.run(PRJ, wait=True, poll=1.0, timeout=3600)
psout = P.find_output_file(PRJ)
for _ in range(20):
    try:
        chs = [c[1] for c in P.list_output_channels(psout) if not c[1].endswith("Domain")]
        break
    except Exception:
        time.sleep(1.0)
series = {c: P.trace_series(psout, c) for c in chs}
print("t".rjust(6) + "".join(f"{c.split('/')[-3][:11]:>13}" for c in chs))
for t in (0.05, 0.2, 0.29, 0.45, 0.6, 1.0, 2.0, 3.0, 5.0):
    row = f"{t:>6.2f}"
    for c, s in series.items():
        row += f"{min(s, key=lambda p: abs(p[0] - t))[1]:>13.5g}"
    print(row)
