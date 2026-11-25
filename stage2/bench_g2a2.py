"""Stage 2 / gate G2a: SyncUnit on an infinite bus - correct electrical terminal.

Established from the master library definition (master.pslx):
    <port name="NS" dim="3" mode="Electrical">   <- the 3-phase STATOR TERMINAL
    <port name="mvit" dim="3" mode="Output" cond=(Term==3)>  <- Vt measurement to the exciter
    <port name="N" dim="1" mode="Electrical" cond=(Neut==1)> / internal ground otherwise

So the network connects at NS, never at mvit. The pasted example loads NS with an
R-L's grounding demo; that load is removed here and replaced by the transformer.

    NS --[wire]-- xfmr 18/400 --[wire]-- source3
      \\-- voltmetergnd (Vt)

Run: python bench_g2a2.py sb9
"""
import sys
import time

import pscad_ops as P

PRJ = sys.argv[1]
P.connect()
log = print


def check(tag, stop=True):
    P.save(PRJ)
    n0 = len(P.messages(PRJ)["messages"])
    P.app().project(PRJ).build()
    new = P.messages(PRJ)["messages"][n0:]
    errs = [x["text"] for x in new if x["status"].startswith("error")]
    warns = [x["text"] for x in new if x["status"].startswith("warning")]
    d = P.build_dimensions(PRJ).get("dimensions") or {}
    log(f"[{tag}] errors={len(errs)} warnings={len(warns)} NODES={d.get('NODES')} "
        f"NPAGES={d.get('NPAGES')} SUBSYS={d.get('SUBSYS')} BRANCHES={d.get('BRANCHES')}")
    for t in errs[:6]:
        log("     E:", t.encode("ascii", "replace").decode())
    for t in warns[:4]:
        log("     W:", t.encode("ascii", "replace").decode())
    if errs and stop:
        sys.exit("stop at " + tag)
    return len(errs)


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


def prune_load(objs):
    """Remove the example's R-L load on NS (multimeter, breaker, L, R, their grounds)."""
    for o in objs:
        if o["defn_name"] in ("master:multimeter", "master:breaker3", "master:inductor", "master:resistor"):
            P.delete_component(PRJ, o["iid"])
            log("  removed", o["defn_name"], o["bounds"])


if PRJ in [p["name"] for p in P.app().projects()]:
    sys.exit("choose an unused project name")
P.create_project(PRJ, r"C:\PSCAD_work")

P.copy_region("sync_exciter_governor", 3, 7, 31, 41)
P.paste(PRJ, 3, 7, mode="transfer")
time.sleep(1.0)
objs = P.list_canvas_objects(PRJ)["objects"]
machine = [o for o in objs if o["defn_name"] == "master:sync_machine"][0]["iid"]
load_defs = ("master:multimeter", "master:breaker3", "master:inductor", "master:resistor")
boxes = [o["bounds"] for o in objs if o["defn_name"] in load_defs]
# delete only the wires that touch the removed components' boxes (+1 grid margin)
for o in objs:
    if not o["defn_name"].startswith("Wire"):
        continue
    l, t, r, b = o["bounds"]
    if any(not (r < bl - 1 or l > br + 1 or b < bt - 1 or t > bb + 1) for bl, bt, br, bb in boxes):
        P.delete_component(PRJ, o["iid"])
        log("  removed wire", o["bounds"])
prune_load(objs)
# the two grounds that served that load
for o in P.list_canvas_objects(PRJ)["objects"]:
    if o["defn_name"] == "master:ground":
        gx, gy = (o["bounds"][0] + o["bounds"][2]) // 2, o["bounds"][3]
        if any(bl - 2 <= gx <= br + 2 and bt - 2 <= gy <= bb + 2 for bl, bt, br, bb in boxes):
            P.delete_component(PRJ, o["iid"])
            log("  removed ground", o["bounds"])

ns = ports(machine)["NS"]
Y = ns["y"]
log("NS terminal at", (ns["x"], ns["y"]))
P.set_component_parameters(PRJ, machine, {"Name": "SyncUnit1", "MVA": 300.0, "VbaseLL": 18.0,
                                          "P0": 60.0, "Q0": 0.0, "POut": "POUT", "QOut": "QOUT"})
publish("LRR", 0.4, (44, 4))
publish("S2M", 0.3, (44, 10))
if check("s0 machine, load removed"):
    pass

# ---- transformer on NS
xt = ns["x"] + 6
tr = P.add_component(PRJ, "master", "xfmr-3p2w", x=xt + 4, y=Y)["iid"]
align(tr, "N1", (xt, Y))
pt = ports(tr)
P.set_component_parameters(PRJ, tr, {"V1": 18.0, "V2": 400.0, "Tmva": 300.0, "f": 50.0, "Xl": 0.1})
P.create_wire(PRJ, [[ns["x"], Y], [xt, Y]])
ground_at((pt["G1"]["x"], pt["G1"]["y"]))
P.create_wire(PRJ, [[pt["G1"]["x"], pt["G1"]["y"]], [pt["G2"]["x"], pt["G2"]["y"]]])
if check("s1 +xfmr"):
    pass

# ---- infinite bus
xinf = pt["N2"]["x"] + 6
src = P.add_component(PRJ, "master", "source3", x=xinf + 6, y=Y, orient=2)["iid"]
align(src, "N3", (xinf, Y))
ps = ports(src)
ground_at((ps["N"]["x"], ps["N"]["y"]))
P.create_wire(PRJ, [[pt["N2"]["x"], Y], [xinf, Y]])
P.set_component_parameters(PRJ, src, {"Name": "GRID", "Vm": 400.0, "Es": 400.0, "F": 50.0, "F0": 50.0,
                                      "MVA": 1500.0, "Vbase": 400.0, "V": "Vinf",
                                      "Imp": "RRL_VALUES", "Z1": 106.7, "Phi1": 85.0})
if check("s2 +source"):
    pass

# ---- terminal voltmeter (on the 18 kV side)
vm = P.add_component(PRJ, "master", "voltmetergnd", x=ns["x"] + 4, y=Y - 4)["iid"]
align(vm, "N1", (ns["x"] + 2, Y))
P.set_component_parameters(PRJ, vm, {"Name": "Vt"})
if check("s3 +voltmeter"):
    pass

P.set_project_parameters(PRJ, {"time_step": 20.0, "time_duration": 3.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
check("s4 +settings")
log("running 3 s ...")
st = P.run(PRJ, wait=True, poll=2.0, timeout=1800)
log("run:", st)
log("log tail:", P.output(PRJ, 600))
