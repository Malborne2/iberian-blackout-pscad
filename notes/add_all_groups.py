"""Create all five collector groups from the pristine snapshot.

Positions in the free band below the network (grid units):
    row 1  y = 104 : C1 (x=22) -> Bus1, C2 (x=45) -> Bus2, C3 (x=68) -> Bus12
    row 2  y = 130 : C4 (x=22) -> Bus16, C5 (x=45) -> Bus22
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
GROUPS = [(22, 104, 'C1', 'Bus1'), (45, 104, 'C2', 'Bus2'), (68, 104, 'C3', 'Bus12'),
          (22, 130, 'C4', 'Bus16'), (45, 130, 'C5', 'Bus22')]

for x, y, tag, bus in GROUPS:
    print('=== %s at (%d,%d) -> %s' % (tag, x, y, bus), flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'add_group.py'),
                        str(x), str(y), tag, bus],
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if 'renamed' in l or 'ERR' in l]
    print('\n'.join(tail) or r.stdout[-400:])
    if r.returncode:
        print('FAILED', r.stderr[-500:])
        break
