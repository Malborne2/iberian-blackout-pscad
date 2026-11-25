"""Record V and angle at all ten generator buses of `iberia3` (the multimeter `Ph` route).

`Ph` is a *parameter*, not a signal name, so it creates a channel only when a datalabel+pgb
references it. Verified with `Ph37` (channel `Root/Main/Ph37/0/1`, PGBS 20 -> 21).

Run: python stage2_bus_angles_final.py
"""
import sys

import pscad_ops as P

DST = "iberia3"
BUSES = (30, 31, 32, 33, 34, 35, 36, 37, 38, 39)
P.connect()


def ports(iid):
    return {p["name"]: p for p in P.get_ports(DST, iid)["ports"]}


def align(iid, port_name, target):
    for _ in range(8):
        p = ports(iid)[port_name]
        dx, dy = target[0] - p["x"], target[1] - p["y"]
        if dx == 0 and dy == 0:
            return
        loc = P.get_ports(DST, iid)["location"]
        P.move_component(DST, iid, loc[0] + dx, loc[1] + dy)
    p = ports(iid)[port_name]
    assert (p["x"], p["y"]) == tuple(target), (iid, port_name, p)


have = set()
for o in P.list_canvas_objects(DST)["objects"]:
    if o["defn_name"] == "master:pgb":
        nm = str(P.get_component_parameters(DST, o["iid"])["parameters"].get("Name", ""))
        have.add(nm)

for bus in BUSES:
    name = f"Ph{bus}"
    if name in have:
        print(f"{name}: already recorded")
        continue
    rect = P.find_empty_rect(DST, 16, 6, [95, 95])
    lbl = P.add_component(DST, "master", "datalabel", x=rect["left"], y=rect["top"] + 2)["iid"]
    P.set_component_parameters(DST, lbl, {"Name": name})
    lp = ports(lbl)["A"]
    pgb = P.add_component(DST, "master", "pgb", x=rect["left"] + 7, y=rect["top"])["iid"]
    align(pgb, "Signl", (lp["x"] + 3, lp["y"]))
    sp = ports(pgb)["Signl"]
    P.create_wire(DST, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
    P.set_component_parameters(DST, pgb, {"Name": name, "UseSignalName": "YES",
                                          "Units": "deg", "Min": -180.0, "Max": 180.0})
    print(f"{name}: label pair at {rect['left']},{rect['top']}")

P.save(DST)
P.app().project(DST).clean()
P.app().project(DST).build()
errs = [x["text"] for x in P.messages(DST)["messages"] if x["status"].startswith("error")]
d = P.build_dimensions(DST).get("dimensions") or {}
print(f"build: errors={len(errs)} NODES={d.get('NODES')} NPAGES={d.get('NPAGES')} "
      f"SUBSYS={d.get('SUBSYS')} BRANCHES={d.get('BRANCHES')} PGBS={d.get('PGBS')}")
for t in errs[:8]:
    print("  E:", t)
if errs:
    sys.exit(1)

P.set_project_parameters(DST, {"time_step": 50.0, "time_duration": 3.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
P.run(DST, wait=True, poll=1.0, timeout=1800)
print("log tail:", P.output(DST, 120))

psout = P.find_output_file(DST)
print("psout:", psout)
from statistics import fmean  # noqa: E402

print(f"\n{'bus':>4}{'Vd (pu)':>10}{'Ph (deg)':>11}")
for bus in BUSES:
    r = P.trace_window(psout, f"Root/Main/Ph{bus}/0/1", 2.5, 2.99)
    v = P.trace_window(psout, f"Root/Main/multimeter[{BUSES.index(bus) + 1}]/4/Vd", 2.5, 2.99)
    print(f"{bus:>4}{v.get('mean', float('nan')):>10.4f}{r.get('mean', float('nan')):>11.3f}")
