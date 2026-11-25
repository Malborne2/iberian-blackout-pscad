"""Name the collector buses in the XML (PSCAD requires unique bus names).

Usage: python notes/name_bus.py <x_xml> <y_xml> <name> <basekv>
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import re
import xmlutil as X

x, y, name, kv = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
s = X.load()
n = 0
for m in re.finditer(r'<Wire classid="Bus"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    h = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    if int(h['x']) == x and int(h['y']) == y:
        new = re.sub(r'(name="Name" value=")[^"]*(")', lambda m2: m2.group(1) + name + m2.group(2), blk)
        new = re.sub(r'(name="BaseKV" value=")[^"]*(")', lambda m2: m2.group(1) + kv + m2.group(2), new)
        s = s[:m.start()] + new + s[m.end():]
        n += 1
X.save(s)
print('renamed', n, 'bus at', (x, y), '->', name, kv)
