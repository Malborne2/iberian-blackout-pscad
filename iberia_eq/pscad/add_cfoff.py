r"""Remove a tripped RES plant's filter capacitors from the grid (S30 sec 25, test 5). Project must not be loaded.

usage: python iberia_eq\pscad\add_cfoff.py --pscx <v2.pscx> [--sign 1]
Why: the plant trips by gate blocking; its three series Rf-Cf filter branches (master:rtcbranch, I = ICA/ICB/ICC) stay
on the bus (stage3 design note), so a tripped plant keeps exchanging 0.06-0.12 pu Q (bench rly_m0). In the event the
plants disconnected. A breaker per plant costs 63 nodes (168 + 63 > 200), so instead each phase gets a controlled
current source (master:src_ccin_1, Cntrl 1, 0 nodes) from the filter node to ground carrying sign * ICx * TRIP: after
a trip it supplies the filter current itself and the grid sees none. Before a trip it carries 0.
Placement: node label on the top port of each filter branch (orient 1: ports (x, y-1) = phase node, (x, y+1) = ground)
and the sources + multipliers in a free strip below the module's schematic.
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pscx_canvas import OfflineCanvas

ap = argparse.ArgumentParser(); ap.add_argument("--pscx", required=True); ap.add_argument("--sign", type=float, default=1.0); a = ap.parse_args()
cv = OfflineCanvas(a.pscx, canvas="RES_Plant")
if any(u.get("defn") == "master:src_ccin_1" for u in cv.main): raise SystemExit("add_cfoff: already applied")
caps = []
for u in cv.main:
    if u.get("defn") != "master:rtcbranch": continue
    P = {q.get("name"): q.get("value") for q in u.iter("param")}
    if P.get("C") == "Cf" and P.get("I"): caps.append((int(u.get("x")) // 18, int(u.get("y")) // 18, u.get("orient"), P["I"]))
if len(caps) != 3 or any(o != "1" for *_, o, _i in caps): raise SystemExit(f"add_cfoff: expected 3 vertical Cf branches, found {caps}")
y0 = max(int(u.get("y", 0)) for u in cv.main) // 18 + 8
for k, (x, y, _o, cur) in enumerate(caps):
    ph = cur[-1]                                                    # A / B / C
    cv.add_component("master", "nodelabel", x, y - 1, 0).parameters(Name=f"CFN_{ph}")
    xs = 10 + 16 * k
    m = cv.add_component("master", "mult", xs, y0, 0); P = m.ports()
    ins = [p for p in P if p not in ("OUT", "O")]; out = "OUT" if "OUT" in P else "O"
    cv.add_component("master", "datalabel", P[ins[0]].x, P[ins[0]].y, 0).parameters(Name=cur)
    cv.add_component("master", "datalabel", P[ins[1]].x, P[ins[1]].y, 0).parameters(Name="TRIP")
    cv.add_component("master", "datalabel", P[out].x, P[out].y, 0).parameters(Name=f"CFM_{ph}")
    if a.sign != 1.0:
        g = cv.add_component("master", "gain", xs, y0 + 4, 0); g.parameters(G=f"{a.sign}"); Q = g.ports()
        gi = [p for p in Q if p not in ("OUT", "O")][0]; go = "OUT" if "OUT" in Q else "O"
        cv.add_component("master", "datalabel", Q[gi].x, Q[gi].y, 0).parameters(Name=f"CFM_{ph}")
        cv.add_component("master", "datalabel", Q[go].x, Q[go].y, 0).parameters(Name=f"CFS_{ph}"); src_sig = f"CFS_{ph}"
    else:
        src_sig = f"CFM_{ph}"
    s = cv.add_component("master", "src_ccin_1", xs, y0 + 8, 0); s.parameters(Cntrl="1", f="50.0"); S = s.ports()
    cv.add_component("master", "nodelabel", S["A"].x, S["A"].y, 0).parameters(Name=f"CFN_{ph}")
    cv.add_component("master", "ground", S["B"].x, S["B"].y, 0)
    cv.add_component("master", "datalabel", S["Mag"].x, S["Mag"].y, 0).parameters(Name=src_sig)
cv.save(); print(f"{a.pscx}: filter-off current sources on {[c[3] for c in caps]}, sign {a.sign}, strip y = {y0}")
