"""Restore the V_G39 signal wire (accidentally removed during an XML cleanup)."""
import time
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
app.load('Spanish_grid_model.pscx')
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

dl = pg = None
for c in main.components():
    b = c.bounds
    if (b.left, b.top) == (1500, 760):
        dl = c
    elif (b.left, b.top) == (1580, 760):
        pg = c
log('datalabel', dl, 'pgb', pg)
if dl is None or pg is None:
    raise SystemExit('components not found')

log('dl port', dl.port('A').location, 'pg port', pg.port('Signl').location)
log('conn', main.create_connection(dl.port('A'), pg.port('Signl')))
pr.save()
log('saved')
