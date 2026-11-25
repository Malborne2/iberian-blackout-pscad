"""Stage 2 input: bus angle (theta) at the five buses that will carry `SyncUnit` or France.

The multimeter's `MeasPh`/`Ph` route computes the angle (verified: `Ph37 = RVD1_1` is in
the generated Fortran) but the value never lands in the `.psout` — nothing records it and
the component exposes no signal port. So use `master:f_ph_mag_meter`, which has explicit
`PHASE`, `FREQ`, `Volts` output ports, and record it through the proven
producer-label -> pgb chain.

Buses: 30 (hydro), 31 & 32 (nuclear), 37 (CCGT), 39 (France equivalent).

Run: python stage2_phase_meters.py
"""
import sys

import pscad_ops as P

DST = "iberia2"
BUSES = (30, 31, 32, 37, 39)
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


# ---------------------------------------------------------------- clean a previous attempt
for o in P.list_canvas_objects(DST)["objects"]:
    if o["defn_name"] in ("master:f_ph_mag_meter",) or (
            o["defn_name"] in ("master:datalabel", "master:pgb")
            and str(P.get_component_parameters(DST, o["iid"])["parameters"].get("Name", "")).startswith("Ang")):
        P.delete_component(DST, o["iid"])
        print("deleted", o["defn_name"], o["bounds"])

buses = {int(str(P.get_component_parameters(DST, o["iid"])["parameters"]["Name"]).replace("Bus", "")):
         o for o in P.list_canvas_objects(DST)["objects"] if o["defn_name"] == "Bus"}

for bus in BUSES:
    b = buses[bus]["bounds"]
    x1, y1, x2, y2 = b
    tap = (x1 + 2, y1)
    meter = P.add_component(DST, "master", "f_ph_mag_meter", x=x1 + 6, y=y1 + 8)["iid"]
    align(meter, "N", (tap[0], tap[1] + 6))
    P.create_wire(DST, [list(tap), [tap[0], tap[1] + 6]])
    prm = P.get_component_parameters(DST, meter)["parameters"]
    print(f"bus {bus}: meter at N=({tap[0]},{tap[1] + 6}), tap on bus at {tap}")
    print("   defaults:", {k: prm[k] for k in ("Nph", "v3Cnfg", "vCnfg", "fCnfg", "pCnfg",
                                               "Vbas", "Fbas", "Ts") if k in prm})
    P.set_component_parameters(DST, meter, {
        "Name": f"M{bus}", "Nph": "THREEPHASE", "Fbas": "50.0 [Hz]", "Vbas": "400.0 [kV]",
        "pCnfg": "DEGREES",
    })
    prm = P.get_component_parameters(DST, meter)["parameters"]
    print("   set  :", {k: prm[k] for k in ("Nph", "Fbas", "Vbas", "pCnfg", "fCnfg") if k in prm})
    print("   ports:", sorted(ports(meter)))

    names = ports(meter)
    ph = names.get("Phase") or names.get("PHASE") or names.get("phase") or names.get("Ph")
    if ph is None:
        sys.exit(f"no phase port on f_ph_mag_meter: {sorted(names)}")
    P.create_wire(DST, [[ph["x"], ph["y"]], [ph["x"] + 4, ph["y"]]])
    lbl = P.add_component(DST, "master", "datalabel", x=ph["x"] + 8, y=ph["y"] + 4)["iid"]
    align(lbl, "A", (ph["x"] + 4, ph["y"]))
    P.set_component_parameters(DST, lbl, {"Name": f"Ang{bus}"})
    lp = ports(lbl)["A"]
    pgb = P.add_component(DST, "master", "pgb", x=lp["x"] + 6, y=lp["y"] + 4)["iid"]
    align(pgb, "Signl", (lp["x"] + 3, lp["y"]))
    sp = ports(pgb)["Signl"]
    P.create_wire(DST, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
    P.set_component_parameters(DST, pgb, {"Name": f"Ang{bus}", "UseSignalName": "YES",
                                         "Units": "deg", "Min": -180.0, "Max": 180.0})
    print(f"   PHASE -> Ang{bus} -> pgb")

P.save(DST)
P.app().project(DST).clean()
P.app().project(DST).build()
errs = [x["text"] for x in P.messages(DST)["messages"] if x["status"].startswith("error")]
warns = [x["text"] for x in P.messages(DST)["messages"] if x["status"].startswith("warning")]
d = P.build_dimensions(DST).get("dimensions") or {}
print(f"build: errors={len(errs)} warnings={len(warns)} NODES={d.get('NODES')} "
      f"NNODES={d.get('NNODES')} NPAGES={d.get('NPAGES')} SUBSYS={d.get('SUBSYS')} "
      f"BRANCHES={d.get('BRANCHES')} PGBS={d.get('PGBS')}")
for t in errs[:8]:
    print("  E:", t)
for t in warns[:6]:
    print("  W:", t)

if "--run" in sys.argv and not errs:
    P.set_project_parameters(DST, {"time_step": 50.0, "time_duration": 0.5,
                                   "sample_step": 200.0, "PlotType": "PSOUT"})
    P.run(DST, wait=True, poll=1.0, timeout=1800)
    print("log tail:", P.output(DST, 120))
