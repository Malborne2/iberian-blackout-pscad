"""Static trip-sensitivity check of a solved pp_v2 state (RUNLOG S28) -- cheap pre-PSCAD gate for the reactive balance.

usage: DUMP_NET=net.p python iberia_eq/pp_v2.py ...   (saves the solved net), then
       python iberia_eq/pp_v2_trip.py net.p [--alpha 0.8 --beta 4.1 --kpf -0.135]

What it does: removes a tripping plant (P and its fixed-PF Q absorption, Q/P = kpf) from the solved state, re-solves with
the exponential loads iterated and the units holding their terminal set-points (AVR, static), and prints dV at the hubs.
Cases (cumulative, as in the report, no other trips between them):
  E3   Granada 355 MW at GRA                              ([FR] Table 3-3)
  E4   + Badajoz 4a 582 + 4b 145 = 727 MW at BAD-TS        ([FR] Table 3-3)
Report checks:
  - after 4a+4b the 400 kV maximum rose +4.9 kV (+0.012 pu)   (Fig 3-7a, RUNLOG S27 sec 21)
  - dV ~ dQ / S_sc at Bienvenida: 727 MW x 0.135 = 98 Mvar / 8,386 MVA = +0.012 pu (Table 4-26)
  - Granada trip: 3-7 kV per 165 Mvar of absorption lost = 18-42 kV/Gvar (RUNLOG S27 sec 9, r3)
Static only: no relay, no slow drift (event 1/2 drivers), no AVR dynamics, no Q(V) of the plants.
"""
import argparse, numpy as np, pandapower as pp, warnings
warnings.filterwarnings("ignore")
ap = argparse.ArgumentParser(); ap.add_argument("net"); ap.add_argument("--alpha", type=float, default=0.8)
ap.add_argument("--beta", type=float, default=4.1); ap.add_argument("--kpf", type=float, default=-0.135)
a = ap.parse_args()
net = pp.from_pickle(a.net); B = {n: i for i, n in zip(net.bus.index, net.bus.name)}
pp.runpp(net, init="results")
LD = net.load.index[net.load.name.str.startswith("Load")]
v0 = net.res_bus.vm_pu[net.load.bus[LD]].values
P0 = net.load.p_mw[LD].values / v0 ** a.alpha; Q0 = net.load.q_mvar[LD].values / v0 ** a.beta


def solve():
    for _ in range(30):
        pp.runpp(net, init="results")
        v = net.res_bus.vm_pu[net.load.bus[LD]].values
        p, q = P0 * v ** a.alpha, Q0 * v ** a.beta
        d = max(abs(p - net.load.p_mw[LD].values).max(), abs(q - net.load.q_mvar[LD].values).max())
        net.load.loc[LD, "p_mw"] = p; net.load.loc[LD, "q_mvar"] = q
        if d < 0.02: return


def sgen_at(bus):
    return [i for i in net.sgen.index if net.sgen.bus[i] == B[bus] and net.sgen.name[i].startswith("RES")][0]


solve()
HUBS = ["GRA", "WAN", "WAN-TS", "BAD", "BAD-TS", "CAC", "SCE", "MAD", "VAL", "SE", "CYL", "N", "CAT", "PT-S", "PT-N"]
base = net.res_bus.vm_pu.copy(); qg0 = net.res_gen.q_mvar.sum(); fr0 = net.res_ext_grid.p_mw.iloc[0]
out = {}
for tag, bus, mw in (("E3 Granada 355", "GRA", 355.0), ("E4 +Badajoz 727", "BAD-TS", 727.0)):
    i = sgen_at(bus); net.sgen.at[i, "p_mw"] -= mw; net.sgen.at[i, "q_mvar"] -= a.kpf * mw
    solve(); out[tag] = (net.res_bus.vm_pu - base) * 400
    print(f"{tag:16s}: units dQ {net.res_gen.q_mvar.sum() - qg0:+6.0f} Mvar, France slack dP {net.res_ext_grid.p_mw.iloc[0] - fr0:+6.0f} MW, "
          f"absorption removed so far {-a.kpf * (355 + (727 if 'E4' in tag else 0)):.0f} Mvar")
print("dV [kV] vs pre-event:  " + "".join(f"{h:>8s}" for h in HUBS))
for tag, dv in out.items():
    print(f"  {tag:20s}" + "".join(f"{dv[B[h]]:+8.2f}" for h in HUBS))
dv4 = out["E4 +Badajoz 727"] - out["E3 Granada 355"]
print(f"  {'4a+4b alone':20s}" + "".join(f"{dv4[B[h]]:+8.2f}" for h in HUBS))
es = [B[h] for h in HUBS if not h.startswith("PT")]
print(f"\ncheck 4a+4b: max Spanish 400 kV rise {dv4[es].max():+.2f} kV at {net.bus.name[dv4[es].idxmax()]} (report +4.9 kV, Fig 3-7a); "
      f"BAD-TS {dv4[B['BAD-TS']]:+.2f} kV (dQ/S_sc estimate +4.7 kV)")
print(f"check E3: GRA {out['E3 Granada 355'][B['GRA']]:+.2f} kV for {-a.kpf * 355:.0f} Mvar -> "
      f"{out['E3 Granada 355'][B['GRA']] / (-a.kpf * 355) * 1000:.0f} kV/Gvar (report 18-42 kV/Gvar)")
