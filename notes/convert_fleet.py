"""Convert buses 31-35 from source3 to synchronous machines (correct edit order).

unload -> XML deletions -> load+create -> save
"""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

EF = sys.argv[1] if len(sys.argv) > 1 else '1.03'
HERE = os.path.dirname(os.path.abspath(__file__))

# bus, source xml, multimeter xml, machine x, MVA, P0, H, bus point, voltmeter position
UNITS = [
    ('Bus31', (594, 1584), (594, 1530), 24, 1130.0, 1000.0, 5.0, '34,83', '34,88'),
    ('Bus32', (774, 1800), (774, 1746), 38, 1130.0, 1000.0, 5.0, '43,94', '43,100'),
    ('Bus33', (1044, 1692), (1044, 1638), 52, 1500.0, 1500.0, 4.0, '58,89', '58,94'),
    ('Bus34', (918, 1692), (918, 1638), 66, 1500.0, 1500.0, 4.0, '51,89', '51,94'),
    ('Bus35', (1170, 666), (1170, 720), 80, 720.0, 720.0, 4.0, '64,43', '65,50'),
]

# 1. leave the API so XML edits survive (no-op if nothing is loaded)
try:
    ptools.save_unload()
    print('offloaded')
except Exception as e:
    print('nothing loaded:', type(e).__name__)

# 2. delete the sources and multimeters (project is not loaded)
for bus, src, met, *_ in UNITS:
    for pos in (src, met):
        r = subprocess.run([sys.executable, os.path.join(HERE, 'del_at.py'),
                            str(pos[0]), str(pos[1])], capture_output=True, text=True)
        print('  ', bus, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-150:])

# 3. create the machines
for bus, src, met, mx, mva, p0, h, bp, vp in UNITS:
    r = subprocess.run([sys.executable, os.path.join(HERE, 'add_unit5.py'),
                        bus, str(mx), str(mva), str(p0), str(h), bp, EF, vp],
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if 'saved' in l or 'ERR' in l]
    print('  ', bus, '->', '; '.join(tail) or r.stderr[-300:])
