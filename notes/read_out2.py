import mhi.psout as ps, os, numpy as np
BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
f = os.path.join(BASE, "Spanish_grid_model.gf81_x86", "Spanish_grid_model.psout")
r = ps.File(f)
run = r.run(0)
for tr, path in run.trace_paths():
    try:
        arr = np.asarray(tr.data, dtype=float).ravel()
    except Exception:
        continue
    if len(arr) < 100:
        continue
    print(f"{str(tr.id)[:60]:62s} n={len(arr):5d} min={arr.min():11.4f} max={arr.max():11.4f} last={arr[-1]:11.4f}")
