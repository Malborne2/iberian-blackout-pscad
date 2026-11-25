import xml.etree.ElementTree as ET
P = r'C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx'
root = ET.parse(P).getroot()
main = [d for d in root.find('definitions') if d.get('name') == 'Main'][0]
for el in main.find('schematic'):
    if 'multimeter' in (el.get('defn') or ''):
        pl = {p.get('name'): p.get('value') for p in el.find('paramlist')}
        print({k: pl[k] for k in ('MeasI', 'MeasV', 'MeasP', 'MeasQ', 'RMS', 'S', 'BaseV', 'Freq',
                                  'P', 'Q', 'Vrms', 'Pd', 'Qd', 'Vd') if k in pl})
