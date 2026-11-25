"""Build the project and print only the error/warning summary."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mhi.pscad as p
from dlgwatch import Watcher

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
w = Watcher(9876)
w.start()
t0 = time.time()
b = pr.build()
log('build', 'OK' if b is not None else 'FAILED', round(time.time() - t0, 1), 's')
w.stop()

msgs = pr.messages()
errs = [m for m in msgs if str(m.status).lower().startswith('err')]
print('messages', len(msgs), 'errors', len(errs))
seen = {}
for m in errs:
    k = (m.text, m.name)
    seen[k] = seen.get(k, 0) + 1
for (t, n), c in seen.items():
    print('  ERR x%d [%s] %s' % (c, n, t))
ws = {}
for m in msgs:
    if 'warn' in str(m.status).lower() and 'Position is exactly' not in m.text:
        ws[m.text] = ws.get(m.text, 0) + 1
print('other warnings', len(ws))
for t, c in list(ws.items())[:20]:
    print('  WARN x%d %s' % (c, t[:160]))
