"""Attach pgb output channels to named signals (datalabel <Name> -> pgb 'Signl').

PSCAD only records a signal in the .psout if a pgb references it; a name on a
component output is not enough (measured on sb10: 0 channels from POUT/QOUT/Vt).

Run: python add_channels.py sb10 POUT QOUT Vt Vinf W
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
NAMES = sys.argv[2:]
P.connect()

x0, y0 = 50, 34
for i, name in enumerate(NAMES):
    y = y0 + 4 * i
    lbl = P.add_component(PRJ, "master", "datalabel", x=x0, y=y)["iid"]
    P.set_component_parameters(PRJ, lbl, {"Name": name})
    px, py = {p["name"]: p for p in P.get_ports(PRJ, lbl)["ports"]}["A"]["x"], y
    pgb = P.add_component(PRJ, "master", "pgb", x=x0 + 6, y=y)["iid"]
    # move pgb so its Signl input lands 2 units right of the datalabel port
    for _ in range(6):
        p = {q["name"]: q for q in P.get_ports(PRJ, pgb)["ports"]}["Signl"]
        dx, dy = (px + 2) - p["x"], py - p["y"]
        if dx == 0 and dy == 0:
            break
        loc = P.get_ports(PRJ, pgb)["location"]
        P.move_component(PRJ, pgb, loc[0] + dx, loc[1] + dy)
    sp = {q["name"]: q for q in P.get_ports(PRJ, pgb)["ports"]}["Signl"]
    P.create_wire(PRJ, [[px, py], [sp["x"], sp["y"]]])
    P.set_component_parameters(PRJ, pgb, {"Name": name, "UseSignalName": "YES", "Units": "", "Max": 0.0, "Min": 0.0})
    print(f"channel {name}: datalabel {lbl} -> pgb {pgb} at ({sp['x']},{sp['y']})")

P.save(PRJ)
n0 = len(P.messages(PRJ)["messages"])
P.app().project(PRJ).build()
new = P.messages(PRJ)["messages"][n0:]
for x in new:
    print(" ", x["status"], "|", x["text"].encode("ascii", "replace").decode())
print("dims:", {k: (P.build_dimensions(PRJ).get("dimensions") or {}).get(k) for k in ("NODES", "PGBS")})
