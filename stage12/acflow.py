"""AC Newton power flow of an ib6-style case, read straight from the .pscx.

Models what EMTDC will see at steady state:
  lines  : pi_section Rp1 [ohm], Lp1 [H], Cp1 [uF] (total, half at each end)  -- ids mapped to buses below
  xfmrs  : Xl [pu on Tmva, 400 kV], no R, tap 1
  loads  : fixed_load P = 3*PO * V (NP=1), Q = 0; shunt reactors Q = 3*QO constant (NQ=0)
  plants : P = Pref*Sbase*V (current-controlled), Q = Kpf*P   (Kpf = -0.17518, absorbing)
  HVDC   : P = -1000 MW at bus 9, Q = 0
  units  : PV at V0 with their P0; France (bus 39 side) = slack at 1.02
usage: python stage12/acflow.py <pscx> [--sh K]   (K scales every shunt reactor)
"""
import sys, re, argparse, numpy as np, xml.etree.ElementTree as ET

LID = {0:(13,14),3:(17,18),6:(23,24),9:(10,11),12:(10,13),15:(14,15),18:(15,16),21:(16,17),24:(16,19),
 27:(16,21),30:(16,24),33:(17,27),36:(1,2),39:(1,39),42:(21,22),45:(22,23),48:(25,26),51:(26,27),
 54:(26,28),57:(26,29),60:(28,29),63:(2,25),66:(2,3),69:(3,18),72:(3,4),75:(4,14),78:(4,5),81:(5,6),
 84:(5,8),87:(6,11),90:(6,7),93:(7,8),96:(8,9),99:(9,39)}
XFB = {"1618177572":(29,38),"81838474":(12,13),"2134729376":(12,11),"143711642":(19,20),
       "790392911":(19,33),"1726223889":(20,34),"1327473079":(10,32),"1798631683":(23,36),
       "1341896340":(6,31),"807978177":(22,35),"170974727":(2,30),"2050788591":(25,37)}
LOADB = {"744210529":3,"1004648478":7,"1522722771":8,"1862156076":12,"914258219":15,"1925407754":16,
 "1087233095":18,"2071274910":20,"775660433":21,"553408281":23,"1468690411":24,"1275297413":25,
 "979306711":26,"768585174":27,"2117866167":28,"427020063":29,"1446795315":31,"2035760321":4,
 "576505807":39}
REACB = {"969776013":9,"1104658829":29,"537126178":1,  # ib6 layout (ib5: 30, 31)
 "1035318058":37,"1786223168":32,"1566437801":19}
UNITB = {"993049547":30,"1404126973":31,"489869766":32,"650097263":37}
PLANTB = {"2127906943":33,"740287642":33,"1700000002":36,"1700000011":36,"1700000020":36,
 "1700000030":34,"1700000039":34,"1700000048":34,"1700000057":34,"1700000066":34,"1700000075":34,
 "1700000084":34,"1700000094":35,"1700000103":35,"1700000112":35,"1700000122":38,"1700000131":38,
 "1700000140":38}
RAMP = {"476430100":"2127906943","1701983861":"740287642","1700000008":"1700000002","1700000017":"1700000011",
 "1700000026":"1700000020","1700000036":"1700000030","1700000045":"1700000039","1700000054":"1700000048",
 "1700000063":"1700000057","1700000072":"1700000066","1700000081":"1700000075","1700000090":"1700000084",
 "1700000100":"1700000094","1700000109":"1700000103","1700000118":"1700000112","1700000128":"1700000122",
 "1700000137":"1700000131","1700000146":"1700000140"}
W = 2 * np.pi * 50; VB = 400.0; SB = 100.0; ZB = VB**2 / SB


def num(v): return float(str(v).split("[")[0])


def load_case(path):
    r = ET.parse(path).getroot()
    M = [d for d in r.iter("Definition") if d.get("name") == "Main"][0]
    C = {c.get("id"): (c.get("defn"), {p.get("name"): p.get("value") for p in c.iter("param")}) for c in M.iter("User")}
    return C


