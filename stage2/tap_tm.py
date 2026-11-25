"""Tap the group's own 'TM' (mechanical torque) name and record it.

The example does this with a second datalabel carrying the same name placed far from
the first one; the only rule is that the datalabel must not land on another wire
(that would publish the name on that node -> 'source contention').
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
P.connect()
objs = P.list_canvas_objects(PRJ)["objects"]
xs = [o["bounds"][2] for o in objs]
x = max(xs) + 6
y = 60
lbl = P.add_component(PRJ, "master", "datalabel", x=x, y=y)["iid"]
P.set_component_parameters(PRJ, lbl, {"Name": "TM"})
lp = {p["name"]: p for p in P.get_ports(PRJ, lbl)["ports"]}["A"]
pgb = P.add_component(PRJ, "master", "pgb", x=x + 8, y=y)["iid"]
sp = {p["name"]: p for p in P.get_ports(PRJ, pgb)["ports"]}["Signl"]
P.create_wire(PRJ, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
P.set_component_parameters(PRJ, pgb, {"Name": "TM", "UseSignalName": "YES"})
print("TM tap at", (lp["x"], lp["y"]), "pgb at", (sp["x"], sp["y"]))
P.save(PRJ)
