"""Recover the DC value of a decimated multimeter channel (100 Hz ripple) by least squares."""
import sys
import numpy as np
import mhi.psout


def dc(path, chan, lo=2.0, hi=3.0, f0=100.0):
    with mhi.psout.File(path) as f:
        r = f.run(0)
        tr = r.call(chan, sep="/")
        t = np.asarray(tr.domain.data, float)
        y = np.asarray(tr.data, float)
    m = (t >= lo) & (t <= hi)
    t, y = t[m], y[m]
    cols = [np.ones_like(t), np.cos(2 * np.pi * f0 * t), np.sin(2 * np.pi * f0 * t),
            np.cos(4 * np.pi * f0 * t), np.sin(4 * np.pi * f0 * t), t - t.mean()]
    A = np.column_stack(cols)
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ c
    return c[0], res.std(), y.std(), t.size


if __name__ == "__main__":
    A, B = sys.argv[1], sys.argv[2]
    print(f"{'channel':28} {'DC pre':>11} {'DC post':>11} {'rel':>10} {'resid rms':>10} {'y sd':>8} {'n':>4}")
    worst = (0, "")
    for k in range(1, 10):
        for sub, nm in ((2, "Pd"), (3, "Qd"), (4, "Vd")):
            ch = f"Root/Main/multimeter[{k}]/{sub}/{nm}"
            try:
                a, ra, sa, na = dc(A, ch)
                b, rb, sb, nb = dc(B, ch)
            except Exception as e:
                print(ch, "missing", e)
                continue
            rel = abs(b - a) / abs(a) if abs(a) > 1e-12 else abs(b - a)
            flag = ""
            if rel > worst[0]:
                worst = (rel, ch)
            print(f"{nm} mm[{k}]{'':12} {a:11.6f} {b:11.6f} {rel:10.2e} {max(ra, rb):10.4f} {max(sa, sb):8.4f} {min(na, nb):4d}")
    print("worst:", worst[1], f"{worst[0]:.2e}")
