import xml.etree.ElementTree as ET
p = r"C:\Users\Public\Documents\PSCAD\5.1.0\Examples\DieselEngine\Diesel_Generator.pscx"
root = ET.parse(p).getroot()
targets = {'71792168','71778296','71773400','71774216'}
for el in root.iter():
    if el.get('id') in targets:
        print(el.tag, el.attrib)
        pl = el.find('paramlist')
        if pl is not None:
            for pp in pl:
                print("    ", pp.tag, pp.attrib)
print("--- definitions names ---")
for d in root.find('definitions'):
    print(d.get('name'), d.get('classid'), len(list(d)))
