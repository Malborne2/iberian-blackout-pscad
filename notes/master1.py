import xml.etree.ElementTree as ET
p = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
root = ET.parse(p).getroot()
print("root", root.tag, root.attrib)
defs = root.find('definitions')
print("n defs", len(defs))
names = []
for d in defs:
    names.append((d.get('name'), d.get('classid'), d.get('group')))
print(len(names))
for n in sorted(names, key=lambda t: (t[1] or '', t[0] or '')):
    print(" | ".join(str(x) for x in n))
