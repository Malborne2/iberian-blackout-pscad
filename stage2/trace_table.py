"""Print POUT, QOUT, VIT, Wspd every 0.25 s for a window, to see whether the bench decays.

Run: python trace_table.py <psout> <chan> <t0> <t1> <dt>
"""
import sys
from statistics import fmean

import mhi.psout

PATH, CHAN = sys.argv[1], sys.argv[2]
T0, T1, DT = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
EXTRA = sys.argv[6:]

with mhi.psout.File(PATH) as f:
    run = f.run(0)
    paths = [str(p) for _, p in run.trace_paths()]
    t = run.call("PGB:Domain", sep="/").data
    chans = {}
    for name in [CHAN] + EXTRA:
        hit = [p for p in paths if p.endswith(f"/{name}/0/1")]
        if hit:
            chans[name] = run.call(hit[0], sep="/").data

idx = {name: 0 for name in chans}
print("t".rjust(8) + "".join(name.rjust(12) for name in chans))
x = T0
while x <= T1:
    row = f"{x:>8.2f}"
    for name, vals in chans.items():
        seg = [v for tt, v in zip(t, vals) if x <= tt < x + DT]
        row += f"{fmean(seg):>12.4f}" if seg else f"{'--':>12}"
    print(row)
    x += DT
