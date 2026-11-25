"""Batch F0: voltage rise after each forced initiator (relays parked).
usage: python stage12/f0_rise.py <run folder> [...]
Windows (T0 28): pre 28.5-29.0 | after event 3 (Granada, 29.0) 31.4-31.9 | after 4a (32.0) 32.25-32.37 |
after 4b (32.377) 33.0-33.5 | late 37.0-38.0. Report Fig 3-7a (400 kV max): 421.8 kV before event 3, 427.8 kV before
4a (+6.0 kV drift over 19 s, ~+0.015 pu), 432.7 kV at 76.9 s after 4a+4b (727 MW: +4.9 kV, +0.012 pu) - later
points include relay trips, not comparable to a parked run.
"""
import sys, os, numpy as np, mhi.psout
W = {"pre": (28.5, 29.0), "ev3": (31.4, 31.9), "4a": (32.25, 32.37), "4b": (33.0, 33.5), "late": (37.0, 38.0)}
GRP = {"b33(1,18)": 1, "b34(5-11)": 7, "b35(12-14)": 13, "b36(2-4)": 3, "b38(15-17)": 16}
for fold in sys.argv[1:]:
    r = mhi.psout.File(os.path.join(fold, "ib6.gf81_x86", "ib6.psout")).run(0)
    def g(p):
        try:
            tr = r.call(p, sep="/"); return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)
        except Exception: return None, None
    t, _ = g("Root/Main/SyncUnit[1]/Wspd/0/1")
    m = lambda y, w: float(np.mean(y[(t >= w[0]) & (t <= w[1])]))
    rows = {}
    for nm, k in GRP.items(): rows["VDF " + nm] = g(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1]
    for b in (20, 23, 29, 4, 8, 16, 21, 27):
        y = g(f"Root/Main/VL{b}/0/1")[1]
        if y is not None: rows[f"VL{b}"] = y
    vls = [v for k, v in rows.items() if k.startswith("VL")]
    rows["VLmax"] = np.max(np.vstack(vls), axis=0)
    UN = {1: "32", 2: "37", 3: "30", 4: "31"}; SB = {1: 15292.0, 2: 12838.0, 3: 6113.0, 4: 13548.0}
    q = {}
    for i in UN:
        y = g(f"Root/Main/SyncUnit[{i}]/QOUT/0/1")[1]
        if y is None: y = g(f"Root/Main/SyncUnit[{i}]/Q/0/1")[1]
        if y is not None: q[UN[i]] = y * SB[i]
    print(f"===== {os.path.basename(fold)}  (t end {t[-1]:.2f})")
    print(f"{'':14s}" + "".join(f"{w:>9s}" for w in W) + "   d(ev3)   d(4a+4b)  d/GW(4a+4b)")
    for k, y in rows.items():
        v = {w: m(y, W[w]) for w in W}
        print(f"{k:14s}" + "".join(f"{v[w]:9.4f}" for w in W) +
              f"  {v['ev3']-v['pre']:+.4f}  {v['4b']-v['ev3']:+.4f}  {(v['4b']-v['ev3'])/0.725:+.4f}")
    for k, y in q.items():
        v = {w: m(y, W[w]) for w in W}
        print(f"Q unit {k:7s}" + "".join(f"{v[w]:9.0f}" for w in W) + f"  {v['ev3']-v['pre']:+.0f}  {v['4b']-v['ev3']:+.0f} Mvar")
    ptie = -g("Root/Main/PTIE/0/1")[1]; f1 = g("Root/Main/SyncUnit[1]/Wspd/0/1")[1] / 2 / np.pi
    print("PTIE  " + "".join(f"{m(ptie, W[w]):9.0f}" for w in W) + "   f32 " + " ".join(f"{m(f1, W[w]):.3f}" for w in W))
