"""Build + run the model, capturing dialogs and the build messages."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mhi.pscad as p
from dlgwatch import Watcher

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

T = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0

app = p.connect()
pr = app.project('Spanish_grid_model')
log('PlotType', pr.parameters()['PlotType'], 'duration', pr.parameters()['time_duration'])

w = Watcher(9876)
w.start()

pr.parameters(time_duration=T)
t0 = time.time()
log('build ...')
b = pr.build()
log('build done in', round(time.time() - t0, 1), 's')
try:
    msg = b.message()
    print(msg[:4000])
except Exception as e:
    print('build msg err', e)

t0 = time.time()
log('run ...')
r = pr.run()
log('run done in', round(time.time() - t0, 1), 's')
w.stop()
log('dialogs seen:', getattr(w, 'seen', '?'))
