"""WP5 state table: collector-bus voltages, plant fleet, machines, from one .psout.

usage: python stage3\\wp5_state.py <psout> [t0 t1]

Instance identification (rule L2).  `RES_Plant[n]` is NOT in the .pscx document order (measured in S19b:
`stage3\\plant_order.py` on the S19 bus-38 gate run, then matched against the Pref values of that run's own
gate tables).  The mapping below is that measurement; the script re-checks it every time by testing that

  * every plant of one bus has the same VDF (1 %), and
  * its ID matches the Pref the placement script gave it (0.648 for bus 34's seven, 0.887-0.900 elsewhere)

and prints **FAIL** if either check breaks, so a changed build cannot silently re-label the table.

  n : bus (Sbase MVA)
  1 : 33 (400)      18 : 33 (2550)
  2 : 36 (172)       3 : 36 (167)       4 : 36 (2402)
  5 : 34 (647)       6 : 34 (162)       7 : 34 (566)       8 : 34 (405)
  9 : 34 (339)      10 : 34 (236)      11 : 34 (1194)
 12 : 35 (612)      13 : 35 (130)      14 : 35 (2498)
 15 : 38 (589)      16 : 38 (348)      17 : 38 (3132)

Evidence for the map (S19b): the ids printed by `plant_order.py` on `iberia4_b38_20s.psout` at 19-20 s are,
per group, 0.8952/0.8980/0.8995 (bus 36's Pref 0.8953/0.8982/0.8997), 0.6478/0.6446/0.6476/0.6472/0.6479/
0.6481/0.6479 (bus 34's seven, in plant-list order), 0.8985/0.8990/0.8998 (bus 35), 0.8997/0.8993/0.8996
(bus 38), 0.8899 and 0.8874 (bus 33: 400 MVA Granada -> 154 MW and 2550 MVA bulk -> 981 MW at 0.4334 pu).
"""
import sys
import numpy as np
import mhi.psout

# n -> (bus label, Sbase MVA)
NBUS = {1: ("33", 400.0), 2: ("36", 172.0), 3: ("36", 167.0), 4: ("36", 2402.0),
        5: ("34", 647.0), 6: ("34", 162.0), 7: ("34", 566.0), 8: ("34", 405.0),
        9: ("34", 339.0), 10: ("34", 236.0), 11: ("34", 1194.0),
        12: ("35", 612.0), 13: ("35", 130.0), 14: ("35", 2498.0),
        15: ("38", 589.0), 16: ("38", 348.0), 17: ("38", 3132.0),
        18: ("33", 2550.0)}
import os
# S23: ib5 uprated every plant x1.30 (stage11/prepare_ib5.py). Set KPLANT=1 for pre-ib5 PSOUTs.
KPLANT = float(os.environ.get("KPLANT", "1.30"))
NBUS = {k: (b, s * KPLANT) for k, (b, s) in NBUS.items()}
BUSES = ["33", "34", "35", "36", "38"]
MACH_SBASE = {1: 6113.0, 2: 13548.0, 3: 15292.0, 4: 12838.0, 5: 200000.0}

PS = sys.argv[1]
T0 = float(sys.argv[2]) if len(sys.argv) > 2 else None
T1 = float(sys.argv[3]) if len(sys.argv) > 3 else None


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


