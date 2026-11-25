import sys
import numpy as np
import mhi.psout
PS = sys.argv[1]
with mhi.psout.File(PS) as f:
    r = f.run(0)
    for ch in ("Root/Main/PG/0/1", "Root/Main/QG/0/1", "Root/Main/IDC/0/1"):
        try:
            tr = r.call(ch, sep="/")
        except Exception as e:
            print(ch, "missing")
            continue
        t = np.asarray(tr.domain.data, float); y = np.asarray(tr.data, float)
        m = t >= max(0, t[-1] - 0.5)
        print("%-22s mean(last 0.5 s) %+10.4f  min %+10.4f max %+10.4f" % (ch[10:], y[m].mean(), y.min(), y.max()))
