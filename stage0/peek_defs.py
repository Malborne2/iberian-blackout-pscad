"""Inspect how definitions are stored in a .pscx (read-only)."""
import re
from pathlib import Path

p = Path(r"C:\PSCAD_work\iberia1_pi1.pscx")
t = p.read_text(encoding="utf-8", errors="replace")
print("Line_ManualYZ:", t.count("Line_ManualYZ"), " pi_section:", t.count("pi_section"))
hits = re.findall(r'<[A-Za-z]+[^>]{0,200}name="T1_2"[^>]{0,80}>', t)
print("tags naming T1_2:", hits[:3])
i = t.find("<Definition")
print("first Definition tag:", t[i:i+160] if i >= 0 else "none")
# show what wraps a Line_ManualYZ
j = t.find("Line_ManualYZ")
print("... Line_ManualYZ context ...")
print(t[max(0, j - 700):j + 300])
