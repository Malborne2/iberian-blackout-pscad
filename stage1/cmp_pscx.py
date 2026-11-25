"""Compare two .pscx files structurally (tags/attrs/params), ignoring the creator/revisor stamps."""
import sys
import collections
import xml.etree.ElementTree as ET

A, B = sys.argv[1], sys.argv[2]


def fingerprint(path):
    root = ET.parse(path).getroot()
    out = collections.Counter()
    for e in root.iter():
        key = (e.tag, tuple(sorted((k, v) for k, v in e.attrib.items() if k not in ("crc", "date"))))
        out[key] += 1
    return out, root


fa, ra = fingerprint(A)
fb, rb = fingerprint(B)
only_a = fa - fb
only_b = fb - fa
print("A =", A)
print("B =", B)
print(f"A elements: {sum(fa.values())}, B elements: {sum(fb.values())}")
print(f"only in A: {sum(only_a.values())}, only in B: {sum(only_b.values())}")
for k, v in list(only_a.items())[:25]:
    print("  A only", v, k[0], dict(k[1][:6]))
for k, v in list(only_b.items())[:25]:
    print("  B only", v, k[0], dict(k[1][:6]))
for name in ("creator", "revisor", "time_duration", "time_step", "sample_step", "PlotType"):
    for p in ra.iter("param"):
        if p.get("name") == name:
            va = p.get("value")
            break
    else:
        va = None
    for p in rb.iter("param"):
        if p.get("name") == name:
            vb = p.get("value")
            break
    else:
        vb = None
    if va != vb:
        print(f"  differs: {name}: A={va!r} B={vb!r}")
