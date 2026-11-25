"""List Bus components (name, grid coords, base kV) from a saved .pscx (read-only)."""
import re
import sys
from pathlib import Path

f = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia1_pi1.pscx")
txt = f.read_text(encoding="utf-8", errors="replace")

pat = re.compile(r'<Wire classid="Bus"[^>]*?id="(\d+)"[^>]*?x="(-?\d+)"[^>]*?y="(-?\d+)"[^>]*?w="(\d+)"[^>]*?h="(\d+)"[^>]*?>(.*?)</Wire>', re.S)
rows = []
for m in pat.finditer(txt):
    iid, x, y, w, h, body = m.groups()
    nm = re.search(r'<param name="Name" value="([^"]*)"', body)
    kv = re.search(r'<param name="BaseKV" value="([^"]*)"', body)
    rows.append((int(iid), nm.group(1) if nm else "?", kv.group(1) if kv else "?",
                 int(x) // 18, int(y) // 18, int(w) // 18, int(h) // 18))

print(f"{len(rows)} buses")
for r in sorted(rows, key=lambda r: r[1]):
    print("  iid=%-11d %-8s %-8s grid=(%2d,%2d) w=%2d h=%d" % r)
