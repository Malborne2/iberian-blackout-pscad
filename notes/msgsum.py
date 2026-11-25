"""Print all build messages grouped by (name, status) with counts."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

app, pr = ptools.ensure_loaded()
c = collections.Counter()
for m in pr.messages():
    key = (str(m.name), str(m.status), str(m.text)[:90])
    c[key] += 1
for (nm, st, tx), n in c.most_common(25):
    print('%3d  [%s] %-34s %s' % (n, st, nm, tx))
