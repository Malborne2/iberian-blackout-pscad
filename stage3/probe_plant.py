"""Print plant dq quantities at several instants (what happened in the bus-34 run)."""
import sys
import numpy as np
import mhi.psout

PS = sys.argv[1]
INSTS = [int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["1", "5"])]
with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    for k in INSTS:
        print(f"=== RES_Plant[{k}]")
        ch = {}
        for c in ("VD", "VQ", "ID", "IQ", "VDF", "TRIP"):
            try:
                ch[c] = get(f"Root/Main/RES_Plant[{k}]/{c}/0/1")
            except Exception:
                pass
        t = ch["VD"][0]
        for tc in (0.05, 0.2, 0.4, 0.6, 0.8, 1.0, 2.0, 5.0, 10.0, 15.0, 19.5):
            i = int(np.argmin(np.abs(t - tc)))
            print(f"  t={t[i]:7.3f} VD {ch['VD'][1][i]:+9.4f} VQ {ch['VQ'][1][i]:+9.4f} "
                  f"ID {ch['ID'][1][i]:+8.4f} IQ {ch['IQ'][1][i]:+8.4f} VDF {ch['VDF'][1][i]:8.4f}")
    # bus voltages on the machine side for reference
    print("\n=== machines")
    for k in range(1, 6):
        try:
            ts, vit = get(f"Root/Main/SyncUnit[{k}]/VIT/0/1")
            for tc in (0.6, 2.0, 10.0, 19.5):
                i = int(np.argmin(np.abs(ts - tc)))
                print(f"  [{k}] t={ts[i]:6.2f} VIT {vit[i]:.4f}", end="")
            print()
        except Exception:
            pass
