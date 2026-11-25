"""Publish a permanent 'INIT0'=0 signal and bind the governor/turbine INIT to it.

'INIT' is a signal binding by name: INIT='NONE' makes PSCAD look for a signal named
NONE. A const 0 published as INIT0 lets the governor run freely from a zero gate,
which tests whether a permanently-high InitGv is what freezes the gate.
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
P.connect()
objs = P.list_canvas_objects(PRJ)["objects"]
x = max(o["bounds"][2] for o in objs) + 6
y = 66
c = P.add_component(PRJ, "master", "const", x=x, y=y, parameters={"Value": 0.0})["iid"]
out = {p["name"]: p for p in P.get_ports(PRJ, c)["ports"]}["OUT"]
lbl = P.add_component(PRJ, "master", "datalabel", x=out["x"] + 5, y=y)["iid"]
P.set_component_parameters(PRJ, lbl, {"Name": "INIT0"})
lp = {p["name"]: p for p in P.get_ports(PRJ, lbl)["ports"]}["A"]
P.create_wire(PRJ, [[out["x"], out["y"]], [lp["x"], lp["y"]]])

for o in objs:
    if o["defn_name"] in ("master:hy_gov", "master:hy_tur"):
        P.set_component_parameters(PRJ, o["iid"], {"INIT": "INIT0"})
        print(o["defn_name"], "INIT ->", P.get_component_parameters(PRJ, o["iid"])["parameters"]["INIT"])
P.save(PRJ)
