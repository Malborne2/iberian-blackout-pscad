import xml.etree.ElementTree as ET
p = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
root = ET.parse(p).getroot()
defs = root.find('definitions')

want = ['sync_machine', 'multimass2', 'excst_2016_2', 'th_gov', 'hy_gov', 'switch', 'tbreakn',
        'timer', 'datalabel', 'pgb', 'voltmeter', 'ammeter', 'power', 'freq-meas',
        'fixed_load', 'source3', 'xfmr_3p2w', 'photovoltaic_source', 'wind_source', 'ground', 'annotation']
for d in defs:
    if d.get('name') in want:
        print("=" * 70)
        print("DEFN", d.get('name'), d.get('classid'), d.attrib)
        for ch in d:
            print("   child <", ch.tag, ">", ch.attrib, "kids=", len(list(ch)))
            if ch.tag == 'schematic':
                for k in ch:
                    if k.tag == 'paramlist':
                        print("       paramlist:")
                        for pp in k:
                            print("         ", pp.tag, pp.attrib)
                    else:
                        print("       ", k.tag, k.get('classid'), k.get('name'), k.get('x'), k.get('y'), 'kids=', len(list(k)))
