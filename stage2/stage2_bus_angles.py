"""Stage 2 input: V and angle (theta) at every generator bus of `iberia1_stage1`.

The model already carries ten `multimeter` components on the generator buses; they only
report `Vd` (pu rms). The multimeter also has `MeasPh` ("Phase Angle") and an output name
parameter `Ph`, which drives the DSL `MPHASE3PS` positive-sequence phase measurement: the
phase of the fundamental at that node **relative to the simulation's t = 0 reference**,
i.e. exactly the bus angle a `SyncUnit` needs for `V0`/`Ph0`.

This script never touches `iberia1_stage1`: it works on `iberia2` (a save_as clone).

Run: python stage2_bus_angles.py
"""
import json
import sys

import pscad_ops as P

SRC, DST = "iberia1_stage1", "iberia2"
P.connect()

if DST not in [p["name"] for p in P.app().projects()]:
    print("clone:", P.save_as(SRC, DST, folder=r"C:\PSCAD_work"))

objs = P.list_canvas_objects(DST)["objects"]
meters = [o for o in objs if o["defn_name"] == "master:multimeter"]
print(f"{len(meters)} multimeters")

rng = P.get_parameter_range(DST, meters[0]["iid"], "MeasPh")
print("MeasPh range:", rng)

for i, o in enumerate(meters, start=1):
    prm = P.get_component_parameters(DST, o["iid"])["parameters"]
    print(f"  [{i}] iid={o['iid']} bounds={o['bounds']}  Name={prm.get('Name')!r} "
          f"MeasPh={prm.get('MeasPh')!r} Freq={prm.get('Freq')!r} "
          f"Vd-name={prm.get('Vd')!r} Ph-name={prm.get('Ph')!r}")
