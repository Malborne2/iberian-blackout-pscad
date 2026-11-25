"""Can the multimeter's computed `Ph` angle be recorded by a datalabel+pgb?

The phase meters of `stage2_phase_meters.py` failed: five taps on a 39-bus canvas produced
implied connections and two type-contention errors, i.e. exactly the geometry trap this
project has already paid for. The multimeter variant needs no geometry at all **if** the
`Ph` output is a signal name PSCAD can resolve. Test with ONE label pair on a fresh clone.

`save_as` RENAMES the loaded project (measured), so the pristine file is reloaded first and
the clone is `iberia3`; `iberia1_stage1.pscx` on disk is never written.

Run: python stage2_ph_probe.py
"""
import sys

import pscad_ops as P

DST = "iberia3"
P.connect()

if DST not in [p["name"] for p in P.app().projects()]:
    if "iberia1_stage1" not in [p["name"] for p in P.app().projects()]:
        P.app().load(r"C:\PSCAD_work\iberia1_stage1.pscx")
    print("clone:", P.save_as("iberia1_stage1", DST, folder=r"C:\PSCAD_work"))

BUS = {1837570401: 37, 470679792: 30, 1917341412: 39, 827627569: 31, 351692673: 32,
       882978752: 34, 873234036: 33, 48983152: 36, 1853913980: 35, 198841240: 38}

for o in [x for x in P.list_canvas_objects(DST)["objects"] if x["defn_name"] == "master:multimeter"]:
    bus = BUS[o["iid"]]
    P.set_component_parameters(DST, o["iid"], {"MeasPh": 2, "Freq": "50.0 [Hz]", "Ph": f"Ph{bus}"})


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


# one label pair in guaranteed-free space
rect = P.find_empty_rect(DST, 14, 8, [95, 95])
print("free rect:", rect)
lbl = P.add_component(DST, "master", "datalabel", x=rect["left"], y=rect["top"] + 2)["iid"]
P.set_component_parameters(DST, lbl, {"Name": "Ph37"})
lp = ports(lbl)["A"]
pgb = P.add_component(DST, "master", "pgb", x=rect["left"] + 7, y=rect["top"])["iid"]
align(pgb, "Signl", (lp["x"] + 3, lp["y"]))
sp = ports(pgb)["Signl"]
P.create_wire(DST, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
P.set_component_parameters(DST, pgb, {"Name": "Ph37", "UseSignalName": "YES",
                                     "Units": "deg", "Min": -180.0, "Max": 180.0})
print("label pair for Ph37 at", (lp["x"], lp["y"]))

P.save(DST)
P.app().project(DST).clean()
P.app().project(DST).build()
errs = [x["text"] for x in P.messages(DST)["messages"] if x["status"].startswith("error")]
d = P.build_dimensions(DST).get("dimensions") or {}
print(f"build: errors={len(errs)} NODES={d.get('NODES')} PGBS={d.get('PGBS')}")
for t in errs[:6]:
    print("  E:", t)
if errs:
    sys.exit(1)

P.set_project_parameters(DST, {"time_step": 50.0, "time_duration": 0.5,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
P.run(DST, wait=True, poll=1.0, timeout=1800)
psout = P.find_output_file(DST)
print("psout:", psout)
hits = [str(path) for _, path in P.list_output_channels(psout) if "Ph" in str(path)]
print("Ph channels:", hits)
