import sys
from pathlib import Path

import numpy as np
from PIL import Image

a = np.asarray(Image.open(sys.argv[1]).convert("RGB"))
h, w, _ = a.shape
r, g, b = (a[..., i].astype(int) for i in range(3))
grey = (abs(r - g) < 12) & (abs(g - b) < 12) & (r < 215)
rows, cols = grey.sum(axis=1), grey.sum(axis=0)


def groups(idx):
    out, run = [], [idx[0]]
    for v in idx[1:]:
        if v - run[-1] <= 2:
            run.append(v)
        else:
            out.append(run); run = [v]
    out.append(run)
    return out


hr = [y for y in range(h) if rows[y] > 0.7 * w]
vc = [x for x in range(w) if cols[x] > 0.25 * h]
print("horizontal lines (y, count):")
for gg in groups(hr):
    y = int(np.mean(gg))
    print(f"  y={y:5d}  n={len(gg)}  grey={rows[y]}")
print("vertical lines (x, count):")
for gg in groups(vc):
    x = int(np.mean(gg))
    print(f"  x={x:5d}  n={len(gg)}  grey={cols[x]}")
