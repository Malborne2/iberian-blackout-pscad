r"""Run-speed optimisation summary figure (RUNLOG S30 sec 23). Values: 'solver speed' lines of run_v2 (0.3 s runs,
build excluded, solver pinned at High priority, 4 long runs in the background), copied here because the smoke run
logs were overwritten by reruns of the same tags.

usage: python iberia_eq\pscad\opt_speed_fig.py   ->  iberia_eq\pscad\figs\opt_speed.png
"""
import os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

A = [("compact core (CPU 8), baseline", 923), ("  + threads=1", 912), ("  + fewer recorded channels", 905),
     ("  + compiler O3 -march=native*", 924), ("fast core shared (SMT, 2 solvers)", 665), ("fast core alone (CPU 0)", 478)]
B = [("full replay (meter + 2 breakers)", 560), ("France meter only", 469), ("France breaker only", 327), ("no series elements", 310)]
C = [("old: series multimeter", 436), ("new: breaker BP/BQ", 248)]
fig, ax = plt.subplots(1, 3, figsize=(16, 5.2), gridspec_kw=dict(width_ratios=[5, 4, 3]))
for x, data, title, col in ((ax[0], A, "1  where the solver runs (same replay case)", "#6b7280"),
                            (ax[1], B, "2  what the replay case costs (one batch)", "#2563eb"),
                            (ax[2], C, "3  adopted fix", "#16a34a")):
    lab = [d[0] for d in data][::-1]; val = [d[1] for d in data][::-1]
    bars = x.barh(lab, val, color=col)
    for b, v in zip(bars, val): x.text(v + 8, b.get_y() + b.get_height() / 2, f"{v}", va="center", fontsize=9)
    x.set_title(title, fontsize=10, loc="left"); x.set_xlabel("wall s per simulated s (lower is faster)", fontsize=9); x.grid(axis="x", alpha=.3)
    x.set_xlim(0, max(val) * 1.18)
fig.text(0.01, 0.01, "* O3 pair measured unpinned against an unpinned baseline (925): no gain", fontsize=8, color="#6b7280")
fig.suptitle("PSCAD run-speed optimisation (S30 sec 23): fast cores 1.9x, France series meter removed 1.75x", fontsize=12)
fig.tight_layout(rect=(0, 0.04, 1, 1))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs", "opt_speed.png"); fig.savefig(out, dpi=110); print(out)
