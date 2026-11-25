import time, os, json
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
import mhi.pscad as p
BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
app = p.connect()
pr = app.project('Spanish_grid_model')
main = pr.canvas('Main')

DEFNS = ['master:xfmr-3p2w', 'master:fixed_load', 'master:reactive_load', 'master:capacitor',
         'master:const', 'master:breaker3', 'master:switch', 'master:voltmeter',
         'master:freq-meas', 'master:tbreakn', 'master:compar', 'master:gain',
         'master:ground', 'master:pgb', 'master:datalabel', 'master:multimeter']

out = {}
for d in DEFNS:
    try:
        c = main.create_component(d, 2000, 1900, 0)
    except Exception as e:
        log(d, "CREATE ERR", e)
        out[d] = {"error": str(e)}
        continue
    try:
        ports = c.ports()
        info = {}
        for nm, pp in ports.items():
            info[nm] = [pp.location[0], pp.location[1], pp.count]
        out[d] = {"iid": c.iid, "ports": info, "params": {k: str(v) for k, v in c.parameters().items()}}
        log(d, info)
    except Exception as e:
        log(d, "PORT ERR", e)
        out[d] = {"error": str(e)}
    try:
        c.delete()
    except Exception as e:
        log(d, "delete err", e)

with open(os.path.join(BASE, 'notes', 'ports.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)
log("written")
