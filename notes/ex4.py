import xml.etree.ElementTree as ET
p = r"C:\Users\Public\Documents\PSCAD\5.1.0\Examples\FixedLoad\fixedload.pscx"
root = ET.parse(p).getroot()
defs = root.find('definitions')
print("defs:", [(d.get('name'), d.get('classid')) for d in defs])
main = [d for d in defs if d.get('name') == 'Main'][0]
sch = main.find('schematic')
for k in sch:
    if k.tag == 'paramlist':
        continue
    info = [k.tag, k.get('classid'), k.get('defn') or '', 'id=' + str(k.get('id')),
            'x=%s y=%s w=%s h=%s o=%s' % (k.get('x'), k.get('y'), k.get('w'), k.get('h'), k.get('orient'))]
    print(" ".join(info))
    pl = k.find('paramlist')
    if pl is not None and k.tag == 'User':
        vals = {pp.get('name'): pp.get('value') for pp in pl}
        print("     ", vals)
    if k.tag == 'Wire':
        print("     ", [(v.get('x'), v.get('y')) for v in k.findall('vertex')])
