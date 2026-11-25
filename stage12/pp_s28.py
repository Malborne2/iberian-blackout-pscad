"""pandapower model of an ib6-family case (default s28), compared with its measured EMT settle.

usage: python stage12/pp_s28.py [pscx] [--cscale k] [--lscale k]
Same reading of the .pscx as acflow.py/qdesign.py (maps LID/XFB/LOADB/REACB/UNITB/PLANTB/RAMP):
  lines      pi_section Rp1 [ohm], Lp1 [H], Cp1 [uF], length 1 (km)  -> create_line_from_parameters
  xfmrs      Xl [pu on Tmva]                                        -> create_impedance (pure reactance)
  loads      P = 3 PO V^NP, Q = 3 QO V^NQ (NP 1 -> const-current)    -> load, const_i / const_z percent
  tranches   LFDD + pump varrlc, V^2                                -> load, const_z 100 %
  plants     P = Pref Sbase V, Q = Kpf P (absorbing)                -> negative load, const_i 100 %
  reactors   fixed_load QO, NQ 0 (constant Q)                        -> load q
  HVDC       1000 MW out of bus 9                                    -> load
  units      PV at V0 with the MEASURED s28 P (26-28 s means)        -> gen
  France     slack at 1.02 pu on bus 39
"""
import sys, argparse, numpy as np, pandapower as pp
sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import acflow as A
from qdesign import TRANCHE

ap = argparse.ArgumentParser(); ap.add_argument("pscx", nargs="?", default=r"C:\PSCAD_work\s28\ib6.pscx")
ap.add_argument("--cscale", type=float, default=1.0); ap.add_argument("--lscale", type=float, default=1.0); ap.add_argument("--resq", type=float, default=1.0); ap.add_argument("--measured", action="store_true"); ap.add_argument("--taps", action="store_true"); ap.add_argument("--tapinv", action="store_true"); ap.add_argument("--tapk", type=float, default=1.0)
a = ap.parse_args()
C = A.load_case(a.pscx)
EMT_VL = {3: 1.139, 4: 1.159, 7: 1.165, 8: 1.164, 12: 1.162, 15: 1.153, 16: 1.148, 18: 1.147, 20: 1.056, 21: 1.147,
          23: 1.142, 24: 1.148, 25: 1.114, 26: 1.153, 27: 1.154, 28: 1.143, 29: 1.131, 31: 1.032}
EMT_Q = {32: -2356, 37: -2398, 30: -2091, 31: 1960}
PG = {32: 3900, 37: 3330, 30: 3460, 31: 3770}
PGM = {32: 4195, 37: 3600, 30: 3367, 31: 4159}          # s28 settle 26-28 s (settle_read.py)
VITM = {32: 1.032, 37: 1.035, 30: 1.051, 31: 1.032}

net = pp.create_empty_network(f_hz=50, sn_mva=100)
B = {b: pp.create_bus(net, vn_kv=400, name=str(b)) for b in range(1, 40)}
for k, (fa, fb) in A.LID.items():
    p = C[str(1600000000 + k)][1]
    pp.create_line_from_parameters(net, B[fa], B[fb], length_km=1, r_ohm_per_km=a.lscale * A.num(p["Rp1"]),
                                   x_ohm_per_km=a.lscale * A.W * A.num(p["Lp1"]),
                                   c_nf_per_km=a.cscale * A.num(p["Cp1"]) * 1e3, max_i_ka=99, name=f"L{fa}-{fb}")
# EMT tap signals (TapI, winding 1), read from the s28 Main.f TRTAP5 calls and Main.dta TRANSFORMERS order
# (RUNLOG S27 sec 23): (winding-1 bus, winding-2 bus) -> tap
TAPS = {(29, 38): 1.0546, (12, 13): 1.006, (12, 11): 1.006, (19, 20): 1.06, (19, 33): 1.057, (20, 34): 0.9874,
        (10, 32): 1.07, (36, 23): 0.9385, (31, 6): 0.8571, (22, 35): 1.0671, (2, 30): 1.025, (25, 37): 1.025}
