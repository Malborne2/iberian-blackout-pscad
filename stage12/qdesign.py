"""AC load flow with load Q (QO, NQ) and an extra per-bus shunt dict; used to design the pre-event reactive balance.

usage: python stage12/qdesign.py <pscx> [--extra bus:Mvar,...]   (extra = absorbing Mvar at 1 pu, constant impedance)
Reuses acflow.py's network. Loads: P = 3PO*V^NP, Q = 3QO*V^NQ (per the pscx). Prints load-bus V, unit Q, collectors.
"""
import sys, argparse, numpy as np
import acflow as A

TRANCHE = {20: 1175.9, 8: 1669.1, 4: 1574.6, 16: 1523.9, 15: 1294.3, 24: 1267.1, 3: 1084.0, 21: 1084.0, 27: 588.0}


TAPS_S28 = {(29, 38): 1.0546, (12, 13): 1.006, (12, 11): 1.006, (19, 20): 1.06, (19, 33): 1.057, (20, 34): 0.9874,
            (10, 32): 1.07, (36, 23): 0.9385, (31, 6): 0.8571, (22, 35): 1.0671, (2, 30): 1.025, (25, 37): 1.025}


def solve(C, extra=None, v0=None, verbose=True, pg=None, ks=(1.0, 1.0), taps=None, caps=None):
    nb = 40; extra = extra or {}
    Y = np.zeros((nb, nb), complex)
    for k, (a, b) in A.LID.items():
        p = C[str(1600000000 + k)][1]
        z = ks[0] * complex(A.num(p["Rp1"]), A.W * A.num(p["Lp1"])) / A.ZB; bsh = ks[1] * A.W * A.num(p["Cp1"]) * 1e-6 * A.ZB; y = 1 / z
        Y[a, a] += y + 1j * bsh / 2; Y[b, b] += y + 1j * bsh / 2; Y[a, b] -= y; Y[b, a] -= y
    for i, (a, b) in A.XFB.items():
        p = C[i][1]; x = A.num(p["Xl"]) * A.SB / A.num(p["Tmva"]); y = 1 / complex(0, x)
        w1, w2, t = a, b, 1.0
        if taps:                                    # PSCAD TapI on winding 1: V_w1 = t * V_w2 (bench lt3, RUNLOG S27 sec 23)
            w1, w2 = next(k for k in taps if set(k) == {a, b}); t = taps[(w1, w2)]
        Y[w1, w1] += y / t ** 2; Y[w2, w2] += y; Y[w1, w2] -= y / t; Y[w2, w1] -= y / t
    for b, cuf in (caps or {}).items():             # shunt capacitors, uF per phase
        Y[b, b] += 1j * A.W * cuf * 1e-6 * A.ZB
    PL = np.zeros(nb); QL = np.zeros(nb); NP = np.ones(nb); NQ = np.ones(nb); QSH = np.zeros(nb); PPL = np.zeros(nb)
    for i, b in A.LOADB.items():
        p = C[i][1]; PL[b] += 3 * A.num(p["PO"]) / A.SB; QL[b] += 3 * A.num(p.get("QO", 0)) / A.SB
        NP[b] = A.num(p.get("NP", 1)); NQ[b] = A.num(p.get("NQ", 1))
    for b, q in extra.items(): QSH[b] += q / A.SB
    GSH = np.zeros(nb)   # LFDD tranches + pump loads: resistive varrlc, P_k at 1 pu (V^2)
    for b, pmw in TRANCHE.items(): GSH[b] += pmw / A.SB
    QR = np.zeros(nb)    # existing reactor fixed_loads (constant Q, NQ 0)
    for i, b in A.REACB.items(): QR[b] += 3 * A.num(C[i][1]["QO"]) / A.SB
    for rid, pid in A.RAMP.items():
        PPL[A.PLANTB[pid]] += A.num(C[rid][1]["Y2"]) * A.num(C[pid][1]["Sbase"]) / A.SB
    kpf = A.num(C["2127906943"][1]["Kpf"])
    PG = np.zeros(nb); VS = {}
    for i, b in A.UNITB.items():
        PG[b] = (pg[b] if pg and b in pg else A.num(C[i][1]["P0"])) / A.SB; VS[b] = A.num(C[i][1]["V0"]) if v0 is None else v0.get(b, A.num(C[i][1]["V0"]))
    PG[9] -= 1000.0 / A.SB; VS[39] = 1.02
    pq = [b for b in range(1, nb) if b not in VS]; ia = [b for b in range(1, nb) if b != 39]
    V = np.ones(nb); th = np.zeros(nb)
    for b, v in VS.items(): V[b] = v

    def mis(t2, v2):
        Vc = v2 * np.exp(1j * t2); S = Vc * np.conj(Y @ Vc)
        P = PG - PL * v2 ** NP - GSH * v2 ** 2 + PPL * v2; Q = -QSH * v2 ** 2 - QR - QL * v2 ** NQ + kpf * PPL * v2
        return S, P - S.real, Q - S.imag
    for it in range(50):
        _, dP, dQ = mis(th, V); m = np.concatenate([dP[ia], dQ[pq]])
        if np.max(np.abs(m)) < 1e-8: break
        x0 = np.concatenate([th[ia], V[pq]]); J = np.zeros((len(x0), len(x0))); h = 1e-6

        def f(x):
            t2 = th.copy(); v2 = V.copy(); t2[ia] = x[:len(ia)]; v2[pq] = x[len(ia):]
            _, a, b = mis(t2, v2); return np.concatenate([a[ia], b[pq]])
        f0 = f(x0)
        for j in range(len(x0)):
            xx = x0.copy(); xx[j] += h; J[:, j] = (f(xx) - f0) / h
        x0 = x0 - np.linalg.solve(J, f0); th[ia] = x0[:len(ia)]; V[pq] = x0[len(ia):]
    S, _, _ = mis(th, V)
    Qg = (S.imag + QSH * V ** 2 + QR + QL * V ** NQ - kpf * PPL * V) * A.SB
    res = dict(V=V, th=th, Pinj=S.real * A.SB, Y=Y, Qg=Qg, it=it, QL=QL * V ** NQ * A.SB, QSH=QSH * V ** 2 * A.SB, Qpl=kpf * PPL * V * A.SB)
    if verbose:
        print(f"it {it}; units Q: " + " ".join(f"{b}:{Qg[b]:+.0f}" for b in (30, 31, 32, 37, 39)) +
              f"  Iberian sum {sum(Qg[b] for b in (30,31,32,37)):+.0f}")
        print("loads V: " + " ".join(f"{b}:{V[b]:.3f}" for b in sorted(set(A.LOADB.values())) if b != 39))
        print("collectors: " + " ".join(f"{b}:{V[b]:.4f}" for b in (33, 34, 35, 36, 38)) +
              "   HV 19/20/22/23/29: " + " ".join(f"{V[b]:.3f}" for b in (19, 20, 22, 23, 29)))
        print(f"tie(1-39,9-39) see slack; slack P {(S.real[39] + PL[39]*V[39]**NP[39])*A.SB:.0f}"); print(f"absorbed: loads {res['QL'].sum():.0f}, shunts {res['QSH'].sum():.0f}, plants {-res['Qpl'].sum():.0f} Mvar")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("pscx"); ap.add_argument("--extra", default=""); ap.add_argument("--pg", default="32:3800,37:3200,30:3400,31:3600")
    a = ap.parse_args()
    ex = {int(k): float(v) for k, v in (x.split(":") for x in a.extra.split(",") if x)}
    pg = {int(k): float(v) for k, v in (x.split(":") for x in a.pg.split(",") if x)}
    solve(A.load_case(a.pscx), ex, pg=pg)
