"""Session 19b bench check for `VrefK` (the AVR voltage-reference scale added to `SyncUnit`).

usage: python stage2\\vref_bench.py <psout> [<reference psout>]

Prints, for every `SyncUnit` instance in a bench run: VIT, VREF, POUT, QOUT, f -- averaged over two windows
(before and after the island's load step at 10 s) -- and, if a reference run is given, the maximum
absolute difference per channel over the whole overlap (the patcher must be transparent at VrefK = 1.0).

Numerics: POUT/QOUT are the machine's own outputs (rule M3: the machine is the independent meter for the
AVR), the frequency is Wspd/2pi smoothed with a 20 ms moving mean padded by edge values (skill P7.4).
"""
import sys
import numpy as np
import mhi.psout

W = [(8.0, 10.0), (20.0, 24.0)]
CH = ("VIT", "VREF", "POUT", "QOUT", "Wspd")


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


def read(path):
    out = {}
    with mhi.psout.File(path) as f:
        r = f.run(0)
        for k in (1, 2, 3):
            for c in CH:
                try:
                    tr = r.call(f"Root/Main/SyncUnit[{k}]/{c}/0/1", sep="/")
                    out[(k, c)] = (np.asarray(tr.domain.data, float), np.asarray(tr.data, float))
                except Exception:
                    pass
    return out


def main():
    A = read(sys.argv[1])
    if not A:
        print("no SyncUnit channels")
        return
    t = A[(1, "VIT")][0]
    n20 = int(round(0.02 / (t[1] - t[0])))
    print(f"{sys.argv[1]}\n  t = {t[0]:.3f}..{t[-1]:.3f} s, dt = {(t[1] - t[0]) * 1e6:.0f} us, n = {t.size}")
    for k in sorted({k for k, _ in A}):
        print(f"  SyncUnit[{k}]")
        for lo, hi in W:
            m = (t >= lo) & (t <= hi)
            row = []
            for c in CH:
                if (k, c) not in A:
                    continue
                y = A[(k, c)][1]
                if c == "Wspd":
                    y = mm(y, n20) / 2 / np.pi
                    row.append(f"f {y[m].mean():.5f} Hz (p-p {np.ptp(y[m]) * 1000:.2f} mHz)")
                else:
                    row.append(f"{c} {y[m].mean():+.5f}")
            print(f"    {lo:4.1f}-{hi:4.1f} s: " + ", ".join(row))
    if len(sys.argv) > 2:
        B = read(sys.argv[2])
        print(f"\nvs {sys.argv[2]}")
        for key in sorted(A):
            if key not in B:
                print(f"  {key}: missing in reference")
                continue
            ta, ya = A[key]
            tb, yb = B[key]
            n = min(ya.size, yb.size)
            if ya.size != yb.size:
                print(f"  {key}: length {ya.size} vs {yb.size} (first {n} compared)")
            d = np.abs(ya[:n] - yb[:n])
            print(f"  {key}: max|diff| {d.max():.3e} at t={ta[int(d.argmax())]:.4f}  (rms {np.sqrt(np.mean(ya[:n] ** 2)):.4g})")


if __name__ == "__main__":
    main()
