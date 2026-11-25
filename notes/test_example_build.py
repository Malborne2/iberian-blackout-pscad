"""Load one of PSCAD's own example projects and try to build it (tests whether this
licence can compile synchronous machines at all)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mhi.pscad as p
from dlgwatch import Watcher

EX = r'C:\Users\Public\Documents\PSCAD\5.1.0\Examples\sync_machines\sync_multiplemachines.pscx'
app = p.connect()
print('projects before', [x['name'] for x in app.projects()])
app.load(EX)
name = os.path.splitext(os.path.basename(EX))[0]
pr = app.project(name)
w = Watcher(9876)
w.start()
before = len(pr.messages())
t0 = time.time()
b = pr.build()
print('build finished in %.1f s' % (time.time() - t0))
w.stop()
msgs = pr.messages()[before:]
errs = [m for m in msgs if str(m.status).lower().startswith('err')]
print('new messages', len(msgs), 'errors', len(errs))
for m in errs[:10]:
    print('  ', m.text[:200])
