"""Find limiter blocks in master.pslx and their field content types."""
import xml.etree.ElementTree as ET

P = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
root = ET.parse(P).getroot()
for d in root.iter("Definition"):
    n = d.get("name") or ""
    if "limit" in n.lower() or "limiter" in n.lower():
        print("=" * 50, n, d.get("classid"))
        form = d.find("form")
        if form is None:
            continue
        for cat in form.iter("category"):
            for par in cat.findall("parameter"):
                print(f"   {par.get('name'):10} type={par.get('type'):8} content={par.get('content_type')} "
                      f"desc={ (par.get('desc') or '')[:40]}")
        g = d.find("graphics")
        if g is not None:
            for e in g:
                if e.tag == "Port":
                    print("   Port", e.attrib)
