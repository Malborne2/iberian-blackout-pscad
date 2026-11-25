"""Add channels for names the pasted group already publishes (EF, IF) - no new labels
are created on any wire, only a receiving datalabel + pgb in free space.

Run: python tap_names.py sb14 EF IF
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
NAMES = sys.argv[2:]
P.connect()


def ports(iid):
    return {p["name"]: p for p in P.get_ports(PRJ, iid)["ports"]}


def align(iid, port_name, target):
    for _ in range(8):
        p = ports(iid)[port_name]
        dx, dy = target[0] - p["x"], target[1] - p["y"]
        if dx == 0 and dy == 0:
            return
        loc = P.get_ports(PRJ, iid)["location"]
        P.move_component(PRJ, iid, loc[0] + dx, loc[1] + dy)


objs = P.list_canvas_objects(PRJ)["objects"]
x = max(o["bounds"][2] for o in objs) + 6
for i, nm in enumerate(NAMES):
    y = 40 + 4 * i
    lbl = P.add_component(PRJ, "master", "datalabel", x=x, y=y)["iid"]
    P.set_component_parameters(PRJ, lbl, {"Name": nm})
    lp = ports(lbl)["A"]
    pgb = P.add_component(PRJ, "master", "pgb", x=x + 8, y=y)["iid"]
    align(pgb, "Signl", (lp["x"] + 3, lp["y"]))
    sp = ports(pgb)["Signl"]
    P.create_wire(PRJ, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
    P.set_component_parameters(PRJ, pgb, {"Name": nm, "UseSignalName": "YES"})
    print("channel", nm, "at", (lp["x"], lp["y"]))
P.save(PRJ)
