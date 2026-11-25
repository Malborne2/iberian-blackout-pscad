r"""Score Case B2 runs: relay-driven plant trips against the report's cumulative loss (Fig 3-7a), on the Case A clock.

usage: python stage12/b2_score.py <T0> <run folder> [<run folder> ...]
Model time -> report time: t_rep = 76.443 + (t - (T0 + 4)) for t >= T0 + 4 (Case A clock, k = 1).
Per run: each plant trip (TRIP > 0.5) with time, report-clock time, pre-event MW, forced/relay, and VDF at the trip;
cumulative tripped MW at report 76.9 / 77.6 / 78.4 / 79.1 s vs Fig 3-7a; `OOS1`/`BRKFR` time vs 81.407 s.
"""
import csv, os, sys
import mhi.psout
import numpy as np

T0 = float(sys.argv[1]); E = T0 + 1.0
HERE = os.path.dirname(os.path.abspath(__file__))
rep = lambda t: 76.443 + (t - (E + 3.0))
FORCED = {18: E, 5: E + 3.0, 6: E + 3.377}
PSB = {1: 3315.0, 2: 223.6, 3: 217.1, 4: 3122.6, 5: 841.1, 6: 210.6, 7: 735.8, 8: 526.5, 9: 440.7, 10: 306.8,
       11: 1552.2, 12: 795.6, 13: 169.0, 14: 3247.4, 15: 765.7, 16: 452.4, 17: 4071.6, 18: 520.0}
fig = [(float(r["t_sim_s"]), float(r["cum_imbalance_MW"])) for r in
       csv.DictReader(open(os.path.join(HERE, "..", "data", "targets_fig3-7a.csv")))]
cum_rep = lambda t: max([c for tt, c in fig if tt <= t] or [0.0])
for fold in sys.argv[2:]:
    r = mhi.psout.File(os.path.join(fold, "ib6.gf81_x86", "ib6.psout")).run(0)
    g = lambda p: np.asarray(r.call(p, sep="/").data, float)
    t = np.asarray(r.call("Root/Main/RES_Plant[1]/VDF/0/1", sep="/").domain.data, float)
    pre = (t >= T0) & (t <= T0 + 0.95)
    rows = []
    for k in PSB:
        c = {x: g(f"Root/Main/RES_Plant[{k}]/{x}/0/1") for x in ("VD", "VQ", "ID", "IQ", "VDF", "TRIP")}
        mw = float(((c["VD"] * c["ID"] + c["VQ"] * c["IQ"]) * PSB[k])[pre].mean())
        on = (t > T0 + 0.1) & (c["TRIP"] > 0.5)
        if on.any():
            i = int(np.argmax(on)); j = max(0, i - int(0.05 / (t[1] - t[0])))
            rows.append((t[i], k, mw, "forced" if abs(t[i] - FORCED.get(k, -9)) < 0.01 else "relay", c["VDF"][j:i].max()))
    rows.sort()
    print(f"## {os.path.basename(fold)}  (t {t[0]:.2f}..{t[-1]:.2f})")
    cum = 0.0
    for tt, k, mw, how, v in rows:
        cum += mw
        print(f"  {tt:7.3f} s (report {rep(tt):7.3f}) plant {k:2d} {mw:6.0f} MW {how:6s} VDF before {v:.4f} | cum {cum:6.0f}"
              f" (report cum {cum_rep(rep(tt)) - 537.4:6.0f})")
    for tr in (76.9, 77.6, 78.4, 79.1, 79.62):
        tm = E + 3.0 + (tr - 76.443)
        m = sum(mw for tt, k, mw, h, v in rows if tt <= tm)
        print(f"  at report {tr:6.2f} s (model {tm:6.2f}): tripped {m:6.0f} MW vs Fig 3-7a cum {cum_rep(tr) - 537.4:6.0f}"
              f" (report curve minus the 537 MW before event 3)")
    for nm in ("OOS1", "BRKFR"):
        try:
            y = g(f"Root/Main/{nm}/0/1"); on = (t > T0 + 0.1) & (y > 0.5)
            print(f"  {nm}: " + (f"{t[np.argmax(on)]:.3f} s (report clock {rep(t[np.argmax(on)]):.3f}; report 81.407)" if on.any() else "none"))
        except Exception as e:
            print(f"  {nm}: n/a ({e})")
