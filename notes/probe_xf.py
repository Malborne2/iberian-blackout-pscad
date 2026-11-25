import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')
comps = main.components()
xf = [c for c in comps if 'xfmr-3p2w' in str(getattr(c, 'definition', ''))]
log('n xfmr', len(xf))
for c in xf[:3]:
    log('---', c.iid, 'bounds', c.bounds())
    for k, v in c.ports().items():
        log('   port', k, v.location)
