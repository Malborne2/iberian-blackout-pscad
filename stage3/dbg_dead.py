import collections
import xml.etree.ElementTree as ET

r = ET.parse(r"C:\PSCAD_work\iberia4.pscx").getroot()
m = [e for e in r.find("definitions") if e.get("name") == "Main"][0]
sc = m.find("schematic")


def params(e):
    pl = e.find("paramlist")
    return {} if pl is None else {p.get("name"): p.get("value") for p in pl.findall("param")}


src = next(e for e in sc if e.tag == "User" and e.get("defn") == "master:source3" and params(e).get("P") == "Pg7")
sp = params(src)
dead = []
for key in ("P", "Q", "V"):
    name = sp.get(key)
    print("key", key, "name", repr(name))
    if not name:
        continue
    hits = [e for e in sc if e.tag == "User" and e.get("defn") == "master:datalabel" and params(e).get("Name") == name]
    print("   datalabels:", [(e.get("id"), e.get("x"), e.get("y")) for e in hits])
    for e in hits:
        dx, dy = int(e.get("x")), int(e.get("y"))
        dead.append(e)
        for w in sc:
            if w.tag != "Wire":
                continue
            vs = [(int(v.get("x")) + dx, int(v.get("y")) + dy) for v in w.findall("vertex")]
            if (dx, dy) in vs:
                print("   wire", w.get("id"), "vs", vs)
                dead.append(w)
print("dead", len(dead), collections.Counter(e.tag for e in dead),
      collections.Counter(e.get("defn") for e in dead))
