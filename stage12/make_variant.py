r"""Make one experiment folder from a settled case: copy <case.pscx> to <out>/ib6.pscx (project name stays
`ib6`, so the case's snapshot is valid there) and apply a JSON spec of EVENT-ONLY edits (S6: these survive a
snapshot). Then run it with: python stage12/run_instance.py <out> --snap <snapshot.snp>

spec keys (all optional):
  "project":    {"time_duration": "8", "sample_step": "500", ...}      run settings (StartType 1 is forced)
  "plants":     {"1": {"Tforce": 33.0}, ...}       RES_Plant by PSOUT index k (RES_Plant[k], not document order)
  "plants_all": {"Vt1": 1.5, ...}                   every RES_Plant
  "ov_report":  true                                 the report's six fleet OV settings, plant k -> setting (k-1)%6
                                                     (stage7/tune_ov_relays.py mapping, 1.111 pu delay 0.1 s assumed)
  "units":      {"31": {"Ttrip": 34.0, "Ptrip": -0.0771}, "France": {...}}   SyncUnit by bus
  "units_all":  {"H": 3.0}
  "breakers":   {"31": 34.0, "32": 34.5}             BRK3x trip time (compare X, absolute s)
  "ids":        {"<component id>": {"param": value}}
usage: python stage12/make_variant.py <case.pscx> <out folder> <spec.json>
"""
import json, os, re, sys, xml.etree.ElementTree as ET

UNIT = {"30": "993049547", "31": "1404126973", "32": "489869766", "37": "650097263", "France": "1766995819"}
OV = [("1.089", "1.5"), ("1.10", "0"), ("1.10", "0.5"), ("1.111", "0.1"), ("1.139", "0.2"), ("1.15", "0.6")]
BRK_ROW = {"30": 400, "31": 402, "32": 404, "37": 406}   # PLAN §2e: compare rows y = 400..406, x = 10

case, out, spec = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
root = ET.parse(case).getroot()
M = [d for d in root.iter("Definition") if d.get("name") == "Main"][0].find("schematic")


def P(el): return {q.get("name"): q for q in el.find("paramlist").findall("param")}


def setp(el, k, v):
    pp = P(el)
    if k not in pp: raise KeyError(f"{el.get('defn')} {el.get('id')} has no parameter {k}")
    pp[k].set("value", str(v))


log = []
plants = [c for c in M if (c.get("defn") or "").endswith(":RES_Plant")]
assert len(plants) == 18
byid = {c.get("id"): c for c in M if c.get("id")}
# PSOUT index RES_Plant[k] -> document position, MEASURED in S27 Batch 1 r3 (Tforce on the 520 MVA Granada plant
# tripped RES_Plant[18]): k=1 -> doc 2 (3315 MVA), k=2..17 -> doc k+1, k=18 -> doc 1 (520 MVA, Granada).
# (The S26 numbering NB had 1 <-> 18 swapped; both are on bus 33.)
PS2DOC = {1: 1, 18: 0, **{k: k for k in range(2, 18)}}
assert P(plants[PS2DOC[1]])["Sbase"].get("value").startswith("3315") and P(plants[PS2DOC[18]])["Sbase"].get("value").startswith("520")
for k, kv in spec.get("plants", {}).items():
    for p, v in kv.items(): setp(plants[PS2DOC[int(k)]], p, v); log.append(f"plant {k} {p}={v}")
for p, v in spec.get("plants_all", {}).items():
    for c in plants: setp(c, p, v)
    log.append(f"all plants {p}={v}")
if spec.get("ov_report"):
    for k, c in enumerate(plants, 1):
        vt, tt = OV[(k - 1) % 6]; setp(c, "Vt1", vt); setp(c, "Tt1", tt)
    log.append("report OV settings on Vt1/Tt1")
for b, kv in spec.get("units", {}).items():
    for p, v in kv.items(): setp(byid[UNIT[b]], p, v); log.append(f"unit {b} {p}={v}")
for p, v in spec.get("units_all", {}).items():
    for i in UNIT.values(): setp(byid[i], p, v)
    log.append(f"all units {p}={v}")
for b, t in spec.get("breakers", {}).items():
    cmp_ = [c for c in M if c.get("defn") == "master:compare" and int(c.get("y")) // 18 == BRK_ROW[b] and int(c.get("x")) // 18 == 10]
    assert len(cmp_) == 1, (b, len(cmp_))
    setp(cmp_[0], "X", t); log.append(f"BRK{b} at {t}")
for i, kv in spec.get("ids", {}).items():
    for p, v in kv.items(): setp(byid[i], p, v); log.append(f"id {i} {p}={v}")

txt = ET.tostring(root, encoding="unicode")
proj = dict(spec.get("project", {})); proj["StartType"] = "1"
for n, v in proj.items():
    txt, k = re.subn(r'(<param name="%s" value=")[^"]*(")' % n, r'\g<1>%s\g<2>' % v, txt, count=1)
    assert k == 1, n
    log.append(f"project {n}={v}")
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "ib6.pscx"), "w", encoding="utf-8").write(txt)
json.dump(spec, open(os.path.join(out, "spec.json"), "w"), indent=1)
print(f"{out}: " + "; ".join(log))
