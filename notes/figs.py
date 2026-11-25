"""Produce the voltage / power / frequency figures from the current .psout."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read_out3 import load

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
T = float(sys.argv[1]) if len(sys.argv) > 1 else 4.0
TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'

d = load()
CYC = 40            # samples per 50 Hz cycle (0.5 ms output step)

MVA = {'G30': 1130, 'G31': 1130, 'G32': 1130, 'G33': 1500, 'G34': 1500, 'G35': 720}


def ts(name):
    a = d.get(name)
    if a is None:
        return None, None
    return np.linspace(0, T, len(a)), a


def rms_trace(a, n):
    """Sliding one-cycle RMS for an instantaneous waveform."""
    k = np.ones(CYC) / CYC
    return np.sqrt(np.convolve(a * a, k, mode='same'))


def envelope(name):
    t, a = ts(name)
    if t is None:
        return None, None
    return t, rms_trace(a, len(a))


# ---------------- figure 1: voltages ----------------
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
ax = axes[0]
for i in range(1, 6):
    t, v = envelope('V_C%d' % i)
    if v is not None:
        ax.plot(t, v / (132.0 / np.sqrt(3)), lw=1.1, label='C%d' % i)
ax.axhline(1.10, color='r', ls='--', lw=1.0)
ax.text(0.02, 1.105, 'OV threshold 1.10 pu', color='r', fontsize=8)
ax.set_ylabel('collector 132 kV bus (pu)')
ax.set_title('Collector bus voltages (GSU tap = 1.03)')
ax.grid(alpha=.3)
ax.legend(ncol=5, fontsize=8)

ax = axes[1]
for g in ('G30', 'G31', 'G32', 'G33', 'G34', 'G35'):
    t, v = envelope('V_' + g)
    if v is not None:
        ax.plot(t, v / 230.94, lw=1.1, label=g)
for g in ('G36', 'G37', 'G38', 'G39'):
    t, v = ts('V_' + g)
    if v is not None:
        ax.plot(t, v, lw=1.1, ls='--', label=g)
ax.set_ylabel('generator bus (pu)')
ax.set_xlabel('time (s)')
ax.set_title('Generator bus voltages (solid = synchronous machines, dashed = sources)')
ax.grid(alpha=.3)
ax.legend(ncol=5, fontsize=8)
fig.tight_layout()
p1 = os.path.join(BASE, 'notes', 'fig_voltage_%s.png' % TAG)
fig.savefig(p1, dpi=110)

# ---------------- figure 2: P, Q, f ----------------
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
ax = axes[0]
for g in ('G30', 'G31', 'G32', 'G33', 'G34', 'G35'):
    t, p = ts('P_' + g)
    if p is not None:
        ax.plot(t, np.convolve(p, np.ones(CYC) / CYC, 'same') * MVA[g], lw=1.1, label=g)
for g in ('G36', 'G37', 'G38', 'G39'):
    t, p = ts('P_' + g)
    if p is not None:
        ax.plot(t, np.convolve(p, np.ones(CYC) / CYC, 'same') * 100, lw=1.1, ls='--',
                label=g)
ax.set_ylabel('P (MW)')
ax.set_title('Active power')
ax.grid(alpha=.3)
ax.legend(ncol=5, fontsize=8)

ax = axes[1]
for g in ('G30', 'G31', 'G32', 'G33', 'G34', 'G35'):
    t, q = ts('Q_' + g)
    if q is not None:
        ax.plot(t, np.convolve(q, np.ones(CYC) / CYC, 'same') * MVA[g], lw=1.1, label=g)
ax.set_ylabel('Q (Mvar)')
ax.set_title('Reactive power of the synchronous fleet')
ax.grid(alpha=.3)
ax.legend(ncol=5, fontsize=8)

ax = axes[2]
t, f = ts('F_G30')
if f is not None:
    ax.plot(t, np.convolve(f, np.ones(CYC) / CYC, 'same'), lw=1.4, color='k')
    ax.axhline(50.0, color='r', ls='--', lw=1.0)
    ax.set_ylabel('frequency (Hz)')
    ax.set_title('Machine speed / system frequency (SMG30)')
else:
    ax.set_title('frequency channel not available in this run')
ax.set_xlabel('time (s)')
ax.grid(alpha=.3)
fig.tight_layout()
p2 = os.path.join(BASE, 'notes', 'fig_pqf_%s.png' % TAG)
fig.savefig(p2, dpi=110)

print('saved', p1)
print('saved', p2)
for k in ('F_G30',):
    a = d.get(k)
    if a is not None:
        print(k, 'min %.3f max %.3f last %.3f' % (a.min(), a.max(), a[-1]))
