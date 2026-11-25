"""build + run + read in one go.

Run: python br.py sb11 [t1 t2 ...]
"""
import sys

import pscad_ops as P

PRJ = sys.argv[1]
TIMES = [float(x) for x in sys.argv[2:]] or [0.05, 0.2, 0.5, 1, 2, 3, 5]
P.connect()
n0 = len(P.messages(PRJ)["messages"])
P.app().project(PRJ).build()
new = P.messages(PRJ)["messages"][n0:]
errs = [x["text"] for x in new if x["status"].startswith("error")]
if errs:
    for t in errs[:8]:
        print("E:", t.encode("ascii", "replace").decode())
    sys.exit("build failed")
P.run(PRJ, wait=True, poll=1.0, timeout=3600)
import time

psout = P.find_output_file(PRJ)
for _ in range(20):
    try:
        chs = [c[1] for c in P.list_output_channels(psout) if not c[1].endswith("Domain")]
        break
    except Exception:
        time.sleep(1.0)
else:
    sys.exit("could not open " + psout)
series = {c: P.trace_series(psout, c) for c in chs}
print("t".rjust(6) + "".join(f"{c.split('/')[-3][:11]:>13}" for c in chs))
for t in TIMES:
    row = f"{t:>6.2f}"
    for c, s in series.items():
        row += f"{min(s, key=lambda p: abs(p[0] - t))[1]:>13.5g}"
    print(row)
