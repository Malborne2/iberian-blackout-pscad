"""Plot selected channels from the current .psout."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read_out3 import load

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
d = load()
chans = sys.argv[1].split(',') if len(sys.argv) > 1 else ['V_C1', 'P_G30', 'P_G39']
outname = sys.argv[2] if len(sys.argv) > 2 else 'dbg.png'
T = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0

fig, axes = plt.subplots(len(chans), 1, figsize=(11, 2.2 * len(chans)), sharex=True)
if len(chans) == 1:
    axes = [axes]
for ax, c in zip(axes, chans):
    if c not in d:
        ax.set_title(c + ' (missing)')
        continue
    a = d[c]
    t = np.linspace(0, T, len(a))
    ax.plot(t, a, lw=1.0)
    ax.set_ylabel(c)
    ax.grid(alpha=.3)
ax.set_xlabel('t (s)')
fig.tight_layout()
p = os.path.join(BASE, 'notes', outname)
fig.savefig(p, dpi=110)
print('saved', p)
for c in chans:
    if c in d:
        a = d[c]
        print(c, 'first', a[1], 'at 0.5', a[len(a)//4], 'at 1.0', a[len(a)//2], 'last', a[-1])
