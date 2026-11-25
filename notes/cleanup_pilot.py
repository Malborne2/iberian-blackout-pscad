"""Delete any components of the pilot collector group (by name / region)."""
import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

PREFIX = ('T_C', 'RES_C', 'REACT_C', 'V_C')
n = 0
for c in main.components():
    nm = ''
    try:
        nm = str(c.parameters().get('Name', ''))
    except Exception:
        pass
    if nm.startswith(PREFIX):
        log('del', nm, c.iid)
        c.delete()
        n += 1
        continue
    b = c.bounds
    if b.left >= 18 and b.top >= 105 and b.right <= 30 and b.bottom <= 125:
        log('del bus/region', type(c).__name__, (b.left, b.top, b.right, b.bottom))
        c.delete()
        n += 1
log('deleted', n)
pr.save()
