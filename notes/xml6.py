import xml.etree.ElementTree as ET, os
BASE = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model"
root = ET.parse(os.path.join(BASE, "Spanish_grid_model.pscx")).getroot()
for d in root.find('definitions'):
    if d.get('name') in ('psse', 'Station'):
        print("=" * 60)
        print(d.get('name'), d.get('classid'))
        sch = d.find('schematic')
        if sch is None:
            print(" no schematic")
            continue
        for k in sch:
            if k.tag == 'paramlist':
                continue
            print("  ", k.tag, k.get('classid'), k.get('defn'), [(pp.get('name'), pp.get('value')) for pp in (k.find('paramlist') or [])])
