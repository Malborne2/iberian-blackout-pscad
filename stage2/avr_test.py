"""sb14: does the AVR hold 1.0 pu if the machine carries less power?

The exciter wound the field to EF ~2.8 and the machine decelerated when VREF was forced
to 1.0 pu at 60 MW. That is the signature of a setpoint the machine cannot reach at that
tie reactance (X_machine ~1.0 pu + X_source 0.2 pu on 300 MVA).

Run: python avr_test.py sb14 <Torque> <P0>
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
TQ = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
P0 = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
P.connect()


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


objs = P.list_canvas_objects(PRJ)["objects"]
exc = [o for o in objs if o["defn_name"] == "master:excac_2016_2"][0]["iid"]
sandh = [o for o in objs if o["defn_name"] == "master:sandhdefn"][0]["iid"]
vref = ports(exc)["VREF"]
yhold = ports(sandh)["yhold"]

# drop the sandh link, put a const 1.0 on VREF instead
for o in P.list_canvas_objects(PRJ)["objects"]:
    if o["defn_name"].startswith("Wire"):
        l, t, r, b = o["bounds"]
        if min(l, r) <= vref["x"] <= max(l, r) and min(t, b) <= vref["y"] <= max(t, b) and t <= 2:
            P.delete_component(PRJ, o["iid"])
            print("removed VREF wire", o["bounds"])
c = P.add_component(PRJ, "master", "const", x=vref["x"] + 8, y=vref["y"] - 5, orient=2,
                    parameters={"Value": 1.0})["iid"]
align(c, "OUT", (vref["x"], vref["y"]))
print("VREF const 1.0, bounds", P.get_bounds(PRJ, [c])["bounds"])

m = [o for o in objs if o["defn_name"] == "master:sync_machine"][0]["iid"]
P.set_component_parameters(PRJ, m, {"P0": P0, "Q0": 0.0})
for o in objs:
    if o["defn_name"] == "master:const":
        p = ports(o["iid"])["OUT"]
        if (p["x"], p["y"]) == (13, 22):
            P.set_component_parameters(PRJ, o["iid"], {"Value": TQ})
            print("torque ->", TQ)
P.save(PRJ)
