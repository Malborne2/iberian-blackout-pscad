import re

path = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
text = open(path, encoding="utf-8", errors="replace").read()
i = text.find('<Definition classid="UserCmpDefn" name="excac_2016"')
j = text.find("</Definition>", i)
seg = text[i:j]
print("definition", len(seg), "chars")

# choice parameter TYPE and its choices
for m in re.finditer(r'<parameter[^>]*name="TYPE"[^>]*>(.*?)</parameter>', seg, re.S):
    body = m.group(1)
    print("\nTYPE block:")
    print(re.sub(r"<[^>]+>", " ", body)[:1500])

# all help texts that mention AC1C or rectifier
helps = re.findall(r"<help><!\[CDATA\[(.*?)\]\]></help>", seg, re.S)
print("\nhelp entries:", len(helps))
for h in helps:
    if h.strip():
        print(" -", h.strip()[:300])
