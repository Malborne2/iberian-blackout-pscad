"""Add an independent bus-to-terminal AC power meter to the WP3 case."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET

folder = Path(r'C:\PSCAD_work\s22')
source = folder / 'wp3_refs.pscx'
target = folder / 'wp3_meter.pscx'
root = ET.fromstring(source.read_bytes().replace(b'wp3_refs:', b'wp3_meter:'))
root.set('name', target.stem)
canvas = next(d for d in root.find('definitions') if d.get('name') == 'Main').find('schematic')
lead = next(e for e in canvas if e.get('id') == '292195335')
assert (lead.get('x'), lead.get('y')) == ('306', '1530')
assert [(v.get('x'), v.get('y')) for v in lead] == [('0','0'),('36','0'),('36','36'),('72','36')]
canvas.remove(lead)
used = {e.get('id') for e in root.iter()}
ids = (str(i) for i in range(1710100000,1710100100) if str(i) not in used)


def add(kind, x, y, **params):
    obj = copy.deepcopy(next(e for e in canvas if e.get('defn') == 'master:' + kind))
    obj.attrib.update(id=next(ids), x=str(x*18), y=str(y*18), orient='0')
    for p in obj.findall('paramlist/param'):
        if p.get('name') in params:
            p.set('value', str(params.pop(p.get('name'))))
    assert not params, params
    canvas.append(obj)


add('multimeter', 9, 98, Name='HVDC_AC', S=1, MeasP=1, MeasQ=1, MeasPh=0,
    RMS=0, MeasI=0, MeasV=0, Dis=1, P='', Q='', Ph='')
for x,y,name in [(21,87,'HV9BUS'),(8,98,'HV9BUS'),(17,85,'HV9TERM'),(10,98,'HV9TERM')]:
    add('nodelabel', x, y, Name=name, MeasV=0)
with target.open('xb') as out:
    ET.ElementTree(root).write(out, encoding='utf-8', xml_declaration=True)
print(target, 'HVDC_AC A=bus side, B=terminal side, Pd/Qd base 1 MVA')
