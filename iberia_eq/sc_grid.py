"""Coarse grid for the fault-level calibration of pp_v2 (Table 4-26): xk, kres, vkg."""
import subprocess, sys, re, itertools, numpy as np, os
HERE = os.path.dirname(os.path.abspath(__file__)); res = []
for xk, kr, vk, fr in itertools.product((1.5, 2, 2.5), (0.2, 0.4), (100, 250), (1500,)):
    o = subprocess.run([sys.executable, os.path.join(HERE, "pp_v2.py"), "--quick", "--frsc", str(fr), "--xk", str(xk), "--kres", str(kr), "--vkg", str(vk)],
                       capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"}).stdout
    r = re.findall(r"^\s+(\w+)\s+(\d+)\s+(\d+)\s+\(", o, re.M)
    if not r: continue
    e = np.array([np.log(float(m) / float(t)) for _, m, t in r]); res.append((np.sqrt((e ** 2).mean()), xk, kr, (vk, fr), {z: round(100 * (float(m) / float(t) - 1)) for z, m, t in r}))
res.sort(key=lambda x: x[0])
for r in res[:6]: print(f"rms log err {r[0]:.3f}  xk {r[1]} kres {r[2]} vkg/frsc {r[3]}  ", r[4])
