"""Match ground components to nearby transformers / sources."""
import re

s = open('Spanish_grid_model.pscx', encoding='utf-8', errors='replace').read()


def inst(defn):
    out = []
    for m in re.finditer(r'<User\b[^>]*defn="%s"[^>]*>' % re.escape(defn), s):
        h = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
        out.append((int(h['x']), int(h['y']), int(h['w']), int(h['h']), h.get('orient')))
    return out


gnds = inst('master:ground')
print('grounds', len(gnds))
for defn in ('master:xfmr-3p2w', 'master:source3', 'master:capacitor', 'master:voltmeter'):
    for (x, y, w, h, o) in inst(defn):
        near = [(gx, gy) for (gx, gy, gw, gh, go) in gnds
                if abs(gx - x) < 90 and abs(gy - y) < 90]
        print('%-22s (%4d,%5d) o=%s  grounds nearby: %s' % (defn.split(':')[1], x, y, o, near))
