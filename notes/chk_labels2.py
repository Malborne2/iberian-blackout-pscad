import xml.etree.ElementTree as ET, collections
P = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx'
root = ET.parse(P).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
sch = main.find('schematic')

n = 0
for el in sch:
    if el.get('defn') in ('master:datalabel', 'master:pgb'):
        print(ET.tostring(el, encoding='unicode')[:600])
        n += 1
        if n >= 3:
            break
