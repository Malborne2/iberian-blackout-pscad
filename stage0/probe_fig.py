"""Locate the plot frame and the curve colours in a rendered report page."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

p = Path(sys.argv[1])
im = Image.open(p).convert("RGB")
a = np.asarray(im)
h, w, _ = a.shape
print("image", w, h)

# grey-ish dark pixels = frame / axis lines
r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
grey = (abs(r - g) < 12) & (abs(g - b) < 12) & (r < 210)

rows = grey.sum(axis=1)
cols = grey.sum(axis=0)
print("top rows by grey count:")
for y in np.argsort(rows)[-12:][::-1]:
    print(f"  y={y:5d} grey={rows[y]:5d}  ({rows[y]/w:.2f} of width)")
print("top cols by grey count:")
for x in np.argsort(cols)[-12:][::-1]:
    print(f"  x={x:5d} grey={cols[x]:5d}  ({cols[x]/h:.2f} of height)")

# saturated colours inside a guess region (whole page for now)
sat = (a.max(axis=2).astype(int) - a.min(axis=2).astype(int)) > 60
ys, xs = np.where(sat)
print("saturated pixel bbox", xs.min(), xs.max(), ys.min(), ys.max(), "count", sat.sum())
from collections import Counter
c = Counter(map(tuple, a[sat][::7]))
print("most common saturated colours:")
for col, n in c.most_common(15):
    print("   ", col, n)
