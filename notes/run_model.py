import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import mhi.pscad as p
from dlgwatch import Watcher

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

T = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0

app = p.connect()
pr = app.project('Spanish_grid_model')
log('params', pr.parameters()['PlotType'], pr.parameters()['time_duration'])

w = Watcher(9876)
w.start()

pr.parameters(time_duration=T)
t0 = time.time()
log('build...')
b = pr.build()
log('build done', round(time.time() - t0, 1), 's')
try:
    print(b.message()[:2000])
except Exception as e:
    print('build msg err', e)

t0 = time.time()
log('run...')
r = pr.run()
log('run done', round(time.time() - t0, 1), 's', r.status() if hasattr(r, 'status') else '')

w.stop()
log('dialogs seen:', w.seen)
