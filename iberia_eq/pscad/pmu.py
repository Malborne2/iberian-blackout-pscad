r"""PMU-style measurement of PSCAD phase-voltage channels (S30 sec 13).

Real comparisons with [FR] use PMU / SCADA data, never raw waveforms: a PMU estimates the 50 Hz phasor over whole
cycles (DFT), which rejects harmonics and converter switching ripple, and derives frequency from the phasor angle.
This module does the same on the model's 3-phase channels so that model curves are measured like the report's.

  pmu(t, va, vb, vc, f0=50.0, cycles=1, rate=50.0) -> dict(t, V, ang, f, rocof)
    - positive-sequence phasor by a recursive full-cycle DFT window of `cycles` cycles at f0
      (cycles=1: P-class-like response; cycles=2..4: closer to M-class filtering);
    - V: positive-sequence magnitude in line-to-line rms units of the input (input in kV phase-to-ground instantaneous
      -> kV LL rms);
    - ang: unwrapped angle (rad); f = f0 + d(ang)/dt / 2 pi, smoothed over one more window; rocof = df/dt;
    - output decimated to `rate` frames per second (50 = a typical PMU reporting rate).
Usage in scripts: from pmu import pmu.
"""
import numpy as np

A = np.exp(2j * np.pi / 3)

def _window_mean(x, n):
    c = np.cumsum(np.insert(x, 0, 0.0)); y = np.empty_like(x)
    y[n - 1:] = (c[n:] - c[:-n]) / n; y[:n - 1] = y[n - 1]
    return y

def pmu(t, va, vb, vc, f0=50.0, cycles=1, rate=50.0):
    dt = t[1] - t[0]; n = int(round(cycles / (f0 * dt)))
    rot = np.exp(-1j * 2 * np.pi * f0 * t)
    vpos = (va + A * vb + A * A * vc) / 3.0                       # instantaneous positive-sequence space vector
    ph = _window_mean(vpos * rot, n)                               # full-cycle DFT of the positive sequence
    # balanced set va = Vp cos(wt+d): vpos*rot averages to Vp/2 e^{jd}; LL rms = Vp*sqrt(3)/sqrt(2)
    Vll = 2.0 * np.abs(ph) * np.sqrt(3.0) / np.sqrt(2.0)
    ang = np.unwrap(np.angle(ph))
    f = f0 + _window_mean(np.gradient(ang, dt), n) / (2 * np.pi)
    rocof = _window_mean(np.gradient(f, dt), n)
    k = max(1, int(round(1.0 / (rate * dt)))); s = slice(n - 1, None, k)
    return dict(t=t[s], V=Vll[s], ang=ang[s], f=f[s], rocof=rocof[s])

if __name__ == "__main__":                                         # self-test on a synthetic signal with ripple
    t = np.arange(0, 1.0, 20e-6); f = 49.8; Vp = 400 * np.sqrt(2 / 3)
    w = 2 * np.pi * f; rip = 0.05 * Vp * np.cos(2 * np.pi * 2700 * t)
    va, vb, vc = (Vp * np.cos(w * t + p) + rip for p in (0, -2 * np.pi / 3, 2 * np.pi / 3))
    r = pmu(t, va, vb, vc)
    m = r["t"] > 0.2
    print(f"V {r['V'][m].mean():.2f} kV (400), f {r['f'][m].mean():.4f} Hz (49.8), ripple in V {np.ptp(r['V'][m]):.2f} kV")
