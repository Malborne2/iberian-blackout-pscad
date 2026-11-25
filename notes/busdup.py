"""List all Bus elements with their id, position and name (duplicates visible)."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()
for m in re.finditer(r'<Wire classid="Bus"[^>]*>.*?</Wire>', s, re.S):
    blk = m.group(0)
    h = dict(re.findall(r'(\w+)="([^"]*)"', blk[:blk.find('>')]))
    nm = re.search(r'name="Name" value="([^"]*)"', blk)
    kv = re.search(r'name="BaseKV" value="([^"]*)"', blk)
    if nm and (nm.group(1).startswith('C1') or nm.group(1) == 'Bus'):
        print('id=%-11s x=%-5s y=%-5s w=%-4s name=%-8s kv=%s  span=%d'
              % (h['id'], h['x'], h['y'], h.get('w'), nm.group(1), kv.group(1) if kv else '?',
                 len(blk)))
