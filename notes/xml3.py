import xml.etree.ElementTree as ET

path = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx"
root = ET.parse(path).getroot()
defs = root.find('definitions')
main = [d for d in defs if d.get('name') == 'Main'][0]
print("Main attrib", main.attrib)
for ch in main:
    print(f"  <{ch.tag}> {ch.attrib} kids={len(list(ch))}")
    for ch2 in list(ch)[:6]:
        print(f"     <{ch2.tag}> {ch2.attrib} kids={len(list(ch2))}")
