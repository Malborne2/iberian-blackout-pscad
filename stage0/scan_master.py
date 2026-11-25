"""List definition names and groups inside PSCAD's master library (read-only).

Only used to choose candidate components for T7 (signal-controlled impedance)
and T8 (PI-section line), because pscad_list_definitions() times out on the
master library.
"""
import re
from pathlib import Path

f = Path(r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx")
txt = f.read_bytes().decode("latin-1")
defs = re.findall(r'<Definition[^>]*name="([^"]+)"[^>]*?(?:group="([^"]*)")?[^>]*>', txt)
rows = sorted(set(defs))
print("definitions:", len(rows))
Path(__file__).with_name("master_defs.txt").write_text(
    "\n".join(f"{n}\t{g}" for n, g in rows), encoding="utf-8")

for pat in ("var", "pi", "section", "flux", "reactor", "shunt", "load", "branch"):
    hits = [(n, g) for n, g in rows if pat in n.lower()]
    print(f"\n{pat.upper()} ({len(hits)}):")
    for n, g in hits[:15]:
        print(f"   {n:32} [{g}]")
