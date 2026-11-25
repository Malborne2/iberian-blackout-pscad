import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')
print('canvas size', main.size)
xf = [c for c in main.components() if 'xfmr-3p2w' in str(getattr(c, 'definition', ''))][0]
pp = xf.port('G1')
print('port attrs', [a for a in dir(pp) if not a.startswith('_')])
for a in ('location', 'point', 'x', 'y', 'name', 'count'):
    if hasattr(pp, a):
        print('  ', a, getattr(pp, a))
print('comp attrs', [a for a in dir(xf) if not a.startswith('_')][:40])
print('bounds', xf.bounds)
print('position?', getattr(xf, 'position', None))
