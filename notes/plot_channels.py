"""Plot the 30 output channels of the current .psout."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read_out3 import load

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
d = load()
n = max(len(v) for k, v in d.items() if k.startswith('P_G'))
T = 2.0
t = np.linspace(0, T, n)

gens = sorted({k.split('_')[1] for k in d if k.startswith('P_G')})

fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
ax = axes[0]
for g in gens:
    if f'P_{g}' in d:
        ax.plot(t, d[f'P_{g}'] * 100, lw=1.0, label=g)
ax.set_ylabel('Active power (MW)')
ax.grid(alpha=.3)
ax.legend(ncol=5, fontsize=7)

ax = axes[1]
for g in gens:
    if f'Q_{g}' in d:
        ax.plot(t, d[f'Q_{g}'] * 100, lw=1.0, label=g)
ax.set_ylabel('Reactive power (Mvar)')
ax.grid(alpha=.3)

ax = axes[2]
for g in gens:
    if f'V_{g}' in d:
        ax.plot(t, d[f'V_{g}'], lw=1.0, label=g)
ax.set_ylabel('Voltage (pu)')
ax.set_xlabel('time (s)')
ax.grid(alpha=.3)
ax.legend(ncol=5, fontsize=7)

fig.suptitle('Spanish_grid_model - phase 1 baseline (scaled IEEE-39, 400 kV, 50 Hz)')
fig.tight_layout()
out = os.path.join(BASE, 'notes', 'phase1_baseline.png')
fig.savefig(out, dpi=110)
print('saved', out)

tot = sum(d[f'P_{g}'][-100:].mean() for g in gens) * 100
print(f'total generation {tot/1000:.2f} GW')
