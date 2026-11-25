"""Print the decimated multimeter samples in the gate window for two runs."""
import sys
import numpy as np
import mhi.psout

A, B = sys.argv[1], sys.argv[2]
CH = sys.argv[3] if len(sys.argv) > 3 else "Root/Main/multimeter[9]/2/Pd"
for p in (A, B):
    with mhi.psout.File(p) as f:
        r = f.run(0)
        tr = r.call(CH, sep="/")
        t = np.asarray(tr.domain.data, float)
        y = np.asarray(tr.data, float)
    m = (t >= 2.0) & (t <= 3.0)
    print(p.rsplit("\\", 1)[-1], "n_in_window", m.sum())
    for a, b in zip(t[m], y[m]):
        print(f"   {a:9.5f} {b:11.6f}")