def solve(C, shk=1.0, v0=None, verbose=True, plant_scale=1.0):
    nb = 40
    Y = np.zeros((nb, nb), complex)
    for k, (a, b) in LID.items():
        p = C[str(1600000000 + k)][1]
        z = complex(num(p["Rp1"]), W * num(p["Lp1"])) / ZB
        bsh = W * num(p["Cp1"]) * 1e-6 * ZB
        y = 1 / z
        Y[a, a] += y + 1j * bsh / 2; Y[b, b] += y + 1j * bsh / 2; Y[a, b] -= y; Y[b, a] -= y
    for i, (a, b) in XFB.items():
        p = C[i][1]
        x = num(p["Xl"]) * SB / num(p["Tmva"]); y = 1 / complex(0, x)
        Y[a, a] += y; Y[b, b] += y; Y[a, b] -= y; Y[b, a] -= y
    PL = np.zeros(nb); QSH = np.zeros(nb); PPL = np.zeros(nb)
    for i, b in LOADB.items(): PL[b] += 3 * num(C[i][1]["PO"]) / SB
    for i, b in REACB.items(): QSH[b] += shk * 3 * num(C[i][1]["QO"]) / SB
    for rid, pid in RAMP.items():
        PPL[PLANTB[pid]] += plant_scale * num(C[rid][1]["Y2"]) * num(C[pid][1]["Sbase"]) / SB
    kpf = num(C["2127906943"][1]["Kpf"])
    PG = np.zeros(nb); VS = {}
    for i, b in UNITB.items():
        PG[b] = num(C[i][1]["P0"]) / SB; VS[b] = num(C[i][1]["V0"]) if v0 is None else v0
    PG[9] -= 1000.0 / SB
    slack = 39; VS[39] = 1.02
    pv = [b for b in VS if b != slack]
    pq = [b for b in range(1, nb) if b not in VS]
    V = np.ones(nb); th = np.zeros(nb)
    for b, v in VS.items(): V[b] = v
    for it in range(40):
        Vc = V * np.exp(1j * th); S = Vc * np.conj(Y @ Vc)
        Pinj = PG - PL * V + PPL * V
        Qinj = -QSH + kpf * PPL * V
        dP = Pinj - S.real; dQ = Qinj - S.imag
        ia = [b for b in range(1, nb) if b != slack]
        mis = np.concatenate([dP[ia], dQ[pq]])
        if np.max(np.abs(mis)) < 1e-7: break
        # numerical Jacobian (small system)
        x0 = np.concatenate([th[ia], V[pq]])
        def f(x):
            t2 = th.copy(); v2 = V.copy(); t2[ia] = x[:len(ia)]; v2[pq] = x[len(ia):]
            Vc2 = v2 * np.exp(1j * t2); S2 = Vc2 * np.conj(Y @ Vc2)
            P2 = PG - PL * v2 + PPL * v2; Q2 = -QSH + kpf * PPL * v2
            return np.concatenate([(P2 - S2.real)[ia], (Q2 - S2.imag)[pq]])
        J = np.zeros((len(x0), len(x0))); f0 = f(x0); h = 1e-6
        for j in range(len(x0)):
            xx = x0.copy(); xx[j] += h; J[:, j] = (f(xx) - f0) / h
        x0 = x0 - np.linalg.solve(J, f0)
        th[ia] = x0[:len(ia)]; V[pq] = x0[len(ia):]
    Vc = V * np.exp(1j * th); S = Vc * np.conj(Y @ Vc)
    Qg = (S.imag + QSH - kpf * PPL * V) * SB
    Pg = (S.real + PL * V - PPL * V) * SB
    res = dict(V=V, th=th, it=it, Qg=Qg, Pg=Pg)
    if verbose:
        print(f"converged in {it} it, shunt reactors x{shk}, plant Pref x{plant_scale}")
        print("units (P MW, Q Mvar, V, angle deg):")
        for b in (30, 31, 32, 37, 39):
            print(f"  bus {b}: P {Pg[b] + (1000 if b==9 else 0):8.0f}  Q {Qg[b]:+8.0f}  V {V[b]:.4f}  {np.degrees(th[b]):+7.2f}")
        print("collectors: " + "  ".join(f"{b}:{V[b]:.4f}" for b in (33, 34, 35, 36, 38)))
        print("400 kV:     " + "  ".join(f"{b}:{V[b]:.3f}" for b in (1, 2, 3, 4, 9, 16, 19, 20, 22, 23, 29)))
        tie = sum(((Vc[a] * np.conj((Vc[a] - Vc[b]) / complex(num(C[str(1600000000+k)][1]['Rp1']), W*num(C[str(1600000000+k)][1]['Lp1'])) * ZB)).real) * SB
                  for k, (a, b) in LID.items() if b == 39)
        print(f"tie Spain->France (series part) {tie:.0f} MW; Iberian sync Q total {sum(Qg[b] for b in (30,31,32,37)):+.0f} Mvar; "
              f"plants {sum(PPL*V)*SB:.0f} MW; shunt reactors {sum(QSH)*SB:.0f} Mvar")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("pscx"); ap.add_argument("--sh", type=float, default=1.0)
    ap.add_argument("--v0", type=float, default=None); ap.add_argument("--pl", type=float, default=1.0)
    a = ap.parse_args()
    solve(load_case(a.pscx), a.sh, a.v0, plant_scale=a.pl)
