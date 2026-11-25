"""Convert buses 32-35 to synchronous machines (same pattern as 31).

Usage: python notes/convert_fleet2.py [efld]
"""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

EF = sys.argv[1] if len(sys.argv) > 1 else '1.03'
HERE = os.path.dirname(os.path.abspath(__file__))

# bus, source xml, multimeter xml, machine x, MVA, P0, H, bus point
UNITS = [
    ('Bus32', (774, 1800), (774, 1746), 38, 1130.0, 1000.0, 5.0, '43,94'),
    ('Bus33', (1044, 1692), (1044, 1638), 52, 1500.0, 1500.0, 4.0, '58,89'),
    ('Bus34', (918, 1692), (918, 1638), 66, 1500.0, 1500.0, 4.0, '51,89'),
    ('Bus35', (1170, 666), (1170, 720), 80, 720.0, 720.0, 4.0, '64,43'),
]

try:
    ptools.save_unload()
    print('offloaded')
except Exception as e:
    print('nothing loaded:', type(e).__name__)

for bus, src, met, *_ in UNITS:
    for pos in (src, met):
        subprocess.run([sys.executable, os.path.join(HERE, 'del_at.py'),
                        str(pos[0]), str(pos[1])], capture_output=True, text=True)

# the deletion above must not be lost: reload happens inside add_unit6
for bus, src, met, mx, mva, p0, h, bp in UNITS:
    r = subprocess.run([sys.executable, os.path.join(HERE, 'add_unit6.py'),
                        bus, str(mx), '160', str(mva), str(p0), str(h), bp, EF],
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if 'saved' in l or 'ERR' in l]
    print('  ', bus, '->', '; '.join(tail) or r.stderr[-300:])
