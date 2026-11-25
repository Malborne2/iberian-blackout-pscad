r"""Offline OV-relay emulation on a run with the relays parked (B2 control b5): when would each plant's report setting
fire if the relay measured VDF through a moving-average window W? Valid only up to the FIRST emulated trip (after it,
the real system would diverge from the parked run) - later lines are indicative.

usage: python stage12/relay_emul.py <run folder> <T0> [W_ms ...]   (default W = 0 20 60)
Settings by document order as `make_variant` ov_report: PSOUT k -> doc PS2DOC[k] -> OV[doc % 6].
"""
import os, sys
import mhi.psout
import numpy as np

fold, T0 = sys.argv[1], float(sys.argv[2]); E = T0 + 1.0
Ws = [float(x) for x in sys.argv[3:]] or [0.0, 20.0, 60.0]
OV = [(1.089, 1.5), (1.10, 0.0), (1.10, 0.5), (1.111, 0.1), (1.139, 0.2), (1.15, 0.6)]
PS2DOC = {1: 1, 18: 0, **{k: k for k in range(2, 18)}}
FORCED = {18, 5, 6}
PSB = {1: 3315.0, 2: 223.6, 3: 217.1, 4: 3122.6, 5: 841.1, 6: 210.6, 7: 735.8, 8: 526.5, 9: 440.7, 10: 306.8,
       11: 1552.2, 12: 795.6, 13: 169.0, 14: 3247.4, 15: 765.7, 16: 452.4, 17: 4071.6, 18: 520.0}
rep = lambda t: 76.443 + (t - (E + 3.0))
r = mhi.psout.File(os.path.join(fold, "ib6.gf81_x86", "ib6.psout")).run(0)
g = lambda p: np.asarray(r.call(p, sep="/").data, float)
t = np.asarray(r.call("Root/Main/RES_Plant[1]/VDF/0/1", sep="/").domain.data, float); dt = t[1] - t[0]
V = {k: g(f"Root/Main/RES_Plant[{k}]/VDF/0/1") for k in PSB}
pre = (t >= T0) & (t <= T0 + 0.95)
MW = {k: float(((g(f"Root/Main/RES_Plant[{k}]/VD/0/1") * g(f"Root/Main/RES_Plant[{k}]/ID/0/1") +
                 g(f"Root/Main/RES_Plant[{k}]/VQ/0/1") * g(f"Root/Main/RES_Plant[{k}]/IQ/0/1")) * PSB[k])[pre].mean()) for k in PSB}


def ma(y, w):    # trailing (causal) moving average, as a relay would compute it
    n = max(1, int(round(w / 1000 / dt)))
    c = np.cumsum(np.concatenate([np.full(n, y[0]), y])); return (c[n:] - c[:-n]) / n


def fire(m, vt, tt):
    above = m > vt; n = max(1, int(round(tt / dt)))
    run = np.convolve(above.astype(int), np.ones(n, int), mode="full")[:len(m)] >= n
    ok = run & (t > T0 + 0.1)
    return t[np.argmax(ok)] if ok.any() else None


coll = np.mean([V[k] for k in PSB], axis=0)
print(f"# {fold}: mean collector VDF, 60 ms MA, at report-clock times (Fig 3-7a 400 kV max for reference)")
for tr in (76.0, 76.443, 76.6, 76.9, 77.3, 77.6, 78.0, 78.4, 79.1):
    tm = E + 3.0 + (tr - 76.443)
    if t[0] <= tm <= t[-1]: print(f"  report {tr:6.3f} s (model {tm:6.3f}): {ma(coll, 60)[np.searchsorted(t, tm)]:.4f} pu")
for W in Ws:
    rows = []
    for k in PSB:
        if k in FORCED: continue
        vt, tt = OV[PS2DOC[k] % 6]; m = ma(V[k], W) if W > 0 else V[k]
        tf = fire(m, vt, tt)
        rows.append((tf if tf is not None else 1e9, k, vt, tt, float(m[t >= E].max())))
    rows.sort()
    print(f"## W = {W:.0f} ms")
    for tf, k, vt, tt, mx in rows:
        s = f"{tf:7.3f} s (report {rep(tf):7.3f})" if tf < 1e8 else "  never" + " " * 19
        print(f"  {s} plant {k:2d} {MW[k]:5.0f} MW  setting {vt:.3f}/{tt:.1f} s  max meas {mx:.4f}")
