"""Check the new Ph9 channel: angle vs time, and the meter's Vd and Pd against neighbouring data."""
import sys
import numpy as np
import mhi.psout

PS = sys.argv[1]
with mhi.psout.File(PS) as f:
    r = f.run(0)

    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)

    for ch in ("Root/Main/Ph9/0/1", "Root/Main/Ph39/0/1", "Root/Main/Ph31/0/1",
               "Root/Main/multimeter[1]/4/Vd", "Root/Main/multimeter[1]/2/Pd"):
        try:
            t, y = get(ch)
        except Exception as e:
            print(ch, "MISSING", e)
            continue
        m = t >= max(0.0, t[-1] - 0.2)
        print("%-32s t %.3f..%.3f  mean(last 0.2 s) %+9.4f  min %+9.4f max %+9.4f" % (
            ch.split("/")[-3] + "/" + ch.split("/")[-2], t[0], t[-1], y[m].mean(), y.min(), y.max()))
