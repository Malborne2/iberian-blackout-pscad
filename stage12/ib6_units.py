r"""S26: identify SyncUnit[i] by matching |POUT*Sbase| to the breaker meters PBK30/31/32/37 (rule L2).

usage: python stage12\ib6_units.py <psout> [w0 w1]
Prints each instance's Sbase-scaled P/Q/V and the four breaker-meter powers, plus the best match and
its residual, so the mapping is measured, not assumed.
"""
import sys
import numpy as np
import mhi.psout

SB = {1: 15292.0, 2: 12838.0, 3: 6113.0, 4: 13548.0, 5: 200000.0}
ps = sys.argv[1]
w0, w1 = (float(x) for x in sys.argv[2:4]) if len(sys.argv) > 3 else (50.0, 52.0)
r = mhi.psout.File(ps).run(0)


def get(ch):
    tr = r.call(ch, sep="/")
    return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)


t, _ = get("Root/Main/SyncUnit[1]/Wspd/0/1")
w = (t >= w0) & (t <= w1)
P = {}
for i in SB:
    P[i] = get(f"Root/Main/SyncUnit[{i}]/POUT/0/1")[1][w].mean() * SB[i]
B = {}
for b in ("30", "31", "32", "37"):
    B[b] = get(f"Root/Main/PBK{b}/0/1")[1][w].mean()

print(f"# {ps}  window {w0}-{w1} s")
print("instance   Sbase    P_mean[MW]   Q[Mvar]   V[pu]      |   PBK[mW]")
for i in SB:
    q = get(f"Root/Main/SyncUnit[{i}]/QOUT/0/1")[1][w].mean() * SB[i]
    v = get(f"Root/Main/SyncUnit[{i}]/VIT/0/1")[1][w].mean()
    print(f"  [{i}]     {SB[i]:8.0f}  {P[i]:9.1f}  {q:9.0f}  {v:8.4f}")
print("breakers: " + "  ".join(f"PBK{b} {B[b]:+8.1f}" for b in B))
print("\nbest match (|P_i| vs |PBK_b|) and residual:")
for i in SB:
    if i == 5:
        print(f"  [{i}] -> France (no breaker meter on the tie side of BRKFR)")
        continue
    b = min(B, key=lambda k: abs(abs(B[k]) - abs(P[i])))
    print(f"  [{i}] -> PBK{b}: |P| {abs(P[i]):.1f} vs {abs(B[b]):.1f}  diff {abs(B[b])-abs(P[i]):+.1f} MW")
