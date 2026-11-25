import xml.etree.ElementTree as ET
P = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
root = ET.parse(P).getroot()
for d in root.find('definitions'):
    if d.get('name') != 'source3':
        continue
    for cat in d.findall('.//category'):
        print('CATEGORY', cat.get('name'))
        for prm in cat.findall('parameter'):
            print(f"   {prm.get('type'):8s} {prm.get('name'):10s} {prm.get('desc')!r:44s} val={(prm.findtext('value') or '').strip()!r}")
            ch = [(c.text or '').strip() for c in prm.findall('choice')]
            if ch:
                print('        choices:', ch)
            cnd = prm.find('cond')
            if cnd is not None and cnd.text:
                print('        cond:', cnd.text.strip())
    break
