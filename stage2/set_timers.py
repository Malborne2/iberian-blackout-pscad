"""Set the start-up timers by the name they publish (S2M 0.3 s, LRR 0.4 s - as the
example does) and report.

Run: python set_timers.py sb14 [s2m] [lrr]
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
S2M = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
LRR = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
P.connect()
objs = P.list_canvas_objects(PRJ)["objects"]


def ports(iid):
    return {p["name"]: p for p in P.get_ports(PRJ, iid)["ports"]}


labels = {o["iid"]: (o, ports(o["iid"])["A"]) for o in objs if o["defn_name"] == "master:datalabel"}
for o in objs:
    if o["defn_name"] != "master:timerdefn":
        continue
    iout = ports(o["iid"])["iout"]
    name = None
    for lab, p in labels.values():
        if (p["x"], p["y"]) == (iout["x"], iout["y"]):
            name = P.get_component_parameters(PRJ, lab["iid"])["parameters"].get("Name")
    if name == "S2M":
        P.set_component_parameters(PRJ, o["iid"], {"Timsw": S2M})
        print("S2M timer", o["iid"], "->", S2M)
    elif name == "LRR":
        P.set_component_parameters(PRJ, o["iid"], {"Timsw": LRR})
        print("LRR timer", o["iid"], "->", LRR)
P.save(PRJ)
