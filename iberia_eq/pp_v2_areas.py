"""Flows between the Fig 2-41 areas (N / SW / E) and the borders in a solved pp_v2 net (RUNLOG S28 sec 2).

usage: DUMP_NET=net.p python iberia_eq/pp_v2.py ...; python iberia_eq/pp_v2_areas.py net.p
Zone -> area as in pp_v2 REG_AREA by zone (VAL / SE hold parts of SW-area regions, so E is approximate).
"""
import pandapower as pp, numpy as np, sys
net = pp.from_pickle(sys.argv[1]); bn = net.bus.name
AREA = {"N": ["CYL","NW","N","ARA","PS-CYL","PS-ARA"], "SW": ["GRA","WAN","BAD","CAC","SCE","MAD","BAD-TS","WAN-TS"], "E": ["CAT","VAL","SE"]}
z2a = {z: A for A, zs in AREA.items() for z in zs}
def area(b):
    n = bn[b]
    if n.endswith(" term"): return None
    return z2a.get(n, n)
flows = {}
for i in net.line.index:
    fa, ta = area(net.line.from_bus[i]), area(net.line.to_bus[i])
    if fa != ta:
        flows[(fa, ta)] = flows.get((fa, ta), 0) + net.res_line.p_from_mw[i]
        flows[(ta, fa)] = flows.get((ta, fa), 0) + net.res_line.p_to_mw[i]
print("inter-area/external flows (MW, from->to):")
for k, v in sorted(flows.items()):
    if v > 0: print(f"  {k[0]:>5s} -> {k[1]:<5s} {v:7.0f}")
for A in AREA:
    out = sum(v for (a, b), v in flows.items() if a == A)
    print(f"  net export of {A}: {out:7.0f}")
print("line P losses MW:", round(net.res_line.pl_mw.sum()), " trafo:", round(net.res_trafo.pl_mw.sum()))
es_bus = [b for b in net.bus.index if area(b) in AREA]
print("Spain line losses (lines touching Spain):", round(net.res_line.pl_mw[net.line.from_bus.isin(es_bus) | net.line.to_bus.isin(es_bus)].sum()))
