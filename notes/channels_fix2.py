"""Rebuild the instrumentation channel layout (correct single-pass version).

Lesson: editing a file with spans collected *before* other edits shift them scrambles
the result.  Everything is done in one regex pass here.

  * datalabel/pgb blocks: row i at grid y = 4 + 5i, x = 100 (datalabel) / 108 (pgb)
  * the degenerate corner wires at (135,175) are deleted
  * the 30 signal wires are then created through the API between the two ports
"""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X
import ptools

SRC = os.path.join(os.path.dirname(__file__), 'base_phase1.pscx')
GRID = 18
X_DL, X_PG = 100, 108
Y0, DY = 4, 5

s = open(SRC, encoding='utf-8', errors='replace').read()

# name -> row
names = sorted(set(re.findall(
    r'<User classid="UserCmp"[^>]*?defn="master:datalabel"[^>]*>.*?'
    r'name="Name" value="([^"]*)"', s, re.S)))
row = {n: i for i, n in enumerate(names)}
print('channels', len(names))

counts = {'dl': 0, 'pg': 0, 'drop': 0}


def fix(m):
    blk = m.group(0)
    hdr = blk[:blk.find('>')]
    d = dict(re.findall(r'(\w+)="([^"]*)"', hdr))
    defn = d.get('defn', '')
    if d.get('classid') == 'WireOrthogonal':
        if 'x="2430" y="3150"' in hdr:
            counts['drop'] += 1
            return ''
        return blk
    if defn not in ('master:datalabel', 'master:pgb'):
        return blk
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    name = nm.group(1) if nm else None
    if name not in row:
        return blk
    x = X_DL if defn == 'master:datalabel' else X_PG
    y = Y0 + row[name] * DY
    new = re.sub(r'\bx="\d+" y="\d+"',
                 'x="%d" y="%d"' % (x * GRID, y * GRID), blk, count=1)
    counts['dl' if defn == 'master:datalabel' else 'pg'] += 1
    return new


s = re.sub(r'\s*<(Wire|User)\b[^>]*>.*?</\1>', fix, s, flags=re.S)
print(counts)
X.save(s)

# ---- verify positions -----------------------------------------------------
s = X.load()
pos = {}
for m in re.finditer(r'<User classid="UserCmp"[^>]*?defn="master:(datalabel|pgb)"[^>]*>', s):
    d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    pos[(d['defn'], d['x'])] = pos.get((d['defn'], d['x']), 0) + 1
print('positions', pos)

# ---- wire the pairs through the API --------------------------------------
app, pr = ptools.ensure_loaded()
main = pr.canvas('Main')
made = 0
for name, i in row.items():
    y = Y0 + i * DY
    try:
        main.create_connection((X_DL, y), (X_PG, y))
        made += 1
    except Exception as e:
        ptools.log('wire err', name, type(e).__name__, e)
ptools.log('wires created', made, 'of', len(row))
pr.save()
ptools.log('saved')
