import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

path = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx"
root = ET.parse(path).getroot()
defs = root.find('definitions')
main = [d for d in defs if d.get('name') == 'Main'][0]
sch = main.find('schematic')

users = [k for k in sch if k.tag == 'User']
cnt = Counter(u.get('defn') for u in users)
print("=== UserCmp defn counts ===")
for k, v in cnt.most_common():
    print(f"  {k}: {v}")

print("\n=== param names per defn (first instance) ===")
seen = set()
for u in users:
    d = u.get('defn')
    if d in seen:
        continue
    seen.add(d)
    pl = u.find('paramlist')
    print(f"\n-- {d}  (id={u.get('id')})")
    for p in pl:
        if p.tag == 'param':
            print(f"     {p.get('name')!r:32s} = {p.get('value')!r}" + ("" if len(p.attrib) == 2 else f"   attrs={ {k:v for k,v in p.attrib.items() if k not in ('name','value')} }"))
        else:
            print(f"     <{p.tag}> {p.attrib}")
