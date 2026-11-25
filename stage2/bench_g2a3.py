"""G2a bench, third topology: exactly PSCAD's own shape (sync_SCtest.pscx).

Differences from the previous attempt, all copied from PSCAD's example:
  * `master:xfmr_3p2w` (the variant PSCAD's machine examples use), generator side DELTA
    (YD1=D), grid side Y grounded (YD2=Y, YD2_VG=11);
  * source3 impedance entered in OHMS/HENRY with Imp=RRL_VALUES (R1p, L1p), not pu:
    the example uses R1p=1 ohm, L1p=0.01 H on a 230 kV / 120 MVA base.
  * here: 0.2 pu on 300 MVA / 400 kV = 106.7 ohm -> R1p=9.3 ohm, L1p=0.34 H.

Run: python bench_g2a3.py sb11
"""
import sys
import time

import pscad_ops as P

PRJ = sys.argv[1]
P.connect()
log = print


def check(tag):
    P.save(PRJ)
    n0 = len(P.messages(PRJ)["messages"])
    P.app().project(PRJ).build()
    new = P.messages(PRJ)["messages"][n0:]
    errs = [x["text"] for x in new if x["status"].startswith("error")]
    warns = [x["text"] for x in new if x["status"].startswith("warning")]
    d = P.build_dimensions(PRJ).get("dimensions") or {}
    log(f"[{tag}] errors={len(errs)} warnings={len(warns)} NODES={d.get('NODES')} "
        f"NPAGES={d.get('NPAGES')} SUBSYS={d.get('SUBSYS')} BRANCHES={d.get('BRANCHES')}")
    for t in errs[:5]:
        log("     E:", t.encode("ascii", "replace").decode())
    for t in warns[:3]:
        log("     W:", t.encode("ascii", "replace").decode())
    if errs:
        sys.exit("stop at " + tag)


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
    p = ports(iid)[port_name]
    assert (p["x"], p["y"]) == tuple(target), (iid, port_name, p)


def ground_at(target):
    g = P.add_component(PRJ, "master", "ground", x=target[0] + 4, y=target[1] + 4)["iid"]
    align(g, "A", target)


def publish(name, timer_time, near):
    t = P.add_component(PRJ, "master", "timerdefn", x=near[0], y=near[1], parameters={"Timsw": timer_time})
    iout = ports(t["iid"])["iout"]
    lbl = P.add_component(PRJ, "master", "datalabel", x=iout["x"] + 4, y=iout["y"] + 4)["iid"]
    align(lbl, "A", (iout["x"], iout["y"]))
    P.set_component_parameters(PRJ, lbl, {"Name": name})


def channel(name, x, y):
    lbl = P.add_component(PRJ, "master", "datalabel", x=x, y=y)["iid"]
    P.set_component_parameters(PRJ, lbl, {"Name": name})
    lp = ports(lbl)["A"]
    pgb = P.add_component(PRJ, "master", "pgb", x=x + 6, y=y)["iid"]
    sp = ports(pgb)["Signl"]
    P.create_wire(PRJ, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
    P.set_component_parameters(PRJ, pgb, {"Name": name, "UseSignalName": "YES"})


if PRJ in [p["name"] for p in P.app().projects()]:
    sys.exit("choose an unused project name")
P.create_project(PRJ, r"C:\PSCAD_work")

# ---- machine group
P.copy_region("sync_exciter_governor", 3, 7, 31, 41)
P.paste(PRJ, 3, 7, mode="transfer")
time.sleep(1.0)
objs = P.list_canvas_objects(PRJ)["objects"]
machine = [o for o in objs if o["defn_name"] == "master:sync_machine"][0]["iid"]
load_defs = ("master:multimeter", "master:breaker3", "master:inductor", "master:resistor")
boxes = [o["bounds"] for o in objs if o["defn_name"] in load_defs]
for o in objs:
    if o["defn_name"].startswith("Wire"):
        l, t, r, b = o["bounds"]
        if any(not (r < bl - 1 or l > br + 1 or b < bt - 1 or t > bb + 1) for bl, bt, br, bb in boxes):
            P.delete_component(PRJ, o["iid"])
for o in objs:
    if o["defn_name"] in load_defs:
        P.delete_component(PRJ, o["iid"])
for o in P.list_canvas_objects(PRJ)["objects"]:
    if o["defn_name"] == "master:ground":
        gx, gy = (o["bounds"][0] + o["bounds"][2]) // 2, o["bounds"][3]
        if any(bl - 2 <= gx <= br + 2 and bt - 2 <= gy <= bb + 2 for bl, bt, br, bb in boxes):
            P.delete_component(PRJ, o["iid"])

ns = ports(machine)["NS"]
Y = ns["y"]
P.set_component_parameters(PRJ, machine, {"Name": "SyncUnit1", "MVA": 300.0, "VbaseLL": 18.0,
                                          "P0": 60.0, "Q0": 0.0, "POut": "POUT", "QOut": "QOUT"})
publish("LRR", 0.4, (44, 4))
publish("S2M", 0.3, (44, 10))
check("s0 machine")

# ---- generator step-up transformer (delta 18 kV / grounded-Y 400 kV)
xt = ns["x"] + 8
tr = P.add_component(PRJ, "master", "xfmr_3p2w", x=xt + 4, y=Y)["iid"]
align(tr, "N1", (xt, Y))
pt = ports(tr)
log("xfmr_3p2w ports:", {k: (v["x"], v["y"]) for k, v in pt.items()})
P.set_component_parameters(PRJ, tr, {"Name": "GSU1", "V1": 18.0, "V2": 400.0, "Tmva": 300.0, "f": 50.0,
                                     "Xl": 0.1, "YD1": "D", "YD2": "Y", "YD2_VG": 11, "ModType": "ONLY_LEAKAGE"})
if "G1" in pt:
    ground_at((pt["G1"]["x"], pt["G1"]["y"]))
if "G2" in pt:
    ground_at((pt["G2"]["x"], pt["G2"]["y"]))
P.create_wire(PRJ, [[ns["x"], Y], [xt, Y]])
check("s1 +GSU")

# ---- infinite bus
xinf = pt["N2"]["x"] + 8
P.create_wire(PRJ, [[pt["N2"]["x"], Y], [xinf, Y]])
src = P.add_component(PRJ, "master", "source3", x=xinf + 6, y=Y, orient=2)["iid"]
align(src, "N3", (xinf, Y))
ps = ports(src)
ground_at((ps["N"]["x"], ps["N"]["y"]))
P.set_component_parameters(PRJ, src, {"Name": "GRID", "Vm": 400.0, "Es": 400.0, "F": 50.0, "F0": 50.0,
                                      "MVA": 300.0, "Vbase": 400.0, "V": "Vinf",
                                      "Imp": "RRL_VALUES", "R1p": 9.3, "L1p": 0.34,
                                      "Z1": 106.7, "Phi1": 85.0})
check("s2 +source")

# ---- channels
vm = P.add_component(PRJ, "master", "voltmetergnd", x=ns["x"] + 4, y=Y - 4)["iid"]
align(vm, "N1", (ns["x"] + 3, Y))
P.set_component_parameters(PRJ, vm, {"Name": "Vt"})
for i, nm in enumerate(("POUT", "QOUT", "Vt", "Vinf", "W")):
    channel(nm, 56, 34 + 4 * i)
P.set_project_parameters(PRJ, {"time_step": 20.0, "time_duration": 5.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
check("s3 +channels")
log("running 5 s ...")
P.run(PRJ, wait=True, poll=2.0, timeout=1800)
log("log tail:", P.output(PRJ, 300))
