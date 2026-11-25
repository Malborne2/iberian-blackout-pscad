import xml.etree.ElementTree as ET, os
BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
root = ET.parse(os.path.join(BASE, "Spanish_grid_model.pscx")).getroot()
d = [x for x in root.find('definitions') if x.get('name') == 'TLine_1'][0]
print("attrib", d.attrib)
sch = d.find('schematic')
for k in sch:
    if k.tag == 'paramlist':
        print("canvas params:")
        for pp in k:
            print("   ", pp.get('name'), '=', pp.get('value'))
        continue
    print(" ", k.tag, k.get('classid'), k.get('defn'))
    pl = k.find('paramlist')
    if pl is not None:
        for pp in pl:
            print("     ", pp.get('name'), '=', pp.get('value'))
