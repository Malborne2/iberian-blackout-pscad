"""Small helpers for editing the .pscx XML by element id."""
import re

PATH = 'Spanish_grid_model.pscx'


def load(path=PATH):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def save(s, path=PATH):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s)


BLOCK = re.compile(r'<(Wire|User|Gfx)\b[^>]*>.*?</\1>', re.S)


def block_span(s, eid):
    """Return (start, end) of the element whose header has id="eid"."""
    for m in BLOCK.finditer(s):
        if 'id="%s"' % eid in s[m.start():m.start() + 300]:
            return m.start(), m.end()
    return None


def remove(s, eid):
    sp = block_span(s, eid)
    if sp is None:
        raise KeyError(eid)
    return s[:sp[0]] + s[sp[1]:]


def get(s, eid, name):
    a, b = block_span(s, eid)
    m = re.search(r'name="%s" value="([^"]*)"' % name, s[a:b])
    return m.group(1) if m else None


def setp(s, eid, name, value):
    a, b = block_span(s, eid)
    blk = s[a:b]
    new, n = re.subn(r'(name="%s" value=")[^"]*(")' % name,
                     lambda m: m.group(1) + value + m.group(2), blk)
    if n == 0:
        raise KeyError('%s has no param %s' % (eid, name))
    return s[:a] + new + s[b:]


def list_ids(s, classid=None):
    out = []
    for m in BLOCK.finditer(s):
        hdr = s[m.start():s.index('>', m.start()) + 1]
        cid = re.search(r'classid="([^"]*)"', hdr)
        eid = re.search(r'\bid="([^"]*)"', hdr)
        if classid and (not cid or cid.group(1) != classid):
            continue
        out.append(eid.group(1) if eid else None)
    return out
