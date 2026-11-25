import xml.etree.ElementTree as ET
P = r'C:\Users\Public\Documents\PSCAD\5.1.0\Examples\FixedLoad\fixedload.pscx'
root = ET.parse(P).getroot()
for d in root.find('definitions'):
    if d.get('name') != 'Main':
        continue
    s = d.find('schematic')
    for el in s:
        d2 = el.get('defn') or ''
        if 'multimeter' in d2 or d2 == 'master:datalabel' or d2 == 'master:pgb':
            print(ET.tostring(el, encoding='unicode')[:1200])
            print('-' * 60)
    print('WIRES near labels:')
    for el in s:
        t = ET.tostring(el, encoding='unicode')
        if el.tag == 'Wire' and ('x="5' in t or True):
            pass
