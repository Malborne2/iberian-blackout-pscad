import xml.etree.ElementTree as ET
P = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
root = ET.parse(P).getroot()
for d in root.find('definitions'):
    if d.get('name') != 'xfmr-3p2w':
        continue
    for prm in d.findall('.//parameter'):
        if prm.get('name') in ('YD1', 'YD2', 'Tap', 'Lead', 'Ideal', 'View', 'Sat'):
            print(prm.get('name'), '=', (prm.findtext('value') or '').strip())
            for c in prm.findall('choice'):
                print('    ', (c.text or '').strip())
    break
