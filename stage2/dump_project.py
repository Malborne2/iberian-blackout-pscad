"""Dump every object of a project canvas: bounds, ports, parameters -> JSON."""
import json
import sys

import pscad_ops as P

proj = sys.argv[1] if len(sys.argv) > 1 else "sync_exciter_governor"
canvas = sys.argv[2] if len(sys.argv) > 2 else "Main"
out = sys.argv[3] if len(sys.argv) > 3 else f"dump_{proj}.json"

P.connect()
objs = P.list_canvas_objects(proj, canvas)["objects"]
data = []
for o in objs:
    rec = {"iid": o["iid"], "defn": o["defn_name"], "bounds": o["bounds"]}
    if not o["defn_name"].startswith("Wire"):
        try:
            rec["ports"] = P.get_ports(proj, o["iid"], canvas)["ports"]
        except Exception as e:
            rec["ports_error"] = str(e)
        try:
            rec["params"] = P.get_component_parameters(proj, o["iid"], canvas)["parameters"]
        except Exception as e:
            rec["params_error"] = str(e)
    data.append(rec)

with open(out, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=1, default=str)
print("wrote", out, "objects", len(data))
