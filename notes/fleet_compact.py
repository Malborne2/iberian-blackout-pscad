"""Rebuild the whole generator fleet with the compact at-bus unit layout.

unload -> delete the ten source3 + multimeters -> create the ten compact units.

Usage: python notes/fleet_compact.py [group]   1 = G30..G35, 2 = G36..G39, 0 = all
"""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

GROUP = int(sys.argv[1]) if len(sys.argv) > 1 else 0
HERE = os.path.dirname(os.path.abspath(__file__))

# bus, source xml, multimeter xml, bus point, MVA, P0, H, tag
ALL = [
    ('Bus30', 486, 216, 486, 270, 27, 17, 1130.0, 1000.0, 5.0, 'G30'),
    ('Bus31', 594, 1584, 594, 1530, 34, 83, 1130.0, 1000.0, 5.0, 'G31'),
    ('Bus32', 774, 1800, 774, 1746, 43, 94, 1130.0, 1000.0, 5.0, 'G32'),
    ('Bus33', 1044, 1692, 1044, 1638, 58, 89, 1500.0, 1500.0, 4.0, 'G33'),
    ('Bus34', 918, 1692, 918, 1638, 51, 89, 1500.0, 1500.0, 4.0, 'G34'),
    ('Bus35', 1170, 666, 1170, 720, 64, 43, 720.0, 720.0, 4.0, 'G35'),
    ('Bus36', 1188, 1548, 1188, 1494, 64, 81, 7200.0, 7000.0, 3.0, 'G36'),
    ('Bus37', 576, 72, 576, 126, 32, 10, 7200.0, 7000.0, 3.0, 'G37'),
    ('Bus38', 1260, 648, 1260, 594, 68, 31, 7200.0, 7000.0, 3.0, 'G38'),
    ('Bus39', 414, 846, 414, 918, 24, 55, 4000.0, 3800.0, 4.0, 'G39'),
]
UNITS = ALL if GROUP == 0 else (ALL[:6] if GROUP == 1 else ALL[6:])

try:
    ptools.save_unload()
    print('offloaded')
except Exception as e:
    print('nothing loaded:', type(e).__name__)

for u in UNITS:
    for pos in ((u[1], u[2]), (u[3], u[4])):
        subprocess.run([sys.executable, os.path.join(HERE, 'del_at.py'),
                        str(pos[0]), str(pos[1])], capture_output=True, text=True)

for u in UNITS:
    bus, sx, sy, mmx, mmy, bx, by, mva, p0, h, tag = u
    r = subprocess.run([sys.executable, os.path.join(HERE, 'unit_compact.py'),
                        bus, str(sx), str(sy), str(mmx), str(mmy), str(bx), str(by),
                        str(mva), str(p0), str(h), tag],
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if 'rect' in l or 'machine' in l or 'ERR' in l]
    print('  ', bus, '->', ' | '.join(tail) or r.stderr[-250:])
