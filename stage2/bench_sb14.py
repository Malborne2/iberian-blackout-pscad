"""G2a bench (sb14): pasted machine+AVR group, machine at 400 kV straight onto the bus.

* machine VbaseLL = 400 kV  -> no transformer in the way
* governor and turbine removed; `tmech` driven by a `const` whose body sits clear of
  the machine's other ports (orientation 2 puts the body to the right of its OUT port)
* `Igov = NO` (no Tmstd port), `Iexc = YES` (the proven AVX from the example)
* start-up timers at t = 0, i.e. the machine is a machine from the first step

Run: python bench_sb14.py sb14
"""
import sys
import time

import pscad_ops as P

PRJ = sys.argv[1]
P.connect()
log = print


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


def check(tag):
    P.save(PRJ)
    P.app().project(PRJ).clean()
    P.app().project(PRJ).build()
    m = P.messages(PRJ)
    errs = [x["text"] for x in m["messages"] if x["status"].startswith("error")]
    warns = [x["text"] for x in m["messages"] if x["status"].startswith("warning")]
    d = P.build_dimensions(PRJ).get("dimensions") or {}
    log(f"[{tag}] errors={len(errs)} warnings={len(warns)} NODES={d.get('NODES')} "
        f"NPAGES={d.get('NPAGES')} SUBSYS={d.get('SUBSYS')} BRANCHES={d.get('BRANCHES')}")
    for t in errs[:6]:
        log("     E:", t.encode("ascii", "replace").decode())
    for t in warns[:3]:
        log("     W:", t.encode("ascii", "replace").decode())
    if errs:
        sys.exit("stop at " + tag)


def publish(name, timer_time, near):
    t = P.add_component(PRJ, "master", "timerdefn", x=near[0], y=near[1],
                        parameters={"Timsw": timer_time})
    iout = ports(t["iid"])["iout"]
    lbl = P.add_component(PRJ, "master", "datalabel", x=iout["x"] + 5, y=iout["y"] + 5)["iid"]
    align(lbl, "A", (iout["x"], iout["y"]))
    P.set_component_parameters(PRJ, lbl, {"Name": name})


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

# ------------------------------------------------- paste + prune
P.copy_region("sync_exciter_governor", 3, 7, 31, 41)
P.paste(PRJ, 3, 7, mode="transfer")
time.sleep(1.0)
objs = P.list_canvas_objects(PRJ)["objects"]
drop = ("master:multimeter", "master:breaker3", "master:inductor", "master:resistor",
        "master:hy_gov", "master:hy_tur", "master:const")
boxes = [o["bounds"] for o in objs if o["defn_name"] in drop]
for o in objs:
    if o["defn_name"].startswith("Wire"):
        l, t, r, b = o["bounds"]
        if any(not (r < bl - 1 or l > br + 1 or b < bt - 1 or t > bb + 1) for bl, bt, br, bb in boxes):
            P.delete_component(PRJ, o["iid"])
for o in objs:
    if o["defn_name"] in drop:
        P.delete_component(PRJ, o["iid"])
for o in P.list_canvas_objects(PRJ)["objects"]:
    if o["defn_name"] == "master:datalabel":
        nm = P.get_component_parameters(PRJ, o["iid"])["parameters"].get("Name")
        if nm in ("W", "TM", "Tmstdy"):
            P.delete_component(PRJ, o["iid"])
    if o["defn_name"] == "master:ground":
        gx, gy = (o["bounds"][0] + o["bounds"][2]) // 2, o["bounds"][3]
        if any(bl - 2 <= gx <= br + 2 and bt - 2 <= gy <= bb + 2 for bl, bt, br, bb in boxes):
            P.delete_component(PRJ, o["iid"])

objs = P.list_canvas_objects(PRJ)["objects"]
machine = [o for o in objs if o["defn_name"] == "master:sync_machine"][0]["iid"]
P.set_component_parameters(PRJ, machine, {
    "Name": "SyncUnit1", "MVA": 300.0, "VbaseLL": 400.0, "H": 3.117,
    "OMO": 314.15926536, "P0": 60.0, "Q0": 0.0, "Pheta": 0.0,
    "Igov": "NO", "Iexc": "YES", "POut": "POUT", "QOut": "QOUT",
})
for o in P.list_canvas_objects(PRJ)["objects"]:
    if o["defn_name"] == "master:timerdefn":
        P.set_component_parameters(PRJ, o["iid"], {"Timsw": 0.0})
publish("S2M", 0.0, (40, 4))
publish("LRR", 0.0, (40, 10))
pm = ports(machine)
log("ports:", {k: (v["x"], v["y"]) for k, v in pm.items()})

# ------------------------------------------------- torque const (body to the right)
c = P.add_component(PRJ, "master", "const", x=pm["tmech"]["x"] + 8, y=pm["tmech"]["y"] + 6,
                    orient=2, parameters={"Value": 0.0})["iid"]
align(c, "OUT", (pm["tmech"]["x"], pm["tmech"]["y"]))
log("const bounds:", P.get_bounds(PRJ, [c])["bounds"], "OUT at tmech",
    (pm["tmech"]["x"], pm["tmech"]["y"]))
check("s0 machine+AVR, torque const")

# ------------------------------------------------- infinite bus at NS
ns = pm["NS"]
Y = ns["y"]
xinf = ns["x"] + 8
src = P.add_component(PRJ, "master", "source3", x=xinf + 6, y=Y, orient=2)["iid"]
align(src, "N3", (xinf, Y))
ps = ports(src)
g = P.add_component(PRJ, "master", "ground", x=ps["N"]["x"] + 5, y=ps["N"]["y"] + 5)["iid"]
align(g, "A", (ps["N"]["x"], ps["N"]["y"]))
P.create_wire(PRJ, [[ns["x"], Y], [xinf, Y]])
P.set_component_parameters(PRJ, src, {"Name": "GRID", "Vm": 400.0, "Es": 400.0, "F": 50.0, "F0": 50.0,
                                      "MVA": 300.0, "Vbase": 400.0, "V": "Vinf",
                                      "Imp": "RRL_VALUES", "R1p": 9.3, "L1p": 0.34,
                                      "Z1": 106.7, "Phi1": 85.0})
check("s1 +infinite bus")

# ------------------------------------------------- channels
vm = P.add_component(PRJ, "master", "voltmetergnd", x=ns["x"] + 3, y=Y - 5)["iid"]
align(vm, "N1", (ns["x"] + 3, Y))
P.set_component_parameters(PRJ, vm, {"Name": "Vt"})
for i, nm in enumerate(("POUT", "QOUT", "Vinf", "Vt")):
    channel(nm, 52, 38 + 4 * i)
P.set_project_parameters(PRJ, {"time_step": 20.0, "time_duration": 3.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
check("s2 +channels")
log("running 3 s ...")
P.run(PRJ, wait=True, poll=1.0, timeout=1800)
log("log tail:", P.output(PRJ, 200))
