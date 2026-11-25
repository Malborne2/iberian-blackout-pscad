"""Look for a selector / switch block in master.pslx (needed for PMODE)."""
import xml.etree.ElementTree as ET

P = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
root = ET.parse(P).getroot()
want = ("select", "switch", "sw", "selsw", "poly", "if")
for d in root.iter("Definition"):
    n = (d.get("name") or "").lower()
    if not any(w in n for w in ("select", "switch", "poly", "logic", "cmp", "compare")):
        continue
    form = d.find("form")
    fields = []
    if form is not None:
        for cat in form.iter("category"):
            for par in cat.findall("parameter"):
                fields.append(f"{par.get('name')}:{par.get('type')}/{par.get('content_type')}")
    print(f"{d.get('name'):24} {d.get('classid'):12} {', '.join(fields)[:120]}")
