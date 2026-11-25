import sys
import numpy as np
import mhi.psout
PS = sys.argv[1]
with mhi.psout.File(PS) as f:
    r = f.run(0)
    def get(p):
        tr = r.call(p, sep="/")
        return np.asarray(tr.domain.data, float), np.asarray(tr.data, float)
    t, idc = get("Root/Main/HVDC_T/ID/0/1")
    _, iq = get("Root/Main/HVDC_T/IQ/0/1")
    _, vdf = get("Root/Main/HVDC_T/VDF/0/1")
    _, tri = get("Root/Main/HVDC_T/TRIP/0/1")
    print(f"{'t':>7} {'ID':>9} {'IQ':>9} {'VDF':>9} {'TRIP':>5}")
    for tt in (0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.5, 2.0):
        i = min(int(np.searchsorted(t, tt)), len(t) - 1)
        print(f"{t[i]:7.3f} {idc[i]:+9.4f} {iq[i]:+9.4f} {vdf[i]:+9.4f} {tri[i]:5.2f}")
