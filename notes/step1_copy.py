import os, shutil, json, time
import mhi.pscad as p

BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
SRC = os.path.join(BASE, "ieee_39_bus.pscx")
DST = os.path.join(BASE, "Spanish_grid_model.pscx")

if not os.path.exists(DST):
    shutil.copy2(SRC, DST)
    print("copied ->", DST)
else:
    print("already exists:", DST)

app = p.connect()
print("PSCAD", app.version)

names = [pr['name'] if isinstance(pr, dict) else pr.name for pr in app.projects()]
print("open projects:", names)

if 'Spanish_grid_model' not in names:
    app.load(DST)
    time.sleep(2)

pr = app.project('Spanish_grid_model')
print("project:", pr.name)
print("dir:", pr.directory)

# project parameters
try:
    pars = pr.parameters()
    print("--- project parameters ---")
    for k, v in pars.items():
        print(f"  {k!r}: {v!r}")
except Exception as e:
    print("param err", e)
