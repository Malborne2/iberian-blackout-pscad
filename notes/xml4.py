import xml.etree.ElementTree as ET
from collections import Counter

path = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx"
root = ET.parse(path).getroot()
defs = root.find('definitions')
main = [d for d in defs if d.get('name') == 'Main'][0]
sch = main.find('schematic')

print("schematic paramlist:")
for p in sch.find('paramlist'):
    print("   ", p.attrib)

kids = [k for k in sch if k.tag != 'paramlist']
print("\ncounts:", Counter((k.tag, k.get('classid')) for k in kids))

print("\n--- first 3 of each (tag,classid) ---")
seen = {}
for k in kids:
    key = (k.tag, k.get('classid'))
    seen.setdefault(key, []).append(k)
for key, lst in seen.items():
    print("\n==", key, len(lst))
    for k in lst[:2]:
        print("  attrib:", k.attrib)
        for c in k:
            print("     <", c.tag, ">", c.attrib, "kids=", len(list(c)))
