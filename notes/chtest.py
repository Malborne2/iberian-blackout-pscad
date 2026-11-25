"""Apply the channel repositioning to the snapshot into a scratch file and report xs."""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))

GRID = 18
X_DL, X_PG = 100, 108
Y0, DY = 4, 5
SRC = os.path.join(os.path.dirname(__file__), 'base_phase1.pscx')
OUT = os.path.join(os.path.dirname(__file__), 'chtest.pscx')

s = open(SRC, encoding='utf-8', errors='replace').read()

blocks = []
for m in re.finditer(r'\s*<(Wire|User)\b[^>]*>.*?</\1>', s, re.S):
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    blocks.append((m.start(), m.end(), d.get('defn', ''), d.get('classid', ''),
                   nm.group(1) if nm else None))

names = sorted({b[4] for b in blocks if b[2] == 'master:datalabel'})

# drop corner wires
drops = [(b[0], b[1]) for b in blocks if b[3] == 'WireOrthogonal'
         and b[2] == '' and False]
drops = []
for b in blocks:
    if b[3] == 'WireOrthogonal':
        hdr = s[b[0]:s.index('>', b[0]) + 1]
        if 'x="2430" y="3150"' in hdr:
            drops.append((b[0], b[1]))
print('corner wires', len(drops))
for a, b in sorted(drops, reverse=True):
    s = s[:a] + s[b:]

edits = []
for i, name in enumerate(names):
    y = Y0 + i * DY
    for b in blocks:
        if b[4] != name or b[2] not in ('master:datalabel', 'master:pgb'):
            continue
        x = X_DL if b[2] == 'master:datalabel' else X_PG
        new = re.sub(r'\bx="\d+" y="\d+"', 'x="%d" y="%d"' % (x * GRID, y * GRID),
                     s[b[0]:b[1]], count=1)
        edits.append((b[0], b[1], new))
print('edits', len(edits))
for a, b, new in sorted(edits, reverse=True):
    s = s[:a] + new + s[b:]

open(OUT, 'w', encoding='utf-8', newline='').write(s)

xs = {}
for m in re.finditer(r'<User\b[^>]*defn="master:(datalabel|pgb)"[^>]*>', s):
    h = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    xs.setdefault((h.get('defn'), h['x']), 0)
    xs[(h.get('defn'), h['x'])] += 1
print('defn/x counts:', xs)
