import time
import mhi.pscad as p

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

dl = main.create_component('master:datalabel', 1500, 2450, Name='TEST_SIG')
pg = main.create_component('master:pgb', 1600, 2450, Name='TEST_SIG')
log('dl port', dl.port('A').location)
log('pg port', pg.port('Signl').location)
try:
    w = main.create_connection(dl.port('A'), pg.port('Signl'))
    log('connection ->', w)
except Exception as e:
    log('conn err', type(e).__name__, e)
pr.save()
time.sleep(1)
dl.delete()
pg.delete()
log('deleted')
