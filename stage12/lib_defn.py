r"""S26: dump a master-library definition's parameters and graphics ports.

usage: python stage12\lib_defn.py <pslx> <definition-name>
"""
import sys, xml.etree.ElementTree as ET

src, want = sys.argv[1], sys.argv[2]
r = ET.parse(src).getroot()
hits = [d for d in r.iter("Definition") if d.get("name") == want]
if not hits:
    names = sorted({d.get("name") or "" for d in r.iter("Definition")})
    print("not found. names containing the string:")
    print([n for n in names if want.lower() in n.lower()][:20])
    raise SystemExit(1)
d = hits[0]
print("definition:", d.get("name"), "id", d.get("id"), "crc", d.get("crc"))
pl = d.find("paramlist")
if pl is not None:
    for q in pl.findall("param"):
        print(f"  PARAM {q.get('name')} = {q.get('value')}  desc={q.get('desc')}")
g = d.find("graphics")
if g is not None:
    for p in g.iter("Port"):
        print("  PORT", p.attrib)
descr = d.find("form")
if descr is not None:
    txt = " ".join(t.strip() for t in descr.itertext() if t.strip())
    print("  form:", txt[:400])
