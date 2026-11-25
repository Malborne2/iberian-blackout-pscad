"""Run the model (only report messages produced by this run)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
from dlgwatch import Watcher

T = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0

app, pr = ptools.ensure_loaded()
pr.parameters(time_duration=T)
before = len(pr.messages())
w = Watcher(9876)
w.start()
t0 = time.time()
r = pr.run()
ptools.log('run finished in', round(time.time() - t0, 1), 's')
w.stop()
msgs = pr.messages()[before:]
errs = [m for m in msgs if str(m.status).lower().startswith('err')]
print('new messages', len(msgs), 'errors', len(errs))
for m in errs[:10]:
    print('  ', m.text[:200])
