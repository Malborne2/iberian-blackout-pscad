"""Unit reactive power at the generator terminal vs at the 400 kV connection point, and the step-up absorption.

usage: python iberia_eq/pp_v2_unitq_side.py <net.p>      (net.p from DUMP_NET=<net.p> on any pp_v2 run)

Why (RUNLOG S29 sec 5): [FR] Figs 2-84..2-86 aggregate unit Q of plants "connected to the Spanish transmission network"
against the P.O. 7.4 reference, which is defined on the 400 kV voltage band (405-410 kV) -- i.e. at the connection
point [inf]. pp_v2 compares the *terminal* Q (res_gen) with them. The difference is the step-up I2X, which depends on
the connection reactance (vkg). This script shows how large that difference is now (vkg as fitted) and what it would be
with a realistic step-up of 15 % at the same loading.
"""
import sys, numpy as np, pandapower as pp

net = pp.from_pickle(sys.argv[1])
rows = []
for i_, n in zip(net.trafo.index, net.trafo.name):
    if not (n.startswith("T G") or n.startswith("T Morocco")): continue
    g = n[2:]
    gi = net.gen.index[net.gen.name == g]
    if len(gi) == 0: continue
    q_term = net.res_gen.at[gi[0], "q_mvar"]
    q_hv = -net.res_trafo.at[i_, "q_hv_mvar"]            # Q delivered into the 400 kV bus (+ = generating)
    i2x = q_term - q_hv
    s = net.trafo.at[i_, "sn_mva"]; vk = net.trafo.at[i_, "vk_percent"]
    sload = np.hypot(net.res_gen.at[gi[0], "p_mw"], q_term)
    i2x15 = (sload / s) ** 2 * 0.15 * s                   # same loading, 15 % reactance (V ~ 1 pu)
    rows.append((g, net.res_gen.at[gi[0], "p_mw"], vk, q_term, q_hv, i2x, i2x15))
print(f"{'unit':22s} {'P':>6s} {'vk%':>5s} {'Q term':>7s} {'Q 400kV':>8s} {'I2X now':>8s} {'I2X@15%':>8s}")
for r in rows: print(f"{r[0]:22s} {r[1]:6.0f} {r[2]:5.1f} {r[3]:+7.0f} {r[4]:+8.0f} {r[5]:8.0f} {r[6]:8.0f}")
sp = [r for r in rows if r[0].split()[0] in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")]
print(f"Spanish units G1-G7: sum Q terminal {sum(r[3] for r in sp):+.0f}, at 400 kV {sum(r[4] for r in sp):+.0f} Mvar; "
      f"step-up I2X now {sum(r[5] for r in sp):.0f}, at 15 % {sum(r[6] for r in sp):.0f} Mvar")
