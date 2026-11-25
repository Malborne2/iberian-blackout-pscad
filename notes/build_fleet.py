"""Rebuild the whole synchronous fleet with the vertical machine+AVR unit layout.

unload -> delete the six sources and their multimeters -> create six units -> build.

Usage: python notes/build_fleet.py [group]      group 1 = G30..G32, 2 = G33..G35, 0 = all
"""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

GROUP = int(sys.argv[1]) if len(sys.argv) > 1 else 0
HERE = os.path.dirname(os.path.abspath(__file__))

# bus, source xml, multimeter xml, machine x, MVA, P0, H, bus point
ALL = [
    ('Bus30', (486, 216), (486, 270), 10, 1130.0, 1000.0, 5.0, '27,17'),
    ('Bus31', (594, 1584), (594, 1530), 26, 1130.0, 1000.0, 5.0, '34,83'),
    ('Bus32', (774, 1800), (774, 1746), 42, 1130.0, 1000.0, 5.0, '43,94'),
    ('Bus33', (1044, 1692), (1044, 1638), 58, 1500.0, 1500.0, 4.0, '58,89'),
    ('Bus34', (918, 1692), (918, 1638), 74, 1500.0, 1500.0, 4.0, '51,89'),
    ('Bus35', (1170, 666), (1170, 720), 90, 720.0, 720.0, 4.0, '64,43'),
]
UNITS = ALL if GROUP == 0 else (ALL[:3] if GROUP == 1 else ALL[3:])

try:
    ptools.save_unload()
    print('offloaded')
except Exception as e:
    print('nothing loaded:', type(e).__name__)

for bus, src, met, *_ in UNITS:
    for pos in (src, met):
        subprocess.run([sys.executable, os.path.join(HERE, 'del_at.py'),
                        str(pos[0]), str(pos[1])], capture_output=True, text=True)

for i, (bus, src, met, mx, mva, p0, h, bp) in enumerate(UNITS):
    log = 1 if bus in ('Bus30', 'Bus33') else 0     # two speed channels are enough
    r = subprocess.run([sys.executable, os.path.join(HERE, 'add_unit8.py'),
                        bus, str(mx), str(mva), str(p0), str(h), bp, str(log)],
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if 'saved' in l or 'ERR' in l]
    print('  ', bus, '->', '; '.join(tail) or r.stderr[-250:])
