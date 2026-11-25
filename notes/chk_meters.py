import xml.etree.ElementTree as ET
P = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx'
root = ET.parse(P).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
sch = main.find('schematic')

for el in sch:
    d = el.get('defn') or ''
    if d in ('master:multimeter', 'master:pgb', 'master:datalabel'):
        pl = {p.get('name'): p.get('value') for p in el.find('paramlist')}
        key = pl.get('Name') or pl.get('Sig') or ''
        print(f"{d:20s} x={el.get('x'):>5s} y={el.get('y'):>5s} Name={key!r:14s} "
              f"MeasP={pl.get('MeasP')} MeasQ={pl.get('MeasQ')} RMS={pl.get('RMS')} MeasV={pl.get('MeasV')} S={pl.get('S')}")
