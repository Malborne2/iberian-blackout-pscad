"""quick_plot.py <psout> <png> <t0> <t1> <ch1> [ch2 ...]  (channel = path below Root/Main/)"""
import sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, mhi.psout
ps, png, t0, t1, chans = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5:]
fig, axs = plt.subplots(len(chans), 1, figsize=(11, 2.1 * len(chans)), sharex=True)
axs = np.atleast_1d(axs)
with mhi.psout.File(ps) as f:
    run = f.run(0)
    for ax, c in zip(axs, chans):
        tr = run.call(f"Root/Main/{c}/0/1", sep="/")
        t, y = np.asarray(tr.domain.data), np.asarray(tr.data)
        s = (t >= t0) & (t <= t1)
        ax.plot(t[s], y[s], lw=0.6); ax.set_ylabel(c.split("/")[-1]); ax.grid(alpha=.3)
        print(f"{c:28s} mean {y[s].mean():+.4f} min {y[s].min():+.4f} max {y[s].max():+.4f}")
axs[-1].set_xlabel("t [s]"); fig.tight_layout(); fig.savefig(png, dpi=90)
