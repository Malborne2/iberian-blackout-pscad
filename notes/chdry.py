"""Dry-run the channel repositioning on the snapshot and print where blocks land."""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))

GRID = 18
X_DL, X_PG = 100, 108
Y0, DY = 4, 5

s = open(os.path.join(os.path.dirname(__file__), 'base_phase1.pscx'),
         encoding='utf-8', errors='replace').read()

blocks = []
for m in re.finditer(r'\s*<(Wire|User)\b[^>]*>.*?</\1>', s, re.S):
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    blocks.append((m.start(), m.end(), d.get('defn', ''), d.get('classid', ''),
                   nm.group(1) if nm else None))

n = 0
for b in blocks:
    if b[2] in ('master:datalabel', 'master:pgb'):
        n += 1
        if n <= 6 or b[4] in ('P_G30', 'P_G31'):
            print(b[4], b[2], 'classid=', b[3])
print('total channel blocks', n)

