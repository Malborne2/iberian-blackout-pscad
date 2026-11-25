"""sb18 = sb17 with the example's real start-up sequence (source -> machine).

PLAN F2 / Stage 2 requires the start-up of `sync_exciter_governor.pscx` exactly:
the machine runs as a **source** at (P0, Q0, VT, Pheta) and at `S2M` becomes a real
machine; `Enab` (lock-rotor -> normal) follows `LRR`; the exciter's `INIT` is held at 0
(it adopts `EFD0` from the machine's `efo`) until `InitEx`, then regulates.

sb17 starts in machine mode at t = 0 (machsw = 1, Enab = 1), which shows up as a hard
start: POUT 0.86 pu at t = 0.05 s, speed 311 rad/s, and Q creeping for seconds.
This script changes only the start-up:

    machsw = "S2M"  <- timerdefn 0.500 s
    Enab   = "LRR"  <- timerdefn 0.600 s
    ExInit: already time-sig -> upramp(0.50 .. 0.51 s) -> exc.INIT

Run: python sb18_startup.py
"""
import sys
import time

import pscad_ops as P

SRC = "sb17"
DST = "sb18"
P.connect()

names = [p["name"] for p in P.app().projects()]
if DST in names:
    sys.exit(f"{DST} is already loaded — choose a fresh name or unload it first")

print("save_as:", P.save_as(SRC, DST, folder=r"C:\PSCAD_work"))
time.sleep(1.0)


def ports(iid, prj=DST):
    return {p["name"]: p for p in P.get_ports(prj, iid)["ports"]}


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


def check(tag):
    P.save(DST)
    P.app().project(DST).clean()
    P.app().project(DST).build()
    errs = [x["text"] for x in P.messages(DST)["messages"] if x["status"].startswith("error")]
    d = P.build_dimensions(DST).get("dimensions") or {}
    print(f"[{tag}] errors={len(errs)} NODES={d.get('NODES')} NPAGES={d.get('NPAGES')} "
          f"SUBSYS={d.get('SUBSYS')} BRANCHES={d.get('BRANCHES')} PGBS={d.get('PGBS')}")
    for t in errs[:8]:
        print("     E:", t.encode("ascii", "replace").decode())
    if errs:
        sys.exit("stop at " + tag)


objs = P.list_canvas_objects(DST)["objects"]
machine = [o for o in objs if o["defn_name"] == "master:sync_machine"][0]["iid"]

# ---------------------------------------------------------------- publish S2M / LRR
def publish(name, t_sw, x, y):
    """timerdefn -> datalabel with Name = signal name (a name binding source)."""
    t = P.add_component(DST, "master", "timerdefn", x=x, y=y, parameters={"Timsw": t_sw})["iid"]
    iout = ports(t)["iout"]
    lbl = P.add_component(DST, "master", "datalabel", x=iout["x"] + 5, y=iout["y"] + 5)["iid"]
    align(lbl, "A", (iout["x"], iout["y"]))
    P.set_component_parameters(DST, lbl, {"Name": name})
    prm = P.get_component_parameters(DST, lbl)["parameters"]
    print(f"  {name}: timer at {t_sw} s, datalabel Name={prm.get('Name')} at "
          f"{(iout['x'], iout['y'])}")


publish("S2M", 0.50, 4, 4)
publish("LRR", 0.60, 4, 9)
check("s1 S2M/LRR published")

# ---------------------------------------------------------------- bind them to the machine
P.set_component_parameters(DST, machine, {"machsw": "S2M", "Enab": "LRR"})
prm = P.get_component_parameters(DST, machine)["parameters"]
print("machine machsw =", prm.get("machsw"), " Enab =", prm.get("Enab"),
      " Iexc =", prm.get("Iexc"), " P0 =", prm.get("P0"), " Q0 =", prm.get("Q0"),
      " VT =", prm.get("VT"), " Pheta =", prm.get("Pheta"))
check("s2 machsw/Enab bound")

P.set_project_parameters(DST, {"time_step": 20.0, "time_duration": 20.0,
                               "sample_step": 20.0, "PlotType": "PSOUT"})
check("s3 params")
print("running 20 s ...")
P.run(DST, wait=True, poll=1.0, timeout=3600)
print("log tail:", P.output(DST, 200))
