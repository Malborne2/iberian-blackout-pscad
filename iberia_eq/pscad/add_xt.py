r"""Publish the SyncUnit machine reactances as module parameters, so a step-up transformer can be lumped into the
machine (v2 node budget, RUNLOG S30 sec 5).

usage: python iberia_eq\pscad\add_xt.py --pscx C:\PSCAD_work\<case>.pscx [--pscx ...]
The project must NOT be loaded in PSCAD (skill P12). Refuses to patch twice.

The sync_machine inside SyncUnit uses reactances + open-circuit time constants (Xd, Xd', Xd'', Xq, Xq', Xq'', Xp; Tdo',
Tdo'', Tqo', Tqo''). A series reactance Xt (the step-up) is represented exactly in that form by adding Xt to every
reactance and leaving the open-circuit time constants unchanged. The new parameters default to the current values, so
every existing instance is unchanged; the generator (build_v2.py) passes base + Xt.
"""
import argparse, copy
import xml.etree.ElementTree as ET
from pathlib import Path

FIELDS = [("Xd", "XmD"), ("Xd_", "XmD1"), ("Xd__", "XmD2"), ("Xq", "XmQ"), ("Xq_", "XmQ1"), ("Xq__", "XmQ2"), ("Xp", "XmP")]
G = 18
PARAM_XML = ('<parameter desc="{d}" name="{n}" group="" unit="" min="-1e+308" max="+1e+308" content_type="Constant" '
             'type="Real" helpmode="Append" intent="Input" dim="1" animate="false"><value>{v}</value><cond /><help /><vis /></parameter>')
_id = [1_395_000_000]


def nid():
    _id[0] += 1; return str(_id[0])


def patch(defn):
    d = copy.deepcopy(defn); cat = d.find("form").find("category")
    if any(p.get("name") == "XmD" for p in cat.findall("parameter")): raise SystemExit("already patched")
    sch = d.find("schematic")
    sm = [u for u in sch.findall("User") if u.get("defn") == "master:sync_machine"]
    if len(sm) != 1: raise SystemExit("expected one sync_machine")
    pv = {p.get("name"): p for p in sm[0].find("paramlist").findall("param")}
    imp_t = [u for u in sch.findall("User") if u.get("defn") == "master:import"][0]
    for k, (field, pname) in enumerate(FIELDS):
        base = pv[field].get("value")
        cat.append(ET.fromstring(PARAM_XML.format(n=pname, d=f"machine {field} (pu), default {base}; + Xt to lump a step-up", v=base)))
        pv[field].set("value", pname)
        imp = copy.deepcopy(imp_t); imp.set("id", nid()); imp.set("x", str(62 * G)); imp.set("y", str((49 + 2 * k) * G))
        for p in imp.find("paramlist").findall("param"):
            if p.get("name") == "Name": p.set("value", pname)
        sch.append(imp)
    return d


ap = argparse.ArgumentParser(); ap.add_argument("--pscx", action="append", required=True); a = ap.parse_args()
for dst in a.pscx:
    root = ET.parse(dst).getroot(); holder = root.find("definitions")
    old = [d for d in holder if d.get("name") == "SyncUnit"][0]
    new = patch(old); new.set("id", old.get("id")); holder.remove(old); holder.append(new)
    Path(dst).write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
    print("SyncUnit reactances published (XmD XmD1 XmD2 XmQ XmQ1 XmQ2 XmP) in", dst)
