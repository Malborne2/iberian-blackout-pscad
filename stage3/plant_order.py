import sys
import numpy as np
import mhi.psout

PS = sys.argv[1]
W = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (19.0, 20.0)

with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    n = 0
    while True:
        try:
            get(f"Root/Main/RES_Plant[{n + 1}]/ID/0/1")
            n += 1
        except Exception:
            break
    t = get("Root/Main/RES_Plant[1]/ID/0/1")[0]
    w = (t >= W[0]) & (t <= W[1])
    print(f"{PS}  {n} plants, window {W[0]}-{W[1]} s")
    print("  n   VDF     ID      IQ")
    for k in range(1, n + 1):
        vdf = get(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1][w].mean()
        idc = get(f"Root/Main/RES_Plant[{k}]/ID/0/1")[1][w].mean()
        iq = get(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1][w].mean()
        print("%3d  %.4f  %.4f  %+.4f" % (k, vdf, idc, iq))
