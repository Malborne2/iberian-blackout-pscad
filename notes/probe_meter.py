import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')
comps = main.components()

kinds = {}
for c in comps:
    k = getattr(c, 'definition', None)
    k = str(k) if k is not None else type(c).__name__
    kinds[k] = kinds.get(k, 0) + 1
log('kinds', kinds)

meters = [c for c in comps if str(getattr(c, 'definition', '')).endswith('multimeter')]
log('meters', len(meters))
for c in meters[:3]:
    ps = c.parameters()
    log('---', c.iid, ps.get('S'))
    for nm, pp in c.ports().items():
        log('    port', nm, pp.location)
