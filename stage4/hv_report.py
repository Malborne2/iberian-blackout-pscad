"""HVDC_T bench report: P/Q/id/iq/VDF/TRIP and the two angle inputs, from one run's own .psout.

usage: python stage4\\hv_report.py <psout> [t0 t1]
"""
import sys
import numpy as np
import mhi.psout

PS = sys.argv[1]
W = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else None
CH = ["ID", "IQ", "VDF", "VD", "VQ", "TRIP", "VA_PU"]
REF = ["IDREF0", "IDANG", "IQREF", "VREF", "ID"]


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    t = None
    data = {}
    for c in CH:
        try:
            tt, y = get(f"Root/Main/HVDC_T/{c}/0/1")
        except Exception:
            continue
        data[c] = y
        t = tt
    if t is None:
        print("no HVDC_T channels; channels present:")
        for ch in r.channels()[:60] if hasattr(r, "channels") else []:
            print("  ", ch)
        sys.exit(1)
    dt = t[1] - t[0]
    n20 = int(round(0.02 / dt))
    lo, hi = W if W else (max(0.0, t[-1] - 1.0), t[-1])
    w = (t >= lo) & (t <= hi)
    print(f"{PS}\n  t = {t[0]:.3f}..{t[-1]:.3f} s, window {lo:.2f}-{hi:.2f} s, dt = {dt * 1e6:.0f} us")
    print(f"  {'chan':8} {'mean':>10} {'min':>10} {'max':>10}  (window mean)")
    for c, y in data.items():
        print(f"  {c:8} {y[w].mean():+10.4f} {y.min():+10.4f} {y.max():+10.4f}")
    if "VD" in data and "ID" in data:
        vd, idc = data["VD"], data["ID"]
        iq = data.get("IQ", np.zeros_like(vd))
        vq = data.get("VQ", np.zeros_like(vd))
        p = mm(vd * idc + vq * iq, n20)
        q = mm(vd * iq - vq * idc, n20)
        print(f"\n  P {p[w].mean():+9.4f} pu = {p[w].mean() * 1000:+8.1f} MW   "
              f"Q {q[w].mean():+9.4f} pu = {q[w].mean() * 1000:+8.1f} Mvar  (Sbase 1000 MVA)")
    print("\n  time series (0.25 s grid):")
    for tt in np.arange(0, t[-1] + 1e-9, 0.25):
        i = int(np.searchsorted(t, tt))
        i = min(i, len(t) - 1)
        row = " ".join(f"{c}={data[c][i]:+8.4f}" for c in ("ID", "IQ", "VDF"))
        print(f"    t={t[i]:5.2f}  {row}")
