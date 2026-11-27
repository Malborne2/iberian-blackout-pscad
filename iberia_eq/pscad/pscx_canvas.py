r"""Offline PSCAD canvas: place components, wires and buses straight into a .pscx file (S30 sec 23, owner: case
generation must not take 8 minutes). Drop-in for the few mhi.pscad calls build_v2.py uses:

    cv = OfflineCanvas(pscx_path)          # loads the project file; Main canvas
    c = cv.add_component("master", "const", x, y, 0); c.parameters(Value="1.0"); P = c.ports()   # P["OUT"].x/.y (grid)
    cv.create_wire((x0, y0), (x1, y1)); b = cv.create_bus((x0, y), (x1, y)); b.parameters(Name="B_X")
    cv.project_parameters(time_step="20"); cv.save()

Coordinates are grid units (the file stores grid x 18), orientation 0 only. Ports come from the definition's <graphics>
Port elements whose `cond` holds for the component's parameters (as PSCAD evaluates them). Choice parameters given as
labels ("YES", "IMPEDANCE") are stored as their index, as the automation API does. Verified against an API-generated
case with compare_pscx.py (RUNLOG S30 sec 23) before use.
"""
import random, re
import xml.etree.ElementTree as ET

MASTER = r"C:\Program Files (x86)\PSCAD\5.1.0\master.pslx"
G = 18

class _P:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"({self.x},{self.y})"

def _cond(expr, prm):
    """evaluate a PSCAD port / enable condition such as '(C1T>=2)&&(GroundS==0)' or 'View==1' for parameter values."""
    if expr is None or expr.strip() in ("", "true"): return True
    if expr.strip() == "false": return False
    e = expr.replace("&&", " and ").replace("||", " or ")
    e = re.sub(r"!(?!=)", " not ", e)
    lo = {k.lower(): v for k, v in prm.items()}                       # PSCAD names are case-insensitive (compare: Conv / conv)
    def val(m):
        v = lo.get(m.group(0).lower())
        if v is None: raise KeyError(f"condition '{expr}': unknown name {m.group(0)}")
        try: return repr(float(v))
        except ValueError: return repr(v)
    e = re.sub(r"\b[A-Za-z_]\w*\b", lambda m: m.group(0) if m.group(0) in ("and", "or", "not", "true", "false") else val(m), e)
    e = e.replace("true", "True").replace("false", "False")
    return bool(eval(e, {"__builtins__": {}}, {}))

class _Defn:
    def __init__(self, el):
        self.el = el; self.params = []; self.choice = {}
        form = el.find("form")
        for p in (form.iter("parameter") if form is not None else []):
            nm = p.get("name"); v = p.find("value"); self.params.append((nm, v.text if v is not None and v.text is not None else ""))
            if p.get("type") == "Choice":
                self.choice[nm] = [(c.text.split("=", 1)[0].strip(), c.text.split("=", 1)[1].strip()) for c in p.findall("choice") if c.text and "=" in c.text]
        self.ports = []
        g = el.find("graphics")
        for p in (g.iter("Port") if g is not None else []):
            q = {x.get("name"): x.get("value") for x in p.iter("param")}
            self.ports.append((q.get("name", "").split(":")[0], int(float(p.get("x"))), int(float(p.get("y"))), q.get("cond")))

