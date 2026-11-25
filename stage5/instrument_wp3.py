"""Create a separate run-16 derivative with plant reference recorders."""
import argparse
import copy
from pathlib import Path
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('target', type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    old = ET.fromstring(raw).get('name')
    new = args.target.stem
    root = ET.fromstring(raw.replace(f'{old}:'.encode(), f'{new}:'.encode()).replace(
        f'name="{old}"'.encode(), f'name="{new}"'.encode(), 1))
    canvas = next(e for e in root.find('definitions') if e.get('name') == 'RES_Plant').find('schematic')
    used = {e.get('id') for e in root.iter()}
    ids = (str(i) for i in range(1710000000, 1710000100) if str(i) not in used)
    for signal, y in [('IDREF', 1764), ('IQREF', 1872)]:
        for kind, x in [('datalabel', 180), ('pgb', 252)]:
            obj = copy.deepcopy(next(e for e in canvas if e.get('defn') == 'master:' + kind))
            obj.attrib.update(id=next(ids), x=str(x), y=str(y), orient='0')
            for p in obj.findall('paramlist/param'):
                key = p.get('name')
                if key in {'Name', 'UseSignalName', 'Scale', 'Units'}:
                    p.set('value', {'Name': signal, 'UseSignalName': '0', 'Scale': '1', 'Units': 'pu'}[key])
            canvas.append(obj)
        wire = ET.SubElement(canvas, 'Wire', dict(classid='WireOrthogonal', id=next(ids), name='',
            x='180', y=str(y), w='82', h='10', orient='0', disable='false'))
        ET.SubElement(wire, 'vertex', dict(x='0', y='0'))
        ET.SubElement(wire, 'vertex', dict(x='72', y='0'))
    with args.target.open('xb') as out:
        ET.ElementTree(root).write(out, encoding='utf-8', xml_declaration=True)
    print(f'{args.target}: added IDREF and IQREF recorders in shared RES_Plant; dispatch unchanged')


if __name__ == '__main__':
    main()
