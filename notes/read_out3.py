"""Read the .psout and summarise every channel by name."""
import os, sys
import numpy as np
import mhi.psout as ps

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
PSOUT = os.path.join(BASE, 'Spanish_grid_model.gf81_x86', 'Spanish_grid_model.psout')


def load():
    r = ps.File(PSOUT)
    run = r.run(0)
    out = {}
    for tr, path in run.trace_paths():
        parts = path.split('/')
        name = parts[2] if len(parts) > 2 else path
        try:
            arr = np.asarray(tr.data, dtype=float).ravel()
        except Exception:
            continue
        out[name] = arr
    return out


if __name__ == '__main__':
    d = load()
    print('channels', len(d))
    for k in sorted(d):
        a = d[k]
        print(f'{k:10s} n={len(a):5d} min={a.min():9.4f} max={a.max():9.4f} last={a[-1]:9.4f} mean_tail={a[-200:].mean():9.4f}')
