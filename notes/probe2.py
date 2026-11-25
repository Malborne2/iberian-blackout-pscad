import time, traceback
def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)

log("import")
import mhi.pscad as p
log("connect")
app = p.connect()
pr = app.project('Spanish_grid_model')
log("canvas")
main = pr.canvas('Main')
log("components")
cs = main.components()
log("n =", len(cs))
for i in range(0, 12):
    c = cs[i]
    log(i, "type", type(c).__name__)
    try:
        log(i, "id", c.id)
    except Exception as e:
        log(i, "id ERR", e)
    try:
        log(i, "loc", list(c.location))
    except Exception as e:
        log(i, "loc ERR", e)
    try:
        log(i, "orient", c.orient)
    except Exception as e:
        log(i, "orient ERR", e)
    try:
        log(i, "defn", c.definition.name)
    except Exception as e:
        log(i, "defn ERR", e)
    try:
        ps = c.parameters()
        log(i, "params n=", len(ps))
    except Exception as e:
        log(i, "params ERR", e)
log("done")
