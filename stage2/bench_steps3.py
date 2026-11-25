"""G2a bench, step-checked, WITHOUT bus elements.

A `Bus` in this master library is a load-flow bus whose Name is also published as a
signal, which collides with the machine/exciter ports ('Output signal BUS18 type
mismatch at connection mvit'). Wires alone form the nodes, so the bench uses wires.

    mvit -- mmeter -- 18/400 xfmr -- source3

Run:  python bench_steps3.py sb7
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
    m = P.messages(PRJ)
    new = m["messages"][n0:]
    errs = [x["text"] for x in new if x["status"].startswith("error")]
    warns = [x["text"] for x in new if x["status"].startswith("warning")]
    d = P.build_dimensions(PRJ).get("dimensions") or {}
    log(f"[{tag}] errors={len(errs)} warnings={len(warns)} "
        f"NODES={d.get('NODES')} NPAGES={d.get('NPAGES')} SUBSYS={d.get('SUBSYS')} BRANCHES={d.get('BRANCHES')}")
    for t in errs[:6]:
        log("     E:", t.encode("ascii", "replace").decode())
    for t in warns[:4]:
        log("     W:", t.encode("ascii", "replace").decode())
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


if PRJ in [p["name"] for p in P.app().projects()]:
    sys.exit("choose an unused project name")
P.create_project(PRJ, r"C:\PSCAD_work")

# --- s0: machine group + start-up signals
P.copy_region("sync_exciter_governor", 3, 7, 31, 41)
P.paste(PRJ, 3, 7, mode="transfer")
time.sleep(1.0)
machine = [o for o in P.list_canvas_objects(PRJ)["objects"] if o["defn_name"] == "master:sync_machine"][0]["iid"]
mv = ports(machine)["mvit"]
Y = mv["y"]
P.set_component_parameters(PRJ, machine, {"Name": "SyncUnit1", "MVA": 300.0, "VbaseLL": 18.0,
                                          "P0": 60.0, "Q0": 0.0, "POut": "POUT", "QOut": "QOUT"})


def publish(name, timer_time, near):
    t = P.add_component(PRJ, "master", "timerdefn", x=near[0], y=near[1], parameters={"Timsw": timer_time})
    iout = ports(t["iid"])["iout"]
    lbl = P.add_component(PRJ, "master", "datalabel", x=iout["x"] + 4, y=iout["y"] + 4)["iid"]
    align(lbl, "A", (iout["x"], iout["y"]))
    P.set_component_parameters(PRJ, lbl, {"Name": name})


def publish_const(name, value, near):
    c = P.add_component(PRJ, "master", "const", x=near[0], y=near[1], parameters={"Value": value})
    out = ports(c["iid"])["OUT"]
    lbl = P.add_component(PRJ, "master", "datalabel", x=out["x"] + 4, y=out["y"] + 4)["iid"]
    align(lbl, "A", (out["x"], out["y"]))
    P.set_component_parameters(PRJ, lbl, {"Name": name})


publish("LRR", 0.4, (44, 4))
publish("S2M", 0.3, (44, 10))
publish_const("BRK", 1.0, (44, 16))
log("mvit:", (mv["x"], mv["y"]))
if check("s0 machine + start-up"):
    sys.exit("stop at s0")

# --- s1: multimeter in series at the machine terminals
mm = P.add_component(PRJ, "master", "multimeter", x=mv["x"] + 8, y=Y - 2)["iid"]
pm = ports(mm)
pL = "A" if pm["A"]["x"] < pm["B"]["x"] else "B"
align(mm, pL, (mv["x"] + 3, Y))
pm = ports(mm)
pR = "B" if pL == "A" else "A"
P.create_wire(PRJ, [[mv["x"], Y], [pm[pL]["x"], Y]])
P.set_component_parameters(PRJ, mm, {"S": 300.0, "BaseV": 18.0, "Freq": 50.0, "RMS": "YES_ANALOG",
                                     "MeasI": "YES", "MeasV": "YES",
                                     "Vd": "Vt", "Pd": "Pt", "Qd": "Qt"})
if check("s1 +multimeter"):
    sys.exit("stop at s1")

# --- s2: transformer
xt = pm[pR]["x"] + 2
P.create_wire(PRJ, [[pm[pR]["x"], Y], [xt, Y]])
tr = P.add_component(PRJ, "master", "xfmr-3p2w", x=xt + 4, y=Y)["iid"]
align(tr, "N1", (xt, Y))
pt = ports(tr)
P.set_component_parameters(PRJ, tr, {"V1": 18.0, "V2": 400.0, "Tmva": 300.0, "f": 50.0, "Xl": 0.1})
if check("s2 +xfmr"):
    sys.exit("stop at s2")

# --- s3: infinite bus source
xinf = pt["N2"]["x"] + 6
P.create_wire(PRJ, [[pt["N2"]["x"], Y], [xinf, Y]])
src = P.add_component(PRJ, "master", "source3", x=xinf + 6, y=Y, orient=2)["iid"]
align(src, "N3", (xinf, Y))
P.set_component_parameters(PRJ, src, {"Name": "GRID", "Vm": 400.0, "Es": 400.0, "F": 50.0, "F0": 50.0,
                                      "MVA": 1500.0, "Vbase": 400.0, "V": "Vinf",
                                      "Imp": "RRL_VALUES", "Z1": 106.7, "Phi1": 85.0})
log("source:", {k: (v["x"], v["y"]) for k, v in ports(src).items()})
if check("s3 +source"):
    sys.exit("stop at s3")

P.set_project_parameters(PRJ, {"time_step": 20.0, "time_duration": 3.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
if check("s4 +run settings"):
    sys.exit("stop at s4")
log("all steps clean")
