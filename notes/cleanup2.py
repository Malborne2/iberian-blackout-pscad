"""Remove leftover probe components (stray T32 + pilot leftovers)."""
import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

n = 0
for c in main.components():
    nm = ''
    try:
        nm = str(c.parameters().get('Name', ''))
    except Exception:
        pass
    if nm in ('T32',) or nm.startswith(('T_C', 'RES_C', 'REACT_C', 'V_C')):
        log('del', nm, c.iid, c.bounds.left, c.bounds.top)
        c.delete()
        n += 1
log('deleted', n)
pr.save()
