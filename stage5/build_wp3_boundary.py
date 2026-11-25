"""Combine one inward meter per bus-39 corridor from generated variants."""
from pathlib import Path
import xml.etree.ElementTree as ET

folder = Path(r'C:\PSCAD_work\s22')
raw = (folder/'wp3_meter.pscx').read_bytes()
name = 'wp3_fr39'
root = ET.fromstring(raw.replace(b'wp3_meter:', (name+':').encode()))
root.set('name', name)


def main(r):
    return next(d for d in r.find('definitions') if d.get('name') == 'Main').find('schematic')


canvas = main(root)
for index, corridor in enumerate(('T1_39', 'T9_39')):
    variant = main(ET.parse(folder/f'boundary_parts/lm_{corridor}.pscx').getroot())
    before = {e.get('id') for e in variant}
    anchor = {'T1_39': ('468','810'), 'T9_39': ('396','1278')}[corridor]
    line = next(e for e in canvas if e.get('defn') == 'master:pi_section' and (e.get('x'),e.get('y')) == anchor)
    stub = str(int(line.get('id')) + 1 + index)
    assert stub not in before
    canvas.remove(next(e for e in canvas if e.get('id') == stub))
    for e in variant:
        iid = int(e.get('id', '-1'))
        base = 1705000000 + 20*index
        if base <= iid < base+20:
            e.set('id', str(iid + 100*index))
            # Shift the remote instrumentation only, not the line-end labels.
            if int(e.get('y')) >= (98+16*index)*18:
                if iid <= base+4:
                    e.set('x', str(int(e.get('x')) + 10*18))
            for p in e.findall('paramlist/param'):
                if p.get('value','').startswith(f'LM{index+1}'):
                    p.set('value', 'FR'+p.get('value')[2:])
            canvas.append(e)
ids = [e.get('id') for e in canvas if e.get('id')]
assert len(ids) == len(set(ids))
with (folder/(name+'.pscx')).open('xb') as out:
    ET.ElementTree(root).write(out, encoding='utf-8', xml_declaration=True)
