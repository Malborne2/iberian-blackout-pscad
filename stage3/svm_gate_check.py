"""Duty-cycle fundamental of each SVM gate signal (0/1 channels)."""
import csv
import sys
import numpy as np

path = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\cv1_gates.csv"
rows = list(csv.reader(open(path)))
hdr = rows[0]
d = np.array([[float(v) for v in r] for r in rows[1:] if r])
t = d[:, 0]
sel = (t >= 0.30) & (t <= 0.36)
tt = t[sel]
dt = tt[1] - tt[0]
n = sel.sum()
w = np.hanning(n)
res = {}
print("duty-cycle fundamental of each gate signal (0/1 channels):")
for c in range(1, d.shape[1]):
    y = d[sel, c]
    y = y - y.mean()
    s = np.fft.rfft(y * w)
    f = np.fft.rfftfreq(n, dt)
    a = 2 * np.abs(s) / w.sum()
    lo = np.argmin(abs(f - 30))
    hi = np.argmin(abs(f - 70))
    k = lo + np.argmax(a[lo:hi])
    name = hdr[c].split("/")[-3]
    res[name] = (a[k], np.degrees(np.angle(s[k])), f[k])
    print(f"{name:<8} duty-fund {a[k]:.4f}  phase {np.degrees(np.angle(s[k])):8.1f} deg  f {f[k]:.1f}")
print()
p1 = res["S1raw"][1]
print("relative to S1:")
for k, (a, ph, f) in res.items():
    print(f"  {k}: {((ph - p1 + 180) % 360) - 180:8.1f} deg  amp {a:.4f}")
