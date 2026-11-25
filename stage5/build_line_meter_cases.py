"""Generate paired-end corridor metering variants, without editing loaded cases.

The two meters point BUS -> LINE. Their summed steady P must be line losses.
34 permanent meter pairs would exceed the Educational node budget, so each
variant instruments exactly one corridor while preserving the same dispatch.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    raw = args.source.read_bytes()
    root = ET.fromstring(raw)
    old = root.get('name')
    sc = next(d for d in root.find('definitions') if d.get('name') == 'Main').find('schematic')
    templates = {n: next(e for e in sc if e.get('defn') == 'master:' + n)
                 for n in ('multimeter', 'nodelabel', 'datalabel', 'pgb')}
    records = json.loads((Path(__file__).parents[1] / 'stage1/line_ports.json').read_text())['instances']
    by_anchor = {tuple(r['loc']): r for r in records}
    lines = [e for e in sc if e.get('defn') == 'master:pi_section']
    assert len(lines) == 34
    manifest = []
    skipped = []
    for line in lines:
        record = by_anchor[(int(line.get('x')) // 18, int(line.get('y')) // 18)]
        corridor = record['defn']
        if any(not any(e.get('id') == str(int(line.get('id')) + i) for e in sc)
               for i in (1, 2)):
            skipped.append({'corridor': corridor, 'reason': 'Original stub replaced; inspect existing MM9 before rewiring'})
            continue
        name = 'lm_' + corridor
        target = args.output / (name + '.pscx')
        if target.exists():
            raise FileExistsError(target)
        renamed = raw.replace((old + ':').encode(), (name + ':').encode())
        renamed = renamed.replace(('name="' + old + '"').encode(), ('name="' + name + '"').encode(), 1)
        r = ET.fromstring(renamed)
        s = next(d for d in r.find('definitions') if d.get('name') == 'Main').find('schematic')
        used = {int(e.get('id')) for e in r.iter() if e.get('id', '').isdigit()}
        counter = 1705000000

        def iid():
            nonlocal counter
            while counter in used:
                counter += 1
            used.add(counter)
            counter += 1
            return counter - 1

        def add(kind, x, y, params):
            e = copy.deepcopy(templates[kind])
            e.set('id', str(iid()))
            e.set('x', str(x * 18))
            e.set('y', str(y * 18))
            e.set('orient', '0')
            e.set('z', '1')
            pl = e.find('paramlist')
            for key, val in params.items():
                p = next((p for p in pl if p.get('name') == key), None)
                if p is None:
                    p = ET.SubElement(pl, 'param', {'name': key})
                p.set('value', str(val))
            s.append(e)
            return int(e.get('id'))

        def wire(x, y, dx, dy):
            w = ET.SubElement(s, 'Wire', {'classid': 'WireOrthogonal', 'id': str(iid()),
                'name': '', 'x': str(x * 18), 'y': str(y * 18),
                'w': str(abs(dx * 18) + 10), 'h': str(abs(dy * 18) + 10),
                'orient': '0', 'disable': 'false'})
            ET.SubElement(w, 'vertex', {'x': '0', 'y': '0'})
            ET.SubElement(w, 'vertex', {'x': str(dx * 18), 'y': str(dy * 18)})

        ends = []
        for idx, endpoint in enumerate(('in', 'out')):
            stubid = int(line.get('id')) + idx + 1
            stub = next(e for e in s if e.get('id') == str(stubid))
            assert stub.tag == 'Wire'
            x, y = int(stub.get('x')) // 18, int(stub.get('y')) // 18
            vertices = [(x + int(v.get('x')) // 18, y + int(v.get('y')) // 18)
                        for v in stub.findall('vertex')]
            outer = tuple(record[endpoint])
            assert len(vertices) == 2 and vertices[0] == outer
            inner = vertices[1]
            assert abs(inner[0] - outer[0]) + abs(inner[1] - outer[1]) == 1
            s.remove(stub)
            # Within MCP-verified empty rectangle (2,94)-(23,127).
            my = 98 + 16 * idx
            prefix = 'LM' + str(idx + 1)
            mid = add('multimeter', 9, my, {'Name': prefix, 'MeasP': 1, 'MeasQ': 1,
                'MeasI': 1, 'MeasV': 1, 'RMS': 1, 'IRMS': 0, 'MeasPh': 0,
                'Freq': 50, 'TS': '0.02 [s]', 'S': 1, 'BaseV': 1, 'BaseA': 1,
                'Dis': 0, 'P': prefix + 'P', 'Q': prefix + 'Q',
                'CurI': prefix + 'I', 'VolI': prefix + 'V', 'Vrms': prefix + 'RMS',
                'VolILL': '', 'Crms': '', 'Ph': ''})
            for point, port, label in ((outer, (8, my), prefix + 'BUS'),
                                       (inner, (10, my), prefix + 'LINE')):
                add('nodelabel', *point, {'Name': label, 'MeasV': 0})
                add('nodelabel', *port, {'Name': label, 'MeasV': 0})
            for j, quantity in enumerate(('P', 'Q', 'I', 'V', 'RMS')):
                cy = my + 2 + j * 2
                signal = prefix + quantity
                add('datalabel', 14, cy, {'Name': signal})
                add('pgb', 17, cy, {'Name': signal, 'UseSignalName': 0,
                    'enab': 1, 'Scale': 1, 'Units': {'P': 'MW', 'Q': 'Mvar', 'I': 'kA',
                    'V': 'kV', 'RMS': 'kV'}[quantity]})
                wire(14, cy, 3, 0)
            ends.append({'meter_iid': mid, 'outer': outer, 'inner': inner,
                         'meter_A': [8, my], 'meter_B': [10, my], 'prefix': prefix})
        # PSCAD may reuse graphic IDs across definitions; canvas IDs are scoped.
        ids = [e.get('id') for e in s if e.get('id', '').isdigit()]
        assert len(ids) == len(set(ids)), 'duplicate IDs'
        ET.indent(r)
        ET.ElementTree(r).write(target, encoding='utf-8', xml_declaration=True)
        assert target.read_bytes().count(b'master:pi_section') == raw.count(b'master:pi_section')
        manifest.append({'corridor': corridor, 'project': name, 'path': str(target),
            'line_iid': int(line.get('id')), 'line_params': {p.get('name'): p.get('value')
                for p in line.findall('paramlist/param')}, 'ends': ends,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    report = {'source': str(args.source), 'source_sha256': hashlib.sha256(raw).hexdigest(),
        'expected_nodes': 197, 'note': '191 baseline + 2 x 3, unverified until build',
        'empty_rectangle_mcp': [2, 94, 23, 127], 'cases': manifest, 'skipped': skipped}
    (args.output / 'manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Generated {len(manifest)} corridor variants; 2 independent end meters each.')
    print('Expected NODES 197, NPAGES unchanged; NOT build-proven.')
    print('Skipped:', skipped)
    print('T1_39:', next(m for m in manifest if m['corridor'] == 'T1_39'))


if __name__ == '__main__':
    main()
