"""Angle spread and France transfer stiffness of a solved pp_v2 state (RUNLOG S29 sec 11, pre-PSCAD review).

usage: python iberia_eq/pp_v2_angles.py <net.p>      (net.p from DUMP_NET=<net.p> on a pp_v2 / base_v2.py run)

Checks:
 - [FR] sec 1.4.2: "high transmission angle (around 80 deg between Carmona and S. Llogaia)" in the oscillation period.
   Carmona ~ WAN (Sevilla), S. Llogaia ~ CAT (HVDC end, Girona).
 - France AC tie stiffness: the AC ties' series reactance between the Spanish ends (N, CAT) and the French hub, and the
   steady-state transfer limit V^2/X over the ties alone. v1 (ib6) reproduced the separation with a Spain-France tie of
   76 ohm (RUNLOG S27 Batch 2); the committee gives 4,609 MW AC import at loss of synchronism ([CA] p.54).
"""
import sys, numpy as np, pandapower as pp

net = pp.from_pickle(sys.argv[1])
va = dict(zip(net.bus.name, net.res_bus.va_degree)); vm = dict(zip(net.bus.name, net.res_bus.vm_pu))
print(f"angle WAN (Carmona) - CAT (S.Llogaia): {va['WAN'] - va['CAT']:+.1f} deg   (report ~80 deg, oscillation period)")
print(f"angle spread of Spanish hubs: max {max(va[z] for z in va if z in ('GRA','WAN','BAD','CAC','SCE','MAD','CYL','NW','N','ARA','CAT','VAL','SE')) - min(va[z] for z in va if z in ('GRA','WAN','BAD','CAC','SCE','MAD','CYL','NW','N','ARA','CAT','VAL','SE')):.1f} deg; "
      f"FR hub {va['FR']:+.1f}, CAT {va['CAT']:+.1f}, N {va['N']:+.1f}, WAN {va['WAN']:+.1f}, BAD-TS {va['BAD-TS']:+.1f}")
ys = 0.0
for i_, n in zip(net.line.index, net.line.name):
    if "FR" in n:
        x = net.line.at[i_, "x_ohm_per_km"] * net.line.at[i_, "length_km"] / net.line.at[i_, "parallel"]
        ys += 1 / x
        print(f"   tie {n:8s} X {x:6.1f} ohm  P {net.res_line.at[i_, 'p_from_mw']:+7.0f} MW")
xt = 1 / ys
print(f"France AC ties in parallel: X {xt:.1f} ohm -> V^2/X = {400 ** 2 / xt:,.0f} MW (ties alone, French hub ideal; v1 total tie 76 ohm -> {400 ** 2 / 76:,.0f} MW)")
