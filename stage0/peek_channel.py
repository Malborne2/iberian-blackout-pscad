"""Show how the demo's channel chain is wired, by reading the .pscx XML directly.

Read-only; used to learn the exact datalabel/pgb convention because the tools do not
expose a meter's signal output port.
"""
import re
import sys
from pathlib import Path

f = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\PSCAD_work\mcp_demo_copy.pscx")
txt = f.read_text(encoding="utf-8", errors="replace")

# component blocks
for name in ("ammeter", "datalabel", "pgb"):
    print(f"\n===== {name} =====")
    for m in re.finditer(r'<component[^>]*defn="([^"]*' + name + r'[^"]*)"[^>]*>(.*?)</component>',
                         txt, re.S | re.I):
        print("defn:", m.group(1))
        for pm in re.finditer(r'<param name="([^"]+)" value="([^"]*)"', m.group(2)):
            print(f"   {pm.group(1):14} = {pm.group(2)}")

print("\n===== wires touching y=11..13 =====")
for m in re.finditer(r"<wire>(.*?)</wire>", txt, re.S | re.I):
    body = m.group(1)
    pts = re.findall(r'<vertex[^>]*x="(-?\d+)"[^>]*y="(-?\d+)"', body)
    if pts and any(11 <= int(y) <= 13 for _x, y in pts):
        print("  ", pts)
