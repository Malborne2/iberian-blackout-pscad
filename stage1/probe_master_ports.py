"""Port offsets of master:pi_section and master:xnode from master.pslx."""
import xml.etree.ElementTree as ET

P = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
root = ET.parse(P).getroot()
for d in root.iter("Definition"):
    if d.get("name") in ("pi_section", "xnode", "nodelabel", "datalabel"):
        print("=" * 40, d.get("name"), d.get("classid"), "id", d.get("id"))
        g = d.find("graphics")
        if g is not None:
            for e in g:
                if e.tag == "Port":
                    print("   Port", e.attrib)
                    pl = e.find("paramlist")
                    if pl is not None:
                        print("        ", {p.get("name"): p.get("value") for p in pl.findall("param")})
        sc = d.find("schematic")
        if sc is not None:
            for e in sc:
                if e.tag == "User":
                    print("   User", e.get("defn"), e.get("x"), e.get("y"), e.get("w"), e.get("h"), e.get("orient"))
