import re, collections, sys, xml.etree.ElementTree as ET

path = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx"
tree = ET.parse(path)
root = tree.getroot()
print("root", root.tag, root.attrib)

# top-level children summary
for ch in root:
    n = len(list(ch))
    print(f"  <{ch.tag}> attrib={ch.attrib} children={n}")

print()
print("=== canvases ===")
for cv in root.iter('canvas'):
    comps = cv.find('components')
    nc = len(comps) if comps is not None else 0
    print(f"canvas name={cv.get('name')!r} id={cv.get('id')} comps={nc}")