def main():
    with mhi.psout.File(PS) as f:
        r = f.run(0)

        def get(p):
            tr = r.call(p, sep="/")
            return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

        n_inst = 0
        while True:
            try:
                get(f"Root/Main/RES_Plant[{n_inst + 1}]/ID/0/1")
                n_inst += 1
            except Exception:
                break
        n_mach = 0
        while True:
            try:
                get(f"Root/Main/SyncUnit[{n_mach + 1}]/Wspd/0/1")
                n_mach += 1
            except Exception:
                break
        t = get("Root/Main/RES_Plant[1]/ID/0/1")[0]
        n20 = int(round(0.02 / (t[1] - t[0])))
        t0 = T0 if T0 is not None else max(0.0, t[-1] - 1.0)
        t1 = T1 if T1 is not None else t[-1]
        w = (t >= t0) & (t <= t1)
        print(f"{PS}\n  t = {t[0]:.3f}..{t[-1]:.3f} s, window {t0:.2f}-{t1:.2f} s, "
              f"{n_inst} plants, {n_mach} machines")
        if n_inst != len(NBUS):
            print(f"  FAIL: {n_inst} plants, map has {len(NBUS)}")
            return

        rows = []
        for k in range(1, n_inst + 1):
            vd = get(f"Root/Main/RES_Plant[{k}]/VD/0/1")[1]
            vdf = get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1]
            idk = get(f"Root/Main/RES_Plant[{k}]/ID/0/1")[1]
            iqk = get(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1]
            try:
                vq = get(f"Root/Main/RES_Plant[{k}]/VQ/0/1")[1]
            except Exception:
                vq = np.zeros_like(vd)
            try:
                trip = get(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")[1].max()
            except Exception:
                trip = 0.0
            bus, sb = NBUS[k]
            rows.append(dict(k=k, bus=bus, sb=sb,
                             vdf=vdf[w].mean(), id=idk[w].mean(), iq=iqk[w].mean(),
                             p=mm(vd * idk + vq * iqk, n20)[w].mean() * sb,
                             q=mm(vd * iqk - vq * idk, n20)[w].mean() * sb, trip=trip))

        # checks (L2)
        ok = True
        for b in BUSES:
            g = [x for x in rows if x["bus"] == b]
            v = np.array([x["vdf"] for x in g]); ids = np.array([x["id"] for x in g])
            if v.max() - v.min() > 0.01 * v.mean():
                ok = False
                print(f"  FAIL: bus {b}: VDF spread {v.min():.4f}..{v.max():.4f}")
            expect = 0.648 if b == "34" else 0.885
            if b != "34" and ids.min() < expect - 0.01:
                ok = False
                print(f"  FAIL: bus {b}: id {ids.min():.4f} below the expected range")
            if b == "34" and (ids.max() > 0.66 or ids.min() < 0.63):
                ok = False
                print(f"  FAIL: bus 34: id {ids.min():.4f}..{ids.max():.4f} outside 0.63-0.66")

        print(f"\n{'bus':4} {'n':>2} {'rating':>7} {'VDF pu':>8} {'mean id':>8} {'mean iq':>8} "
              f"{'P [MW]':>9} {'Q [Mvar]':>9} {'MW/Sbase':>9}")
        tp = tq = 0.0
        for b in BUSES:
            g = [x for x in rows if x["bus"] == b]
            sb = sum(x["sb"] for x in g)
            p = sum(x["p"] for x in g); q = sum(x["q"] for x in g)
            tp += p; tq += q
            print(f"{b:4} {len(g):2d} {sb:7.0f} {np.mean([x['vdf'] for x in g]):8.4f} "
                  f"{np.mean([x['id'] for x in g]):8.4f} {np.mean([x['iq'] for x in g]):+8.4f} "
                  f"{p:9.1f} {q:9.1f} {p / sb:9.4f}")
        print(f"{'TOT':4} {n_inst:2d} {sum(NBUS[k][1] for k in NBUS):7.0f} {'':8} {'':8} {'':8} "
              f"{tp:9.1f} {tq:9.1f}")
        print(f"  checks: {'PASS' if ok else 'FAIL'}; trips max {max(x['trip'] for x in rows):.2f}")

        print(f"\n{'machine':8} {'Sbase':>7} {'VIT':>7} {'POUT':>8} {'QOUT':>8} {'P [MW]':>9} "
              f"{'Q [Mvar]':>9} {'f Hz':>9} {'f p-p mHz':>10}")
        mp = mq = 0.0
        for k in range(1, n_mach + 1):
            vit = get(f"Root/Main/SyncUnit[{k}]/VIT/0/1")[1][w].mean()
            po = get(f"Root/Main/SyncUnit[{k}]/POUT/0/1")[1][w].mean()
            qo = get(f"Root/Main/SyncUnit[{k}]/QOUT/0/1")[1][w].mean()
            ws = get(f"Root/Main/SyncUnit[{k}]/Wspd/0/1")[1]
            fs = mm(ws, n20) / 2 / np.pi
            sb = MACH_SBASE.get(k, 0.0)
            mp += po * sb; mq += qo * sb
            print(f"[{k}]      {sb:7.0f} {vit:7.4f} {po:+8.4f} {qo:+8.4f} {po * sb:9.1f} "
                  f"{qo * sb:9.1f} {fs[w].mean():9.5f} {np.ptp(fs[w]) * 1000:10.1f}")
        print(f"{'TOTAL':8} {'':7} {'':7} {'':8} {'':8} {mp:9.1f} {mq:9.1f}")
        print(f"\nbalance: machines {mp:.0f} MW + plants {tp:.0f} MW = {mp + tp:.0f} MW "
              f"(load {25237.6 * (0 if False else 1):.0f} MW at 1.0 pu)")


if __name__ == "__main__":
    main()
