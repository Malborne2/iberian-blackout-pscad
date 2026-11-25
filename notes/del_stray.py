"""Remove the stray probe bus (grid 97,134) left over from probe_geom.py, then save+unload."""
import time
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

n = 0
for c in list(main.components()):
    try:
        b = c.bounds
    except Exception:
        continue
    if (b.left, b.top) == (97, 134):
        log('deleting', type(c).__name__, (b.left, b.top))
        c.delete()
        n += 1
log('deleted', n)

pr.save()
pr.unload()
log('saved + unloaded')
