import xml.etree.ElementTree as ET

path = r"C:\Users\Ibrahim\OneDrive - Østfold University College\PhD Projects\PSCAD\Spanish_netowrk_model\Spanish_grid_model.pscx"
root = ET.parse(path).getroot()

def walk(el, depth=0, maxdepth=3):
    if depth > maxdepth:
        return
    kids = list(el)
    print("  " * depth + f"<{el.tag}> " + str(el.attrib)[:160] + f"  (kids={len(kids)})")
    for k in kids:
        walk(k, depth + 1, maxdepth)

walk(root, 0, 2)
