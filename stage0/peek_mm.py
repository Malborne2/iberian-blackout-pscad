"""List multimeter iids from the saved .pscx (read-only), so the base update needs no canvas listing."""
import re
from pathlib import Path

p = Path(r"C:\PSCAD_work\iberia1_400.pscx")
t = p.read_text(encoding="utf-8", errors="replace")
ids = re.findall(r'<User classid="UserCmp"[^>]*id="(\d+)"[^>]*defn="master:multimeter"', t)
print(len(ids), ids)
