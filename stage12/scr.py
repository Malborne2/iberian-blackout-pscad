"""Short-circuit ratio at the collector buses: Zth from the network Y-bus with each synchronous
machine as Xd''=0.135 pu (own Sbase) behind its bus, France 200 GVA Xd''; loads ignored.
SCR = S_sc / (Sbase of the plants on that bus).  usage: scr.py <pscx> [xfmr_k] [kplant]"""
import sys, numpy as np
sys.path.insert(0, 'stage12'); import acflow as A
C = A.load_case(sys.argv[1]); xk = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
kpl = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
kl = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0   # extra line+xfmr admittance factor (not ties)
nb = 40; Y = np.zeros((nb, nb), complex)
for k, (a, b) in A.LID.items():
    p = C[str(1600000000 + k)][1]; z = complex(A.num(p['Rp1']), A.W * A.num(p['Lp1'])) / A.ZB
    y = (1 if 39 in (a, b) else kl) / z; Y[a, a] += y; Y[b, b] += y; Y[a, b] -= y; Y[b, a] -= y
COLL = {(19, 33), (20, 34), (22, 35), (23, 36), (29, 38)}
for i, (a, b) in A.XFB.items():
    p = C[i][1]; x = A.num(p['Xl']) * A.SB / A.num(p['Tmva'])
    if (a, b) in COLL: x /= xk
    y = kl / complex(0, x); Y[a, a] += y; Y[b, b] += y; Y[a, b] -= y; Y[b, a] -= y
SBU = {30: 6113, 31: 13548, 32: 15292, 37: 12838, 39: 200000}
for b, s in SBU.items(): Y[b, b] += 1 / complex(0, 0.135 * A.SB / s)
Z = np.linalg.inv(Y[1:, 1:])
SPL = {33: 3835, 34: 4614, 35: 4212, 36: 3563, 38: 5290}
for b, s in SPL.items():
    ssc = A.SB / abs(Z[b - 1, b - 1])
    print(f"bus {b}: Ssc {ssc:8.0f} MVA  plants {s*kpl:6.0f} MVA  SCR {ssc/(s*kpl):5.2f}")
