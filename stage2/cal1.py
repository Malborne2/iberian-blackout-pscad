"""Calibration: what does `voltmetergnd` report for a known source voltage?

Circuit: source3 (400 kV, F=50) with its 3-phase terminal on a wire that runs to the
LEFT of the source (the source's single-phase neutral N sits 4 units to the right, so a
wire to the right would touch it: measured `Signal 'GND' dimension mismatch`).

Run: python cal1.py cal1c
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
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


def channel(name, x, y):
    lbl = P.add_component(PRJ, "master", "datalabel", x=x, y=y)["iid"]
    P.set_component_parameters(PRJ, lbl, {"Name": name})
    lp = ports(lbl)["A"]
    pgb = P.add_component(PRJ, "master", "pgb", x=x + 7, y=y)["iid"]
    align(pgb, "Signl", (lp["x"] + 3, lp["y"]))
    sp = ports(pgb)["Signl"]
    P.create_wire(PRJ, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
    P.set_component_parameters(PRJ, pgb, {"Name": name, "UseSignalName": "YES"})


if PRJ in [p["name"] for p in P.app().projects()]:
    sys.exit("choose an unused project name")
P.create_project(PRJ, r"C:\PSCAD_work")

Y = 20
src = P.add_component(PRJ, "master", "source3", x=20, y=Y, orient=2)["iid"]
align(src, "N3", (20, Y))
ps = ports(src)
print("source ports:", {k: (v["x"], v["y"]) for k, v in ps.items()})
g = P.add_component(PRJ, "master", "ground", x=ps["N"]["x"] + 5, y=ps["N"]["y"] + 5)["iid"]
align(g, "A", (ps["N"]["x"], ps["N"]["y"]))
P.set_component_parameters(PRJ, src, {"Name": "GRID", "Vm": "400 [kV]", "Es": "400 [kV]",
                                      "F": 50.0, "F0": 50.0, "MVA": 300.0, "Vbase": "400 [kV]",
                                      "Imp": "RRL_VALUES", "R1p": "9.3 [ohm]", "L1p": "0.34 [H]",
                                      "V": "Vinf"})

P.create_wire(PRJ, [[20, Y], [10, Y]])
vm = P.add_component(PRJ, "master", "voltmetergnd", x=14, y=Y - 6)["iid"]
align(vm, "N1", (14, Y))
P.set_component_parameters(PRJ, vm, {"Name": "Vpk"})
for i, nm in enumerate(("Vinf", "Vpk")):
    channel(nm, 30, 38 + 4 * i)

P.set_project_parameters(PRJ, {"time_step": 20.0, "time_duration": 0.2,
                               "sample_step": 50.0, "PlotType": "PSOUT"})
P.save(PRJ)
P.app().project(PRJ).clean()
P.app().project(PRJ).build()
for x in P.messages(PRJ)["messages"]:
    if x["status"].startswith("error"):
        print("E", x["text"].encode("ascii", "replace").decode()[:140])
print("dims", {k: (P.build_dimensions(PRJ).get("dimensions") or {}).get(k) for k in ("NODES", "BRANCHES", "PGBS")})
