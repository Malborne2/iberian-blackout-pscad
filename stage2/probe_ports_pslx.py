import re

path = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
text = open(path, encoding="utf-8", errors="replace").read()

for name in ("xfmr_3p2w", "xfmr-3p2w", "source3", "voltmetergnd", "multimeter"):
    i = text.find('<Definition classid="UserCmpDefn" name="%s"' % name)
    if i < 0:
        i = text.find('name="%s"' % name)
    j = text.find("</Definition>", i)
    seg = text[i:j]
    print("\n=====", name, "definition chars", len(seg))
    for m in re.finditer(r"<port [^>]*?/>|<port [^>]*?>", seg):
        print("   ", m.group(0)[:180])
