"""Remove duplicate bus elements (same position+name) and any stale collector bus."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import xmlutil as X

s = X.load()

KEEP = {('558', '1908'), ('522', '2124')}      # the two buses of the current group
seen = set()
drop = []

for m in re.finditer(r'\s*<Wire classid="Bus"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    h = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    key = (h['x'], h['y'])
    if key not in KEEP:
        drop.append((m.start(), m.end(), key, 'not in keep list'))
        continue
    if key in seen:
        drop.append((m.start(), m.end(), key, 'duplicate'))
    else:
        seen.add(key)

for a, b, key, why in reversed(drop):
    print('drop bus', key, why)
    s = s[:a] + s[b:]

X.save(s)
s = X.load()
print('buses now', len(re.findall(r'<Wire classid="Bus"', s)))
