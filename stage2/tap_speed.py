"""Tap the machine's `speed` output on a stub wire (a datalabel placed directly on an
output port gives 'A constant signal cannot be utilized before it is generated').

Run: python tap_speed.py sb14
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
P.connect()


def ports(iid):
    return {p["name"]: p for p in P.get_ports(PRJ, iid)["ports"]}


objs = P.list_canvas_objects(PRJ)["objects"]
m = [o for o in objs if o["defn_name"] == "master:sync_machine"][0]["iid"]
sp = ports(m)["speed"]
print("speed port", (sp["x"], sp["y"]))
P.create_wire(PRJ, [[sp["x"], sp["y"]], [sp["x"], sp["y"] + 4]])
lbl = P.add_component(PRJ, "master", "datalabel", x=sp["x"] + 4, y=sp["y"] + 8)["iid"]
P.set_component_parameters(PRJ, lbl, {"Name": "Wspd"})
for _ in range(6):
    p = ports(lbl)["A"]
    dx, dy = sp["x"] - p["x"], (sp["y"] + 4) - p["y"]
    if dx == 0 and dy == 0:
        break
    loc = P.get_ports(PRJ, lbl)["location"]
    P.move_component(PRJ, lbl, loc[0] + dx, loc[1] + dy)
lp = ports(lbl)["A"]
pgb = P.add_component(PRJ, "master", "pgb", x=lp["x"] + 8, y=lp["y"])["iid"]
for _ in range(6):
    p = ports(pgb)["Signl"]
    dx, dy = (lp["x"] + 2) - p["x"], lp["y"] - p["y"]
    if dx == 0 and dy == 0:
        break
    loc = P.get_ports(PRJ, pgb)["location"]
    P.move_component(PRJ, pgb, loc[0] + dx, loc[1] + dy)
spg = ports(pgb)["Signl"]
P.create_wire(PRJ, [[lp["x"], lp["y"]], [spg["x"], spg["y"]]])
P.set_component_parameters(PRJ, pgb, {"Name": "Wspd", "UseSignalName": "YES"})
print("Wspd tap at", (lp["x"], lp["y"]))

for o in P.list_canvas_objects(PRJ)["objects"]:
    if o["defn_name"] == "master:timerdefn":
        print("timer", o["iid"], P.get_component_parameters(PRJ, o["iid"])["parameters"])
P.save(PRJ)
