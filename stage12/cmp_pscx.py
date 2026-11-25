r"""S26: compare two .pscx parameter blocks (project-level) and report differences.

usage: python stage12\cmp_pscx.py <a.pscx> <b.pscx>
"""
import sys, xml.etree.ElementTree as ET


def proj_params(p):
    r = ET.parse(p).getroot()
    pl = r.find("paramlist")
    return {q.get("name"): q.get("value") for q in pl.findall("param")}


a, b = sys.argv[1], sys.argv[2]
A, B = proj_params(a), proj_params(b)
keys = sorted(set(A) | set(B))
for k in keys:
    if A.get(k) != B.get(k):
        print(f"{k:32s} A={A.get(k)!r:40s} B={B.get(k)!r}")
print(f"\nproject name: {ET.parse(a).getroot().get('name')} / {ET.parse(b).getroot().get('name')}")
