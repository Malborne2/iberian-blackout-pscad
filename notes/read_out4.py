"""Read the .psout and summarise every channel: one-cycle mean and RMS where useful.

The output step is 0.5 ms, so 40 samples = one 50 Hz cycle.
"""
import os, sys
import numpy as np
import mhi.psout as ps

BASE = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model'
PSOUT = os.path.join(BASE, 'Spanish_grid_model.gf81_x86', 'Spanish_grid_model.psout')
CYCLE = 40


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
    names = sorted(k for k in d if k[:2] in ('P_', 'Q_', 'V_') and len(k) <= 6)
    print('channels', len(names))
    tot_p = tot_q = 0.0
    for k in names:
        a = d[k]
        if k.startswith('V_'):
            rms = float(np.sqrt(np.mean(a[-CYCLE:] ** 2)))
            print('%-8s rms=%8.4f  peak=%8.3f' % (k, rms, np.abs(a[-CYCLE:]).max()))
        else:
            m = float(a[-CYCLE:].mean())
            if k.startswith('P_G'):
                tot_p += m
            if k.startswith('Q_G'):
                tot_q += m
            print('%-8s mean=%8.4f' % (k, m))
    print('TOTAL generation %.2f GW, reactive %.0f Mvar' % (tot_p * 100 / 1000, tot_q * 100))
