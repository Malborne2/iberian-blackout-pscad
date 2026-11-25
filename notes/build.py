"""Build and print every error/warning of this build (pr.messages() is per-build)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
from dlgwatch import Watcher

app, pr = ptools.ensure_loaded()
w = Watcher(9876)
w.start()
t0 = time.time()
pr.build()
ptools.log('build finished in', round(time.time() - t0, 1), 's')
w.stop()

msgs = pr.messages()
errs = [m for m in msgs if str(m.status).lower().startswith('err')]
ws = [m for m in msgs if 'warn' in str(m.status).lower()]
print('messages', len(msgs), 'ERRORS', len(errs), 'warnings', len(ws))
seen = {}
for m in errs:
    k = (m.text, m.name)
    seen[k] = seen.get(k, 0) + 1
for (t, n), c in seen.items():
    print('  ERR x%d [%s] %s' % (c, n, t))
for m in ws[:10]:
    print('  WARN [%s] %s' % (m.name, m.text))

exe = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'Spanish_grid_model.gf81_x86', 'Spanish_grid_model.exe')
ok = os.path.exists(exe)
ptools.log('exe', 'present' if ok else 'MISSING',
           time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(exe))) if ok else '')
