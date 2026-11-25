r"""Read PSCAD legacy output (PlotType 1): <case>.infx channel index + <case>_NN.out files (time + up to 10 channels each).

usage (module): from legacy_out import load; t, ch = load(r"C:\PSCAD_work\lt7_base\lt7.gf81_x86", "lt7")
       ch is {name: array}, name as in the .infx without the Main(0) prefix, e.g. "VHV", "SyncUnit(0):QOUT",
       arrays expanded for dim > 1 as "<name>[k]".
usage (cli):    python iberia_eq\pscad\legacy_out.py <gf81 folder> <case>      -> prints the channel list
"""
import glob, os, re, sys
import numpy as np
import xml.etree.ElementTree as ET


def load(folder, case):
    root = ET.parse(os.path.join(folder, f"{case}.infx")).getroot()
    names = []
    for a in root.iter("Analog"):
        nm = a.get("name"); nm = re.sub(r"^Main\(0\)[:\\]", "", nm)
        d = int(a.get("dim", "1"))
        names += [nm] if d == 1 else [f"{nm}[{k + 1}]" for k in range(d)]
    cols, t = [], None
    for f in sorted(glob.glob(os.path.join(folder, f"{case}_[0-9][0-9].out"))):
        a = np.loadtxt(f, skiprows=1, ndmin=2)
        if t is None: t = a[:, 0]
        n = min(len(t), len(a)); t = t[:n]; cols = [c[:n] for c in cols] + [a[:n, k] for k in range(1, a.shape[1])]
    return t, dict(zip(names, cols))


if __name__ == "__main__":
    t, ch = load(sys.argv[1], sys.argv[2])
    print(f"{len(t)} samples, t {t[0]:.3f} .. {t[-1]:.3f} s; channels:", list(ch))
