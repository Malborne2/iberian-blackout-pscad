"""Dump a library definition: description, form parameters, ports."""
import re, sys

path = r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx'
s = open(path, encoding='utf-8', errors='replace').read()
name = sys.argv[1]
m = re.search(r'<Definition classid="UserCmpDefn" name="%s"' % re.escape(name), s)
if not m:
    print('not found')
    sys.exit()
a = m.start()
b = s.find('</Definition>', a)
blk = s[a:b]
d = re.search(r'name="Description" value="([^"]*)"', blk)
print('DESCRIPTION:', d.group(1) if d else '?')
for p in re.finditer(r'<parameter ([^>]*)>(.*?)</parameter>', blk, re.S):
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', p.group(1)))
    body = p.group(2)
    val = re.search(r'<value><!\[CDATA\[(.*?)\]\]></value>', body, re.S)
    desc = attrs.get('desc', '')
    mn = attrs.get('min')
    mx = attrs.get('max')
    ch = re.findall(r'<choice[^>]*><!\[CDATA\[(.*?)\]\]></choice>', body)
    print('  %-14s %-42s val=%-10s min=%s max=%s %s'
          % (attrs.get('name'), desc, (val.group(1) if val else ''), mn, mx,
             ('choices=' + str(ch)) if ch else ''))
