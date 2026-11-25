"""Move one component (by current XML position) to a new position and re-wire its ports.

Usage: python notes/move_comp.py <oldx> <oldy> <newx> <newy>
Only relocates the block; existing wires are left where they are, so only use this for a
component whose connections are about to be redone.
"""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

ox, oy, nx, ny = (int(v) for v in sys.argv[1:5])
s = X.load()
n = 0


def fix(m):
    global n
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    if 'classid="UserCmp"' not in hdr:
        return blk
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    if int(d.get('x', -1)) == ox and int(d.get('y', -1)) == oy:
        n += 1
        return re.sub(r'\bx="\d+" y="\d+"', 'x="%d" y="%d"' % (nx, ny), blk, count=1)
    return blk


s = re.sub(r'\s*<User\b[^>]*>.*?</User>', fix, s, flags=re.S)
X.save(s)
print('moved', n)
