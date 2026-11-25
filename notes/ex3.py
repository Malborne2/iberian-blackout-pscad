import xml.etree.ElementTree as ET
p = r"C:\Users\Public\Documents\PSCAD\5.1.0\Examples\DieselEngine\Diesel_Generator.pscx"
root = ET.parse(p).getroot()
defs = root.find('definitions')
main = [d for d in defs if d.get('name') == 'Main'][0]
sch = main.find('schematic')
for k in sch:
    if k.tag == 'paramlist':
        continue
    print(k.tag, k.get('classid'), k.get('defn'), 'id=', k.get('id'), 'x=', k.get('x'), 'y=', k.get('y'),
          'w=', k.get('w'), 'h=', k.get('h'), 'orient=', k.get('orient'))
    for c in k:
        if c.tag == 'paramlist':
            for pp in c:
                print("      ", pp.get('name'), '=', pp.get('value'))
        elif c.tag in ('vertex',):
            print("      vertex", c.attrib)
        else:
            print("      <", c.tag, ">", c.attrib)
