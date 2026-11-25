import mhi.psout as ps
import os
BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
f = os.path.join(BASE, "Spanish_grid_model.gf81_x86", "Spanish_grid_model.psout")
r = ps.File(f)
print("num_runs", r.num_runs)
for run in r.runs:
    print("run id", run.id, "num_traces", run.num_traces)
    print("  paths", run.trace_paths)
    for tr in run.traces:
        d = tr.data
        print("   ", tr.id, type(d).__name__, getattr(d, 'shape', len(d)))
        try:
            print("      first/last:", d[0][:3] if hasattr(d[0], '__len__') else d[0], d[-1][:3] if hasattr(d[-1], '__len__') else d[-1])
        except Exception as e:
            print("      err", e)
