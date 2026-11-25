import xml.etree.ElementTree as ET
P = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx'
root = ET.parse(P).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
sch = main.find('schematic')

print('tag summary:')
import collections
print(collections.Counter((el.tag, el.get('classid')) for el in sch))

n = 0
for el in sch:
    if el.tag == 'Wire':
        s = ET.tostring(el, encoding='unicode')
        if '1566' in s or '1476' in s:
            print(s[:800])
            n += 1
            if n > 2:
                break
print('wires with those coords:', n)
