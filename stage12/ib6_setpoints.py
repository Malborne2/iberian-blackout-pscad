"""Machine set-points for ib6 from the AC power flow (stage12/acflow.py).
Reactor layout v2: generator-bus reactors (SH30/31/32/37/19) and the bus-9 bank OFF; new
shunt reactors 750 Mvar at bus 29 and 500 Mvar at bus 1 (re-labelled SH30/SH31 reactor elements).
Iberian units scaled together (k) so that France P = 3,195.8 MW (Spain exports 335 MW AC + 1,000 HVDC).
Prints P0/Q0/V0/Ph0 for every unit (Ph0 relative to France kept at -0.17784 rad)."""
import sys, numpy as np
sys.path.insert(0, 'stage12'); import acflow as A
V0 = float(sys.argv[2]) if len(sys.argv) > 2 else 1.06
Q29, Q1, Q9 = (float(x) for x in (sys.argv[3:6] if len(sys.argv) > 5 else (750, 500, 0)))
C = dict(A.load_case(sys.argv[1]))
A.REACB['X29'] = 29; A.REACB['X1'] = 1
C['X29'] = ('f', {'QO': str(Q29 / 3)}); C['X1'] = ('f', {'QO': str(Q1 / 3)})
C['969776013'] = ('f', {'QO': str(Q9 / 3)})
for i in ('1104658829', '537126178', '1035318058', '1786223168', '1566437801'):
    C[i] = ('f', {'QO': '0'})
base = {i: A.num(C[i][1]['P0']) for i in A.UNITB}
FR = 4195.8   # French load 4,530.8 - AC tie 335 (the HVDC power goes into the ideal DC source, not to France)
k = 1.0
REF = A.load_case('stage11/ib5_s23_prepared.pscx')   # report loads (S23), before any voltage correction
PO0 = {i: A.num(REF[i][1]['PO']) for i in A.LOADB}
for i in A.LOADB: C[i] = (C[i][0], dict(C[i][1], PO=str(PO0[i])))
Y20 = {i: A.num(REF[i][1]['Y2']) for i in A.RAMP}
for i in A.RAMP: C[i] = (C[i][0], dict(C[i][1], Y2=str(Y20[i])))
for outer in range(4):
  for it in range(20):
    for i in A.UNITB:
        C[i] = (C[i][0], dict(C[i][1], P0=str(base[i] * k)))
    r = A.solve(C, 1.0, V0, verbose=False)
    p39 = r['Pg'][39]
    if abs(p39 - FR) < 1: break
    k += 0.7 * (p39 - FR) / sum(base.values()); pass
  # loads are P = PO*V (NP=1): set PO so each load draws its report MW at its own voltage
  for i, b in A.LOADB.items():
      C[i] = (C[i][0], dict(C[i][1], PO=str(PO0[i] / r['V'][b])))
  # plants are current sources (P = Y2*Sbase*V): set Y2 so each delivers its report MW at its bus V
  for i, pid in A.RAMP.items():
      C[i] = (C[i][0], dict(C[i][1], Y2=str(Y20[i] / r['V'][A.PLANTB[pid]])))
r = A.solve(C, 1.0, V0, verbose=True)
th39 = r['th'][39]
print(f"\nunit scale k = {k:.4f} (Iberian sync {k*sum(base.values()):.0f} MW)")
for i, b in A.UNITB.items():
    print(f"{i} bus {b}: P0 {base[i]*k:.1f}  Q0 {r['Qg'][b]:.1f}  V0 {V0}  Ph0 {-0.17784 + r['th'][b] - th39:.5f}")
print(f"France: P0 {r['Pg'][39]:.1f} Q0 {r['Qg'][39]:.1f} V0 1.02 Ph0 -0.17784")
print("loads PO per phase (report MW at operating V):")
for i, b in A.LOADB.items(): print(f"  {i} bus {b}: PO {A.num(C[i][1]['PO']):.3f}  (V {r['V'][b]:.4f})")

import json
out = {"units": {i: [round(base[i]*k, 1), round(float(r['Qg'][b]), 1), round(-0.17784 + float(r['th'][b] - th39), 5)] for i, b in A.UNITB.items()},
       "fr_q0": round(float(r['Qg'][39]), 1),
       "loads": {i: round(A.num(C[i][1]['PO']), 4) for i in A.LOADB},
       "ramps": {i: round(A.num(C[i][1]['Y2']), 6) for i in A.RAMP},
       "reactors": {"969776013": Q9 / 3, "1104658829": Q29 / 3, "537126178": Q1 / 3,
                    "1035318058": 0.001, "1786223168": 0.001, "1566437801": 0.001}}
fn = sys.argv[6] if len(sys.argv) > 6 else "stage12/setpoints.json"
json.dump(out, open(fn, "w"), indent=1); print("wrote", fn)
