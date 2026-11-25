"""Rebuild the instrumentation channel layout from the known-good snapshot.

History: PSCAD clamps anything outside the canvas, so the 30 datalabel/pgb channel
blocks created at grid x=1500 all ended up on the canvas corner (135,175).  Everything
coincided -> `Signal 'P_G30' source contention`.

Steps:
 1. start from notes/base_phase1.pscx (30 datalabel + 30 pgb, 242 wires)
 2. drop the degenerate corner wires
 3. place row i at grid y = 4 + 5i, datalabel x=100, pgb x=108
 4. load the project and wire each pair with create_connection between grid points
"""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X
import ptools
import mhi.pscad as p

SRC = os.path.join(os.path.dirname(__file__), 'base_phase1.pscx')
GRID = 18
X_DL, X_PG = 100, 108
Y0, DY = 4, 5

s = open(SRC, encoding='utf-8', errors='replace').read()

blocks = []          # (start, end, defn, name, text)
for m in re.finditer(r'\s*<(Wire|User)\b[^>]*>.*?</\1>', s, re.S):
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    blocks.append((m.start(), m.end(), d.get('defn', ''), d.get('classid', ''),
                   nm.group(1) if nm else None, d))

dl_names = [b[4] for b in blocks if b[2] == 'master:datalabel']
pg_names = [b[4] for b in blocks if b[2] == 'master:pgb']
print('datalabels', len(dl_names), 'pgb', len(pg_names))
assert len(dl_names) == len(pg_names) == 30, 'channel count changed'
assert set(dl_names) == set(pg_names), 'names do not pair'
names = sorted(dl_names)

# ---- drop corner wires ----------------------------------------------------
drops = [b for b in blocks if b[3] == 'WireOrthogonal'
         and b[5].get('x') == '2430' and b[5].get('y') == '3150']
print('corner wires to drop:', len(drops))
for a, b, *_ in sorted(drops, reverse=True):
    s = s[:a] + s[b:]

# ---- move the blocks ------------------------------------------------------
edits = []
for i, name in enumerate(names):
    y = Y0 + i * DY
    for b in blocks:
        if b[4] == name and b[2] in ('master:datalabel', 'master:pgb'):
            x = X_DL if b[2] == 'master:datalabel' else X_PG
            new = re.sub(r'\bx="\d+" y="\d+"', 'x="%d" y="%d"' % (x * GRID, y * GRID),
                         b[0 + 0:] if False else s[b[0]:b[1]], count=1)
            edits.append((b[0], b[1], new, name, b[2]))
for a, b, new, name, defn in sorted(edits, reverse=True):
    s = s[:a] + new + s[b:]
print('moved', len(edits), 'blocks')

X.save(s)
print('written', len(s), 'chars')

# ---- wire them through the API -------------------------------------------
app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
made = 0
for i, name in enumerate(names):
    y = Y0 + i * DY
    try:
        main.create_connection((X_DL, y), (X_PG, y))
        made += 1
    except Exception as e:
        ptools.log('wire err', name, type(e).__name__, e)
ptools.log('wires created', made, 'of', len(names))
pr.save()
ptools.log('saved')
