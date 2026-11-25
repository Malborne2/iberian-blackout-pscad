"""List all trace names in the .psout (optionally filtered)."""
import os, sys
import mhi.psout as ps

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
PSOUT = os.path.join(BASE, 'Spanish_grid_model.gf81_x86', 'Spanish_grid_model.psout')
kw = sys.argv[1].lower() if len(sys.argv) > 1 else ''
r = ps.File(PSOUT).run(0)
seen = []
for tr, path in r.trace_paths():
    if kw in path.lower():
        seen.append(path)
for p in sorted(set(seen)):
    print(p)
print('total', len(seen))
