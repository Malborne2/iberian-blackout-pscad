"""Turn on the phase measurement of the ten generator-bus multimeters and run.

`MeasPh` is a choice parameter (`YES_RADIANS`, `YES_DEGREES`, `NO`); on this machine choice
parameters must be written by **index**. `Freq` on these meters was left at 60 Hz by the
rebase, so it is set to 50 Hz here as well (the phase measurement uses it).

Run: python stage2_bus_angles.py --run
"""
import sys

import pscad_ops as P

DST = "iberia2"
P.connect()

# multimeter iid order on the canvas -> generator bus (matched by position with each source)
BUS = {1837570401: 37, 470679792: 30, 1917341412: 39, 827627569: 31, 351692673: 32,
       882978752: 34, 873234036: 33, 48983152: 36, 1853913980: 35, 198841240: 38}

objs = [o for o in P.list_canvas_objects(DST)["objects"] if o["defn_name"] == "master:multimeter"]
for i, o in enumerate(objs, start=1):
    bus = BUS[o["iid"]]
    P.set_component_parameters(DST, o["iid"], {
        "MeasPh": 2,                      # 1 = YES_RADIANS, 2 = YES_DEGREES, 3 = NO
        "Freq": "50.0 [Hz]",
        "Ph": f"Ph{bus}",
    })
    prm = P.get_component_parameters(DST, o["iid"])["parameters"]
    print(f"  mm{i:>2} bus {bus:>2}: MeasPh={prm.get('MeasPh')!r} Freq={prm.get('Freq')} "
          f"Ph={prm.get('Ph')!r}")

if "--run" in sys.argv:
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
    P.set_project_parameters(DST, {"time_step": 50.0, "time_duration": 0.5,
                                   "sample_step": 200.0, "PlotType": "PSOUT"})
    P.run(DST, wait=True, poll=1.0, timeout=1800)
    print("log tail:", P.output(DST, 120))