for i, (fa, fb) in A.XFB.items():
    p = C[i][1]; sn = A.num(p["Tmva"]); x = A.num(p["Xl"])
    if not a.taps:
        pp.create_impedance(net, B[fa], B[fb], rft_pu=0, xft_pu=x, sn_mva=sn, name=f"T{fa}-{fb}"); continue
    w1, w2 = next(k for k in TAPS if set(k) == {fa, fb}); t = TAPS[(w1, w2)]
    if a.tapinv: t = 1.0 / t
    # winding 1 = "hv" side with a tap changer; ratio V_w1/V_w2 = t (PSCAD convention, bench lt3)
    pp.create_transformer_from_parameters(net, B[w1], B[w2], sn_mva=sn, vn_hv_kv=400.0, vn_lv_kv=400.0, vk_percent=100 * x,
                                          vkr_percent=0, pfe_kw=0, i0_percent=0, tap_side="hv", tap_neutral=0,
                                          tap_min=-100, tap_max=100, tap_step_percent=100 * (t - 1), tap_pos=1,
                                          tap_changer_type="Ratio", name=f"T{w1}-{w2}")
if a.taps:   # the two capacitors in the EMT build (Main.dta): Bus5 10.029 uF, Bus4 5.014 uF per phase
    for b, cuf in ((5, 10.029), (4, 5.014)):
        pp.create_shunt(net, B[b], q_mvar=-A.W * cuf * 1e-6 * 400 ** 2, p_mw=0, name=f"C{b}")
for i, b in A.LOADB.items():
    p = C[i][1]; NP = A.num(p.get("NP", 1)); NQ = A.num(p.get("NQ", 1))
    pz = 100 if NP == 2 else 0; pi = 100 if NP == 1 else 0
    pp.create_load(net, B[b], p_mw=3 * A.num(p["PO"]), q_mvar=3 * A.num(p.get("QO", 0)),
                   const_i_p_percent=pi, const_z_p_percent=pz,
                   const_i_q_percent=100 if NQ == 1 else 0, const_z_q_percent=100 if NQ == 2 else 0, name=f"LD{b}")
for b, pmw in TRANCHE.items():
    pp.create_load(net, B[b], p_mw=pmw, q_mvar=0, const_z_p_percent=100, name=f"TR{b}")
for i, b in A.REACB.items():
    pp.create_load(net, B[b], p_mw=0, q_mvar=3 * A.num(C[i][1]["QO"]), name=f"SR{b}")
kpf = A.num(C["2127906943"][1]["Kpf"]); PPL = {}
for rid, pid in A.RAMP.items():
    b = A.PLANTB[pid]; PPL[b] = PPL.get(b, 0) + A.num(C[rid][1]["Y2"]) * A.num(C[pid][1]["Sbase"])
for b, pw in PPL.items():
    pp.create_load(net, B[b], p_mw=-pw, q_mvar=-a.resq * kpf * pw, const_i_p_percent=100, const_i_q_percent=100, name=f"RES{b}")
pp.create_load(net, B[9], p_mw=1000, q_mvar=0, name="HVDC")
for i, b in A.UNITB.items():
    pp.create_gen(net, B[b], p_mw=(PGM if a.measured else PG)[b], vm_pu=(VITM[b] if a.measured else A.num(C[i][1]["V0"])), name=f"U{b}")
pp.create_ext_grid(net, B[39], vm_pu=1.022 if a.measured else 1.02, name="France")
if a.taps:
    pp.runpp(net, voltage_depend_loads=True, max_iteration=50)
else:
    pp.runpp(net, voltage_depend_loads=True, max_iteration=50)
V = net.res_bus.vm_pu.values; vb = lambda b: V[B[b]]
print(f"pandapower converged={net.converged}  cscale {a.cscale} lscale {a.lscale} resq {a.resq}")
print(f"{'bus':>4s} {'EMT':>6s} {'pp':>6s} {'diff':>7s}")
d = []
for b, v in EMT_VL.items():
    d.append(vb(b) - v); print(f"{b:4d} {v:6.3f} {vb(b):6.3f} {vb(b) - v:+7.3f}")
print(f"RMS diff {np.sqrt(np.mean(np.square(d))):.3f} pu")
qg = net.res_gen.q_mvar.values
for j, (i, b) in enumerate(A.UNITB.items()):
    print(f"unit {b}: Q pp {qg[j]:+7.0f}  EMT {EMT_Q[b]:+6.0f} Mvar")
print(f"slack (France) P {net.res_ext_grid.p_mw.iloc[0]:.0f} MW, Q {net.res_ext_grid.q_mvar.iloc[0]:.0f} Mvar; "
      f"line charging at solution {-net.res_line.ql_mvar.sum():.0f} Mvar (losses-Q sign: negative = generated)")
