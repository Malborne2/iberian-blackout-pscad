"""AC-emulation lag check (G3c): id(t) after a 2 deg step of (Th9 - Th39) at t = 1 s.

The reference is  id_ref = Kang*(Th9 - Th39)/(1 + s*Tang), Kang = -0.36 pu/deg, Tang = 50 s, and the
module divides by VDF (constant-power), so the *power* reference steps to 0.72 pu and id follows
0.72/VDF * (1 - exp(-(t-1)/50)).

usage: python stage4\\hv_lag.py <psout>
"""

import sys
import numpy as np
import mhi.psout

PS = sys.argv[1]
T_STEP = 1.0
with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    t, idc = get("Root/Main/HVDC_T/ID/0/1")
    _, iq = get("Root/Main/HVDC_T/IQ/0/1")
    _, vdf = get("Root/Main/HVDC_T/VDF/0/1")
    _, tri = get("Root/Main/HVDC_T/TRIP/0/1")


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


dt = t[1] - t[0]
n20 = max(1, int(round(0.02 / dt)))
idf = mm(idc, n20)
print(f"{PS}\n  t = {t[0]:.1f}..{t[-1]:.1f} s, dt = {dt * 1e6:.0f} us, switchings step at t = {T_STEP} s")
print(f"  TRIP max {tri.max():.2f}")
print(f"  {'t [s]':>7} {'ID':>9} {'ID_filt':>9} {'VDF':>7}   expected 0.72*(1-exp(-(t-1)/50))")
for ts in (0.9, 1.5, 6, 11, 26, 51, 76, 101, 119.5):
    i = int(np.searchsorted(t, ts))
    i = min(i, len(t) - 1)
    exp = 0.0 if ts < T_STEP else 0.72 * (1 - np.exp(-(ts - T_STEP) / 50.0))
    print(f"  {t[i]:7.2f} {idc[i]:+9.4f} {idf[i]:+9.4f} {vdf[i]:7.4f}   {exp:+.4f}")

# the 63.2 % crossing and a least-squares T over the step
w = t > T_STEP + 0.5
inorm = (idf[w] - idf[w][0]) / (idf[np.argmin(np.abs(t - 119.9))] - idf[w][0])
i63 = np.argmax(inorm >= 0.632)
print(f"\n  63.2 % of the final rise reached at t = {t[w][i63]:.1f} s "
      f"({t[w][i63] - T_STEP:.1f} s after the step; T = 50 s would give 51.0 s)")
print(f"  final ID (119.9 s) = {idf[np.argmin(np.abs(t - 119.9))]:+.4f} pu; "
      f"hand: 0.72/VDF = {0.72 / vdf[np.argmin(np.abs(t - 119.9))]:+.4f} pu")
print(f"  peak |IQ| = {np.abs(iq).max():.3f} pu (Q channel active, Vset 1.025)")
