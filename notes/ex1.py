import xml.etree.ElementTree as ET
p = r"C:\Users\Public\Documents\PSCAD\5.1.0\Examples\DieselEngine\Diesel_Generator.pscx"
root = ET.parse(p).getroot()
print("root", root.tag, root.attrib)
for ch in root:
    print(" <", ch.tag, ">", ch.attrib, "kids=", len(list(ch)))
out = root.find('output')
if out is not None:
    print("\n=== output ===")
    print(ET.tostring(out, encoding='unicode')[:4000])
