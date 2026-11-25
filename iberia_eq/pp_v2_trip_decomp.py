"""Decomposition of the static 4a+4b (727 MW at BAD-TS) voltage rise of a solved pp_v2 net (RUNLOG S28 sec 5).

usage: python iberia_eq/pp_v2_trip_decomp.py net.p
Cases: base (P + Q), P only, Q only, constant-power loads, DSO shunts as constant Q, both, units stiff (vk 2 %).
"""
import numpy as np, pandapower as pp, warnings, sys; warnings.filterwarnings("ignore")
def run(mode):
    net = pp.from_pickle(sys.argv[1]); B = {n: i for i, n in zip(net.bus.index, net.bus.name)}
    pp.runpp(net, init="results")
    LD = net.load.index[net.load.name.str.startswith("Load")]
    v0 = net.res_bus.vm_pu[net.load.bus[LD]].values
    al, be = (0.0, 0.0) if "constload" in mode else (0.8, 4.1)
    P0 = net.load.p_mw[LD].values / v0**al; Q0 = net.load.q_mvar[LD].values / v0**be
    if "constdso" in mode:   # DSO shunts -> constant Q injections at their solved value
        for i in net.shunt.index[net.shunt.name.str.startswith("Qdso")]:
            q = net.res_shunt.q_mvar[i]; pp.create_sgen(net, net.shunt.bus[i], p_mw=0, q_mvar=-q, name="cq"); net.shunt.at[i, "in_service"] = False
    if "stiffunits" in mode:  # unit connection reactance 20 % -> 2 %, set-point re-solved to the same Q
        for i in net.trafo.index[net.trafo.name.str.startswith("T G")]: net.trafo.at[i, "vk_percent"] = 2.0
        pp.runpp(net, init="results")
        # restore same hub voltages by moving gen set-points: iterate
        tgt = {g: net.res_bus.vm_pu[net.trafo.hv_bus[net.trafo.index[net.trafo.lv_bus == net.gen.bus[g]][0]]] for g in net.gen.index}
    if "noflowrelief" in mode: pass
    def solve():
        for _ in range(30):
            pp.runpp(net, init="results")
            v = net.res_bus.vm_pu[net.load.bus[LD]].values
            p, q = P0*v**al, Q0*v**be
            d = max(abs(p-net.load.p_mw[LD].values).max(), abs(q-net.load.q_mvar[LD].values).max())
            net.load.loc[LD,"p_mw"] = p; net.load.loc[LD,"q_mvar"] = q
            if d < 0.02: return
    solve(); base = net.res_bus.vm_pu.copy()
    i = [k for k in net.sgen.index if net.sgen.bus[k]==B["BAD-TS"] and net.sgen.name[k].startswith("RES")][0]
    if "ponly" in mode: net.sgen.at[i,"p_mw"] -= 727
    elif "qonly" in mode: net.sgen.at[i,"q_mvar"] += 0.135*727
    else: net.sgen.at[i,"p_mw"] -= 727; net.sgen.at[i,"q_mvar"] += 0.135*727
    solve(); dv = (net.res_bus.vm_pu-base)*400
    print(f"{mode:22s} BAD-TS {dv[B['BAD-TS']]:+6.2f}  BAD {dv[B['BAD']]:+6.2f}  MAD {dv[B['MAD']]:+6.2f}  CAT {dv[B['CAT']]:+6.2f}  max {dv.max():+6.2f} kV")
for m in ["base","ponly","qonly","constload","constdso","constload+constdso","stiffunits"]: run(m)