class Comp:
    def __init__(self, cv, lib, name, x, y, d):
        self.cv, self.lib, self.name, self.x, self.y, self.d = cv, lib, name, x, y, d
        self.prm = dict(d.params); self.id = cv._id()
    def parameters(self, **kw):
        for k, v in kw.items():
            v = str(v)
            if k in self.d.choice:                                     # label -> index, like the automation API
                for idx, lbl in self.d.choice[k]:
                    if v == idx or v.strip().lower() == lbl.lower() or v.strip().lower() == lbl.split()[0].lower().rstrip(","):
                        v = idx; break
            self.prm[k] = v
        return dict(self.prm)
    def ports(self):
        out = {}
        for nm, px, py, cond in self.d.ports:
            if nm and _cond(cond, self.prm): out[nm] = _P(self.x + px // G, self.y + py // G)
        return out
    def xml(self):
        e = ET.Element("User", {"classid": "UserCmp", "id": str(self.id), "name": f"{self.lib}:{self.name}", "x": str(self.x * G), "y": str(self.y * G),
                                "w": "40", "h": "40", "z": "-1", "orient": "0", "defn": f"{self.lib}:{self.name}", "link": "-1", "disable": "false"})
        pl = ET.SubElement(e, "paramlist", {"name": "", "link": "-1", "crc": "0"})
        for k, v in self.prm.items(): ET.SubElement(pl, "param", {"name": k, "value": v})
        return e

class _Bus:
    def __init__(self, el): self.el = el
    def parameters(self, **kw):
        pl = self.el.find("paramlist")
        for k, v in kw.items():
            for p in pl:
                if p.get("name") == k: p.set("value", str(v))
        return {p.get("name"): p.get("value") for p in pl}

class OfflineCanvas:
    def __init__(self, pscx, canvas="Main"):
        self.path = pscx; self.tree = ET.parse(pscx); self.root = self.tree.getroot(); self.proj = self.root.get("name")
        self.main = [d for d in self.root.iter("Definition") if d.get("name") == canvas][0].find("schematic")
        self.lib = {}
        for d in ET.parse(MASTER).getroot().iter("Definition"): self.lib[("master", d.get("name"))] = d
        for d in self.root.find("definitions"): self.lib[(self.proj, d.get("name"))] = d
        self._defs = {}; self._ids = set(); self.items = []
    def _id(self):
        while True:
            i = random.randint(100000000, 2000000000)
            if i not in self._ids: self._ids.add(i); return i
    def _d(self, lib, name):
        k = (lib, name)
        if k not in self._defs: self._defs[k] = _Defn(self.lib[k])
        return self._defs[k]
    def parameters(self): return {}
    def add_component(self, lib, name, x, y, orient=0):
        assert orient == 0, "offline canvas: orientation 0 only"
        c = Comp(self, lib, name, int(x), int(y), self._d(lib, name)); self.items.append(c); return c
    def create_wire(self, p0, p1):
        (x0, y0), (x1, y1) = p0, p1
        e = ET.Element("Wire", {"classid": "WireOrthogonal", "id": str(self._id()), "name": "", "x": str(x0 * G), "y": str(y0 * G),
                                "w": str(abs(x1 - x0) * G + 10), "h": str(abs(y1 - y0) * G + 10), "orient": "0", "disable": "false"})
        ET.SubElement(e, "vertex", {"x": "0", "y": "0"}); ET.SubElement(e, "vertex", {"x": str((x1 - x0) * G), "y": str((y1 - y0) * G)})
        self.items.append(e); return e
    def create_bus(self, p0, p1):
        (x0, y0), (x1, y1) = p0, p1
        e = ET.Element("Wire", {"classid": "Bus", "id": str(self._id()), "name": "", "x": str(x0 * G), "y": str(y0 * G),
                                "w": str(abs(x1 - x0) * G + 10), "h": str(abs(y1 - y0) * G + 24), "orient": "0", "disable": "false"})
        ET.SubElement(e, "vertex", {"x": "0", "y": "0"}); ET.SubElement(e, "vertex", {"x": str((x1 - x0) * G), "y": str((y1 - y0) * G)})
        pl = ET.SubElement(e, "paramlist", {"link": "-1"})
        for k, v in (("Name", ""), ("BaseKV", "0.0"), ("Vrms", "0"), ("VA", "0.0"), ("VM", "1.0"), ("type", "0"), ("VRMS", "0")):
            ET.SubElement(pl, "param", {"name": k, "value": v})
        self.items.append(e); return _Bus(e)
    def project_parameters(self, **kw):
        pl = self.root.find("paramlist")
        for k, v in kw.items():
            for p in pl:
                if p.get("name") == k: p.set("value", str(v))
    def save(self):
        for it in self.items: self.main.append(it.xml() if isinstance(it, Comp) else it)
        self.items = []; self.tree.write(self.path, encoding="unicode")
