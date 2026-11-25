import xml.etree.ElementTree as ET
P = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
root = ET.parse(P).getroot()
for want in ('reactive_load', 'fixed_load', 'voltmeter'):
    for d in root.find('definitions'):
        if d.get('name') != want:
            continue
        print('=' * 30, want)
        for cat in d.findall('.//category'):
            print(' CATEGORY', cat.get('name'))
            for prm in cat.findall('parameter'):
                ch = [(c.text or '').strip() for c in prm.findall('choice')]
                print(f"   {prm.get('type'):8s} {prm.get('name'):8s} {prm.get('desc')!r:40s} val={(prm.findtext('value') or '').strip()!r}")
                if ch:
                    print('        choices:', ch)
        print(' PORTS/graphics:')
        for g in d.findall('.//graphics/port'):
            print('   port', g.get('name'), g.get('x'), g.get('y'))
        break
