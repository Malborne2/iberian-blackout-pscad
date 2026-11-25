"""G2a bench, minimal form (sb13): machine directly on a 400 kV infinite bus.

No transformer, no bus elements, no governor: the machine's own VbaseLL is 400 kV, so
it sits straight on the source node. Mechanical torque from a `const` placed exactly
as PSCAD's own `sync_condensor.pscx` does it (const OUT port on the machine's `tmech`
port, body clear of every other port).
`machsw` and `Enab` are given as integers (1/1) so no start-up signals are needed -
also PSCAD's own condenser example style.

    machine.NS ---- source3.N3        (source N grounded)

Run: python bench_sb13.py sb13
"""
import sys

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
    return len(errs)


if PRJ in [p["name"] for p in P.app().projects()]:
    sys.exit("choose an unused project name")
P.create_project(PRJ, r"C:\PSCAD_work")

# ------------------------------------------------------------------ machine
r = P.add_component(PRJ, "master", "sync_machine", x=20, y=30)
m = r["iid"]
P.set_component_parameters(PRJ, m, {
    "Name": "SyncUnit1", "MVA": 300.0, "VbaseLL": 400.0, "H": 3.117,
    "OMO": 314.15926536, "icTyp": "POWERS", "P0": 60.0, "Q0": 0.0,
    "machsw": 1, "Enab": 1, "Iexc": "NO", "Igov": "NO", "Term": "NONE",
    "POut": "POUT", "QOut": "QOUT",
})
pm = ports(m)
log("ports:", {k: (v["x"], v["y"], v["dim"]) for k, v in pm.items()})
log("params:", {k: v for k, v in P.get_component_parameters(PRJ, m)["parameters"].items()
                if k in ("P0", "Q0", "VbaseLL", "MVA", "OMO", "machsw", "Enab", "Iexc", "Igov", "Term")})
if check("s0 machine alone"):
    sys.exit("stop at s0")

# ------------------------------------------------------------------ torque
c = P.add_component(PRJ, "master", "const", x=pm["tmech"]["x"] + 6, y=pm["tmech"]["y"] + 5,
                    parameters={"Value": 0.0})["iid"]
align(c, "OUT", (pm["tmech"]["x"], pm["tmech"]["y"]))
log("const bounds:", P.get_bounds(PRJ, [c])["bounds"], "tmech:", (pm["tmech"]["x"], pm["tmech"]["y"]))
if check("s1 +torque const"):
    sys.exit("stop at s1")

# ------------------------------------------------------------------ infinite bus
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
if check("s2 +source"):
    sys.exit("stop at s2")

# ------------------------------------------------------------------ channels
for i, nm in enumerate(("POUT", "QOUT", "Vinf")):
    lbl = P.add_component(PRJ, "master", "datalabel", x=40, y=40 + 4 * i)["iid"]
    P.set_component_parameters(PRJ, lbl, {"Name": nm})
    lp = ports(lbl)["A"]
    pgb = P.add_component(PRJ, "master", "pgb", x=47, y=40 + 4 * i)["iid"]
    align(pgb, "Signl", (lp["x"] + 3, lp["y"]))
    sp = ports(pgb)["Signl"]
    P.create_wire(PRJ, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
    P.set_component_parameters(PRJ, pgb, {"Name": nm, "UseSignalName": "YES"})

vm = P.add_component(PRJ, "master", "voltmetergnd", x=ns["x"] + 3, y=Y - 5)["iid"]
align(vm, "N1", (ns["x"] + 3, Y))
P.set_component_parameters(PRJ, vm, {"Name": "Vt"})
lbl = P.add_component(PRJ, "master", "datalabel", x=50, y=56)["iid"]
P.set_component_parameters(PRJ, lbl, {"Name": "Vt"})
lp = ports(lbl)["A"]
pgb = P.add_component(PRJ, "master", "pgb", x=57, y=56)["iid"]
align(pgb, "Signl", (lp["x"] + 3, lp["y"]))
sp = ports(pgb)["Signl"]
P.create_wire(PRJ, [[lp["x"], lp["y"]], [sp["x"], sp["y"]]])
P.set_component_parameters(PRJ, pgb, {"Name": "Vt", "UseSignalName": "YES"})

P.set_project_parameters(PRJ, {"time_step": 20.0, "time_duration": 3.0,
                               "sample_step": 200.0, "PlotType": "PSOUT"})
if check("s3 +channels"):
    sys.exit("stop at s3")
log("running 3 s ...")
P.run(PRJ, wait=True, poll=1.0, timeout=1800)
log("log tail:", P.output(PRJ, 200))
