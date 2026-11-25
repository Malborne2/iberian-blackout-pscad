r"""S26: list the internal datalabels (output names) of a master-library definition.

usage: python stage12\lib_labels.py <pslx> <definition-name>
"""
import sys, xml.etree.ElementTree as ET

src, want = sys.argv[1], sys.argv[2]
r = ET.parse(src).getroot()
d = [x for x in r.iter("Definition") if x.get("name") == want][0]
s = d.find("schematic")
print("definition:", want)
for c in s:
    dn = (c.get("defn") or "")
    pl = c.find("paramlist")
    p = {} if pl is None else {q.get("name"): q.get("value") for q in pl.findall("param")}
    if dn.split(":")[-1] in ("datalabel", "pgb", "export", "import", "xnode") or c.get("x") is None:
        if c.get("x") is None:
            continue
        print(f"  {dn.split(':')[-1]:10s} ({int(c.get('x'))//18:4d},{int(c.get('y'))//18:4d}) "
              f"Name={p.get('Name')} Units={p.get('Units')}")
