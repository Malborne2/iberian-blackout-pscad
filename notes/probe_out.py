import os
import mhi.psout as ps

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
f = os.path.join(BASE, 'Spanish_grid_model.gf81_x86', 'Spanish_grid_model.psout')
r = ps.File(f)
run = r.run(0)
print('run attrs', [a for a in dir(run) if not a.startswith('_')])
for tr, path in run.trace_paths():
    print(repr(path))
    print('   id', repr(tr.id), 'attrs', [a for a in dir(tr) if not a.startswith('_')][:20])
    break
