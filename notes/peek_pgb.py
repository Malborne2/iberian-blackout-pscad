import xml.etree.ElementTree as ET
P = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
root = ET.parse(P).getroot()
for d in root.find('definitions'):
    n = d.get('name')
    if n in ('pgb', 'datalabel', 'multimeter'):
        print('=' * 70)
        print(ET.tostring(d, encoding='unicode')[:3500])
