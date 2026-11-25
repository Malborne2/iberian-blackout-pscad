"""List source3 instances (iid, name, coords) from the saved .pscx (read-only)."""
import re
import sys
from pathlib import Path

f = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\iberia1_pi1.pscx")
txt = f.read_text(encoding="utf-8", errors="replace")
pat = re.compile(r'<User classid="UserCmp"[^>]*id="(\d+)"[^>]*defn="master:source3"[^>]*>(.*?)</User>', re.S)
for m in pat.finditer(txt):
    iid, body = m.groups()
    nm = re.search(r'<param name="Name" value="([^"]*)"', body)
    vm = re.search(r'<param name="Vm" value="([^"]*)"', body)
    v = re.search(r'<param name="V" value="([^"]*)"', body)
    print(f"iid={iid:>11}  name={nm.group(1) if nm else '?':<10} Vm={vm.group(1) if vm else '?':<18} V='{v.group(1) if v else ''}'")
