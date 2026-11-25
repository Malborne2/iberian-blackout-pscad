"""Total scheduled load and generator voltage bases in the converted model (read-only)."""
import re
from pathlib import Path

p = Path(r"C:\PSCAD_work\iberia1_pi1.pscx")
t = p.read_text(encoding="utf-8", errors="replace")

loads = re.findall(r'<User classid="UserCmp"[^>]*defn="master:fixed_load"[^>]*>(.*?)</User>', t, re.S)
tot = 0.0
vals = []
for b in loads:
    po = re.search(r'<param name="PO" value="([^"]*)"', b)
    if po:
        v = float(po.group(1).split()[0])
        vals.append(v)
        tot += v * 3          # fixed_load P is per phase
print(f"fixed_load instances: {len(loads)}  sum(PO)*3 = {tot:.1f} MW")
print("per-instance PO (MW/phase):", vals)

src = re.findall(r'defn="master:source3".*?<param name="Vm" value="([^"]*)"', t, re.S)
print("source Vm:", sorted(set(src)))
