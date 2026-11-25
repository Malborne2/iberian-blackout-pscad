"""List components whose x position is >= a threshold (grid units)."""
import sys
import mhi.pscad as p

thr = int(sys.argv[1]) if len(sys.argv) > 1 else 1400
app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')
rows = []
for c in main.components():
    b = c.bounds
    if b.left >= thr:
        rows.append((b.left, b.top, str(getattr(c, 'definition', ''))))
rows.sort()
for r in rows:
    print(r)
print('total', len(rows))
