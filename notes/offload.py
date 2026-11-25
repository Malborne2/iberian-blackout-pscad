"""Save + unload the project so the .pscx can be edited safely."""
import time
import mhi.pscad as p

def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

app = p.connect()
pr = app.project('Spanish_grid_model')
pr.save()
pr.unload()
log('saved + unloaded')
