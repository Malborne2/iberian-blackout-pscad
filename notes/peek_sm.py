import xml.etree.ElementTree as ET, re
P = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
root = ET.parse(P).getroot()
for d in root.find('definitions'):
    if d.get('name') != 'sync_machine':
        continue
    # list parameters
    for cat in d.findall('.//category'):
        print('CATEGORY', cat.get('name'))
        for prm in cat.findall('parameter'):
            print(f"   {prm.get('type'):8s} {prm.get('name'):14s} {prm.get('desc')!r:46s} value={ (prm.findtext('value') or '').strip()!r}")
            ch = [ (c.text or '').strip() for c in prm.findall('choice')]
            if ch:
                print('        choices:', ch)
    break
