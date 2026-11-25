"""Sum the rebased load and compare with the expected 25,240 MW (read-only)."""
import re
from pathlib import Path

p = Path(r"C:\PSCAD_work\iberia1_stage1.pscx")
t = p.read_text(encoding="utf-8", errors="replace")
loads = re.findall(r'defn="master:fixed_load".*?</User>', t, re.S)
tot = 0.0
vals = []
for b in loads:
    m = re.search(r'<param name="PO" value="([^"]*)"', b)
    v = float(m.group(1).split()[0]) if m else 0.0
    vals.append(round(v, 2))
    tot += v * 3
print(f"loads: {len(loads)}   sum(PO)*3 = {tot:.1f} MW   expected 25,237 MW")
print("PO per phase:", vals)
