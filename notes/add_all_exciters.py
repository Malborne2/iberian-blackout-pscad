"""Add the IEEE SCRX exciter to every machine (deleting the fixed-field const first).

Usage: python notes/add_all_exciters.py
"""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools

HERE = os.path.dirname(os.path.abspath(__file__))
UNITS = [('G30', 10, 1130.0), ('G31', 24, 1130.0), ('G32', 38, 1130.0),
         ('G33', 52, 1500.0), ('G34', 66, 1500.0), ('G35', 80, 720.0)]

try:
    ptools.save_unload()
    print('offloaded')
except Exception as e:
    print('nothing loaded:', type(e).__name__)

# 1. remove the fixed-field constants so the exciter can own efldn
names = ['EF' + t for t, _, _ in UNITS]
subprocess.run([sys.executable, os.path.join(HERE, 'del_name.py')] + names,
               capture_output=True, text=True)

# 2. add one exciter per machine
for tag, mx, mva in UNITS:
    r = subprocess.run([sys.executable, os.path.join(HERE, 'add_exciter.py'),
                        tag, str(mx), '160', str(mva)],
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if 'wired' in l or 'saved' in l or 'ERR' in l]
    print('  ', tag, '->', '; '.join(tail) or r.stderr[-250:])
