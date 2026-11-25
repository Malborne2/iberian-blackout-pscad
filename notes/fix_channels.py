"""Repair the instrumentation channels.

PSCAD had clamped all 30 datalabel / 30 pgb blocks (created far outside the canvas at
grid x = 1500) onto the canvas corner (135,175), so every data port coincided and the
build failed with `Signal 'P_G30' source contention`.

This script lays them out inside the canvas - one row per signal, datalabel at x=100,
pgb at x=108 - and rebuilds the datalabel -> pgb wires in XML.
"""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

DX = 144                 # datalabel -> pgb distance in drawing units (8 grid units)
X0 = 100 * 18            # grid 100
X1 = X0 + DX
Y0 = 4 * 18              # grid 4
DY = 5 * 18              # 5 grid units per row

s = X.load()

# ---- collect datalabel / pgb blocks ---------------------------------------
dls, pgs = {}, {}
corner_wires = []
for m in re.finditer(r'\s*<(Wire|User)\b[^>]*>.*?</\1>', s, re.S):
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    defn = d.get('defn', '')
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    name = nm.group(1) if nm else None
    if defn == 'master:datalabel' and name:
        dls[name] = (m.start(), m.end(), blk)
    elif defn == 'master:pgb' and name:
        pgs[name] = (m.start(), m.end(), blk)
    elif d.get('classid') == 'WireOrthogonal' and d.get('x') == '2430' and d.get('y') == '3150':
        corner_wires.append((m.start(), m.end()))

names = sorted(set(dls) & set(pgs))
print('datalabels', len(dls), 'pgb', len(pgs), 'paired', len(names),
      'corner wires', len(corner_wires))
missing = (set(dls) ^ set(pgs))
if missing:
    print('UNPAIRED:', sorted(missing))

# ---- remove the 30 corner wires -------------------------------------------
for a, b in sorted(corner_wires, reverse=True):
    s = s[:a] + s[b:]

# ---- move the blocks and add a fresh wire per channel ---------------------
out = []
pos = 0
new_wires = []
edits = []
for i, name in enumerate(names):
    y = Y0 + i * DY
    for tbl, x in ((dls, X0), (pgs, X1)):
        a, b, blk = tbl[name]
        newblk = re.sub(r'\bx="\d+" y="\d+"',
                        'x="%d" y="%d"' % (x, y), blk, count=1)
        edits.append((a, b, newblk))
    new_wires.append(y)

for a, b, blk in sorted(edits, reverse=True):
    s = s[:a] + blk + s[b:]

# wires: x,y = start, w = dx+10, h = dy+10, one vertex pair
wire_tpl = ('        <Wire classid="WireOrthogonal" id="{id}" name="" x="{x}" y="{y}" '
            'w="{w}" h="10" orient="0" disable="false">\n'
            '          <vertex x="0" y="0" />\n'
            '          <vertex x="{dx}" y="0" />\n'
            '        </Wire>\n')
import random
used = set(re.findall(r'\bid="(\d+)"', s))
wires = []
for y in new_wires:
    while True:
        wid = random.randrange(100000000, 1999999999)
        if str(wid) not in used:
            used.add(str(wid))
            break
    wires.append(wire_tpl.format(id=wid, x=X0, y=y, w=DX + 10, dx=DX))

i = s.rindex('</schematic>')
s = s[:i] + ''.join(wires) + '      ' + s[i:]

X.save(s)

# ---- verify ---------------------------------------------------------------
s = X.load()
print('channels repositioned:', len(names))
print('datalabel xs:', sorted({int(m) for m in re.findall(
    r'<User classid="UserCmp"[^>]*?defn="master:datalabel"[^>]*?x="(\d+)"', s)}))
print('pgb xs:', sorted({int(m) for m in re.findall(
    r'<User classid="UserCmp"[^>]*?defn="master:pgb"[^>]*?x="(\d+)"', s)}))
print('wires', len(re.findall(r'<Wire classid="WireOrthogonal"', s)))
