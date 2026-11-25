"""Stage 3a bench report: fundamentals, balance, THD, and the hand check Vph_pk = AMP*Vdc/2."""
import csv
import sys
import numpy as np

path = sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\cv1_traces.csv"
win = (0.30, 0.36)          # 3 fundamental periods
tsw = 1650.0

with open(path, newline="") as fh:
    rows = list(csv.reader(fh))
hdr = rows[0]
d = np.array([[float(v) for v in r] for r in rows[1:] if r])
t = d[:, 0]
sel = (t >= win[0]) & (t <= win[1])
tt = t[sel]
dt = tt[1] - tt[0]
n = sel.sum()
w = np.hanning(n)


def spec(y):
    y = y - y.mean()
    s = np.fft.rfft(y * w)
    f = np.fft.rfftfreq(n, dt)
    a = 2 * np.abs(s) / w.sum()
    return f, a


def fundamental(y):
    f, a = spec(y)
    k = np.argmin(np.abs(f - 50.0))
    # refine by taking the local max within +-20 Hz of 50 Hz
    lo = np.argmin(np.abs(f - 30.0)); hi = np.argmin(np.abs(f - 70.0))
    k = lo + np.argmax(a[lo:hi])
    ph = np.angle(np.fft.rfft((y - y.mean()) * w)[k])
    return a[k], np.degrees(ph), f[k]


print(f"window {win[0]}..{win[1]} s  ({n} samples, dt={dt*1e6:.2f} us)")
print(f"{'signal':<10} {'mean':>9} {'f1':>7} {'amp1':>9} {'phase':>8} {'THD%':>7}")
out = {}
for c in range(1, d.shape[1]):
    y = d[sel, c]
    a1, p1, f1 = fundamental(y)
    f, a = spec(y)
    fund_bin = np.argmin(np.abs(f - f1))
    band = (np.abs(f - f1) < 5)
    harm = np.sqrt(np.sum(a[(f > 100)] ** 2))
    thd = 100 * harm / a1 if a1 > 1e-9 else float("nan")
    out[hdr[c]] = dict(mean=y.mean(), amp=a1, phase=p1, thd=thd)
    if "raw" not in hdr[c] or "S1" in hdr[c]:
        print(f"{hdr[c].split('/')[-3]:<10} {y.mean():9.2f} {f1:7.1f} {a1:9.3f} {p1:8.1f} {thd:7.2f}")

print()
for nm in ("VbrA", "VbrB", "VbrC"):
    key = [k for k in out if f"/{nm}/" in k][0]
    o = out[key]
    print(f"{nm}: mean {o['mean']:.1f} kV, fundamental peak {o['amp']:.1f} kV, phase {o['phase']:.1f} deg")
va = [out[k] for k in out if "/VbrA/" in k][0]
vb = [out[k] for k in out if "/VbrB/" in k][0]
vc = [out[k] for k in out if "/VbrC/" in k][0]
print(f"phase spreads: A-B {((vb['phase']-va['phase']+180)%360)-180:.1f} deg, "
      f"B-C {((vc['phase']-vb['phase']+180)%360)-180:.1f} deg, "
      f"amplitude spread {100*(max(va['amp'],vb['amp'],vc['amp'])-min(va['amp'],vb['amp'],vc['amp']))/np.mean([va['amp'],vb['amp'],vc['amp']]):.2f} %")
vrail = [out[k] for k in out if "/Vrail/" in k][0]
amp = [out[k] for k in out if "/AMPraw/" in k]
print(f"Vrail: mean {vrail['mean']:.1f} kV, ripple amp {vrail['amp']:.2f} kV at {vrail['thd']:.0f}% THD")
for k, o in out.items():
    if "/Isrc" in k:
        print(f"{k.split('/')[-3]}: fundamental peak {o['amp']*1000:.1f} A, THD {o['thd']:.2f} %")
