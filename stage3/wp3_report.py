"""WP3 gate report: one collector bus's plant fleet in a network run.

usage: python stage3\\wp3_report.py <psout> <bus> <name:Sbase[,name:Sbase...]>

Instances are found and identified by measurement (rule L2):
  * a run's RES_Plant instances are scanned by index but the ones belonging to <bus> are those whose
    VDF sits within 1 % of the bus's voltage (the bus voltage is 0.85-0.95 pu, other buses differ);
  * inside the bus, the instance with the largest P (per unit) is paired with the plant with the
    largest Sbase, and the P/Sbase ratios are printed so a wrong pairing is visible (they must agree
    to a few %: same bus voltage, same PF).
The multimeter of the bus is found by its Vd matching the plants' VDF, and used as the independent
meter (rule M3).
"""
import sys
import numpy as np
import mhi.psout

PS = sys.argv[1]
BUS = int(sys.argv[2])
SPEC = sys.argv[3] if len(sys.argv) > 3 else ""
PLANTS = [(x.split(":")[0].strip(), float(x.split(":")[1])) for x in SPEC.split(",") if x.strip()]

W1 = (5.0, 6.0)
W2 = (19.0, 20.0)


def mm(y, n):
    h = n // 2
    p = np.concatenate([np.full(h, y[0]), y, np.full(n - h - 1, y[-1])])
    return np.convolve(p, np.ones(n) / n, mode="valid")


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
    print(f"{n_inst} RES_Plant instances in {PS}")

    D = {}
    for k in range(1, n_inst + 1):
        for c in ("ID", "IQ", "VD", "VQ", "VDF", "TRIP", "THETA_TR"):
            try:
                D[(k, c)] = get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")
            except Exception:
                pass
    t = D[(1, "ID")][0]
    n20 = int(round(0.02 / (t[1] - t[0])))

    rows = []
    for k in range(1, n_inst + 1):
        if (k, "ID") not in D:
            continue
        vd, idc, iq = D[(k, "VD")][1], D[(k, "ID")][1], D[(k, "IQ")][1]
        vq = D[(k, "VQ")][1] if (k, "VQ") in D else np.zeros_like(vd)
        p_pu = mm(vd * idc + vq * iq, n20)
        q_pu = mm(vd * iq - vq * idc, n20)
        a, b = (t >= W1[0]) & (t <= W1[1]), (t >= W2[0]) & (t <= W2[1])
        rows.append(dict(k=k, id=idc[b].mean(), id1=idc[a].mean(), iq=iq[b].mean(), iq1=iq[a].mean(),
                         vd=vd[b].mean(), vdf=D[(k, "VDF")][1][b].mean(),
                         ppu=p_pu[b].mean(), qpu=q_pu[b].mean(), p1=p_pu[a].mean(),
                         idpp=np.ptp(idc[a]),
                         trip=D[(k, "TRIP")][1].max() if (k, "TRIP") in D else 0.0))

    # which instances belong to this bus?  VDF is the bus voltage; buses differ by >5 %
    vdfs = np.array([x["vdf"] for x in rows])
    # cluster them
    best, best_n = None, 0
    for v in vdfs:
        sel = [x["k"] for x in rows if abs(x["vdf"] - v) < 0.01 * v]
        if len(sel) > best_n:
            best, best_n = v, len(sel)
    mine = [x for x in rows if abs(x["vdf"] - best) < 0.01 * best]
    print(f"\nbus {BUS}: {len(mine)} instance(s) with VDF {best:.4f} pu "
          f"(other buses: {sorted(set(round(x['vdf'], 3) for x in rows if x not in mine))})")
    print(f"{'inst':>5} {'id 5-6':>8} {'id 19-20':>9} {'iq 5-6':>8} {'iq 19-20':>9} {'vd':>7} "
          f"{'vdf':>7} {'P pu':>7} {'Q pu':>8} {'TRIP':>5}")
    for x in mine:
        print(f"{x['k']:5d} {x['id1']:8.4f} {x['id']:9.4f} {x['iq1']:8.4f} {x['iq']:9.4f} "
              f"{x['vd']:7.4f} {x['vdf']:7.4f} {x['ppu']:7.4f} {x['qpu']:8.4f} {x['trip']:5.2f}")

    if PLANTS and len(PLANTS) == len(mine):
        order = sorted(mine, key=lambda x: -x["ppu"])
        spec = sorted(PLANTS, key=lambda s: -s[1])
        print(f"\n{'plant':10} {'Sbase':>7} {'id':>8} {'id ref':>8} {'P [MW]':>9} {'Q [Mvar]':>9} "
              f"{'P/Sbase':>8}")
        tot_p = tot_q = 0.0
        ratios = []
        for x, (nm, sb) in zip(order, spec):
            ref = x["id"]
            tot_p += x["ppu"] * sb
            tot_q += x["qpu"] * sb
            ratios.append(x["ppu"])
            print(f"{nm:10} {sb:7.0f} {x['id']:8.4f} {ref:8.4f} {x['ppu'] * sb:9.1f} "
                  f"{x['qpu'] * sb:9.1f} {x['ppu']:8.4f}")
        print(f"{'TOTAL':10} {'':7} {'':8} {'':8} {tot_p:9.1f} {tot_q:9.1f}")
        spread = (max(ratios) - min(ratios)) / max(abs(np.mean(ratios)), 1e-9) * 100
        print(f"  P/Sbase spread over the bus: {spread:.2f} %  (a wrong instance pairing shows up here)")
        # independent meter
        meters = {}
        for m in range(1, 10):
            try:
                meters[m] = (get(f"Root/Main/multimeter[{m}]/2/Pd"), get(f"Root/Main/multimeter[{m}]/3/Qd"),
                             get(f"Root/Main/multimeter[{m}]/4/Vd"))
            except Exception:
                pass
        meter, bestd = None, None
        for m, (_, _, (tm, vm)) in meters.items():
            v = vm[(tm >= W2[0]) & (tm <= W2[1])].mean()
            d = abs(v - best)
            if bestd is None or d < bestd:
                meter, bestd = m, d
        if meter is not None:
            (tm, pm), (_, qm), (_, vm) = meters[meter]
            s2 = (tm >= W2[0]) & (tm <= W2[1])
            print(f"  independent meter: multimeter[{meter}] Vd {vm[s2].mean():.4f} pu, "
                  f"Pd {pm[s2].mean():+.4f} pu, Qd {qm[s2].mean():+.4f} pu  (pu on 410.4 MVA)")
            print(f"    plant total in the same units: P {tot_p / 410.4:+.4f}, Q {tot_q / 410.4:+.4f} "
                  f"-> P residual {(tot_p / 410.4 + pm[s2].mean()):+.4f} pu "
                  f"({(tot_p / 410.4 + pm[s2].mean()) / (tot_p / 410.4) * 100:+.1f} % of the plant total)")
            print(f"    voltage agreement: |VDF - Vd| = {abs(best - vm[s2].mean()):.4f} pu")

    print("\nSyncUnit (15-20 s):")
    for k in range(1, 6):
        try:
            ts, ws = get(f"Root/Main/SyncUnit[{k}]/Wspd/0/1")
            _, vit = get(f"Root/Main/SyncUnit[{k}]/VIT/0/1")
            _, po = get(f"Root/Main/SyncUnit[{k}]/POUT/0/1")
            s2 = (ts >= 15) & (ts <= 20)
            fs = mm(ws, int(round(0.02 / (ts[1] - ts[0])))) / 2 / np.pi
            print(f"  [{k}] VIT {vit[s2].mean():.4f}  POUT {po[s2].mean():+.4f}  "
                  f"f {fs[s2].mean():.5f} Hz  p-p {np.ptp(fs[s2]) * 1000:.1f} mHz")
        except Exception:
            pass
