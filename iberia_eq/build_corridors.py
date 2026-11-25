"""Corridors of the Iberian equivalent from OpenStreetMap 400 kV line geometry.

usage: python iberia_eq/build_corridors.py
Inputs (fetched 2026-11-23, (c) OpenStreetMap contributors, ODbL):
  ext/osm_lines_400kV.json        Overpass: way[power~line|cable][voltage~400000], bbox 35.9,-9.6,43.9,3.4, out geom
  ext/osm_substations_400kV.json  Overpass: 400 kV substations, ES + PT
  ext/osm_substations_ree.json    Overpass: Red Electrica substations, ES
  substations.csv                 Fig 2-4 substations with zone (build_substations.py)
Method:
  1. Every OSM way is a segment, with length from its geometry (haversine) and its circuit count: the `circuits` tag,
     else cables/3, else 1.
  2. Each segment endpoint is snapped to the nearest 400 kV substation within 1.5 km. Endpoints that don't snap
     are junctions (split ways).
  3. Chains of segments through junctions are merged into lines between two substations. The length is the sum along
     the chain; the circuit count is the minimum along it.
  4. Substation -> zone: the zone of the nearest Fig 2-4 substation (substations.csv). Portugal = operator REN or a
     Portuguese name; France = north of the Pyrenees with no Iberian substation (lat > 42.6, lon > -2.0 and not
     snapped) or operator RTE.
Outputs: corridors.csv (inter-zone lines), zone_km.csv (circuit-km inside each zone, for line charging).
Limits: OSM is volunteer-mapped. Missing tags default to 1 circuit, and mixed-voltage ways (400;220 kV) count as 400 kV.
Cross-check against Fig 2-4 ([FR] p.37) before use.
"""
import csv, json, math, os, collections

HERE = os.path.dirname(os.path.abspath(__file__)); X = os.path.join(HERE, "ext")


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


# substations
subs = {}
for fn in ("osm_substations_400kV.json", "osm_substations_ree.json"):
    for e in json.load(open(os.path.join(X, fn), encoding="utf-8"))["elements"]:
        t = e.get("tags", {}); c = e.get("center", e)
        if "400000" not in t.get("voltage", ""): continue
        subs[f"{e['type']}/{e['id']}"] = dict(name=t.get("name", "?"), op=t.get("operator", ""), lat=c["lat"], lon=c["lon"])
fig = [r for r in csv.DictReader(open(os.path.join(HERE, "substations.csv"), encoding="utf-8")) if r["lat"]]
for r in fig: r["p"] = (float(r["lat"]), float(r["lon"]))


def zone_of(s):
    nm = s["name"]
    if "REN" in s["op"] or nm.startswith(("Subestação", "Posto de Corte", "Subestaçao")) or "ção" in nm: return "PT"
    if "RTE" in s["op"]: return "FR"
    p = (s["lat"], s["lon"]); r = min(fig, key=lambda r: hav(p, r["p"]))
    return r["zone"] if r["zone"] != "PT" else "PT"


for s in subs.values(): s["zone"] = zone_of(s)
SL = list(subs.items())


def snap(p, tol=1.5):
    best = min(SL, key=lambda kv: hav(p, (kv[1]["lat"], kv[1]["lon"])))
    return best[0] if hav(p, (best[1]["lat"], best[1]["lon"])) <= tol else None


# segments
ways = json.load(open(os.path.join(X, "osm_lines_400kV.json"), encoding="utf-8"))["elements"]
segs = []
for w in ways:
    g = w.get("geometry"); t = w["tags"]
    if not g or len(g) < 2: continue
    if t.get("operator", "").startswith("RTE") and "REE" not in t.get("operator", "") and "Red El" not in t.get("operator", ""):
        if min(p["lat"] for p in g) > 42.6: continue          # purely French lines
    L = sum(hav((g[i]["lat"], g[i]["lon"]), (g[i + 1]["lat"], g[i + 1]["lon"])) for i in range(len(g) - 1))
    try: nc = int(t["circuits"])
    except Exception:
        try: nc = max(1, int(t.get("cables", "3")) // 3)
        except Exception: nc = 1
    segs.append(dict(id=w["id"], a=(g[0]["lat"], g[0]["lon"]), b=(g[-1]["lat"], g[-1]["lon"]), L=L, nc=nc,
                     name=t.get("name", ""), cable=t["power"] == "cable"))

# node ids: substation id, or rounded junction coordinate
def nid(p):
    s = snap(p)
    if s: return s
    if p[0] > 42.6 and p[1] > -2.0: return "FR"
    return f"J{round(p[0], 3)},{round(p[1], 3)}"


adj = collections.defaultdict(list)
for i, s in enumerate(segs):
    s["na"], s["nb"] = nid(s["a"]), nid(s["b"])
    adj[s["na"]].append(i); adj[s["nb"]].append(i)
is_term = lambda n: not n.startswith("J")
# walk chains from every terminal
lines = []; used = set()
for start in [n for n in adj if is_term(n)]:
    for i0 in adj[start]:
        if i0 in used: continue
        L = 0.0; nc = 99; names = set(); cur = start; i = i0; ok = True; path = []
        while True:
            s = segs[i]; used.add(i); path.append(i); L += s["L"]; nc = min(nc, s["nc"]); names.add(s["name"])
            nxt = s["nb"] if s["na"] == cur else s["na"]
            if is_term(nxt): break
            nb = [j for j in adj[nxt] if j not in used]
            if not nb: ok = False; break             # dangling junction (gap in OSM)
            if len(nb) > 1:                          # T-junction: follow the first, the others start new walks
                pass
            cur, i = nxt, nb[0]
        lines.append(dict(a=start, b=nxt, L=L, nc=nc, ok=ok, names=";".join(sorted(n for n in names if n))[:120]))

zn = lambda n: "FR" if n == "FR" else (subs[n]["zone"] if n in subs else "?")
nm = lambda n: "FR" if n == "FR" else (subs[n]["name"] if n in subs else n)
cor = collections.defaultdict(list); zkm = collections.Counter(); zroute = collections.Counter(); dangling = 0
for l in lines:
    if not l["ok"]: dangling += 1; continue
    za, zb = zn(l["a"]), zn(l["b"])
    if za == zb: zkm[za] += l["L"] * l["nc"]; zroute[za] += l["L"]
    else:
        k = tuple(sorted((za, zb))); cor[k].append(l)
        for z in k: zkm[z] += l["L"] * l["nc"] / 2               # half of a tie's charging to each end
with open(os.path.join(HERE, "corridors.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["zone_a", "zone_b", "sub_a", "sub_b", "route_km", "circuits", "osm_names"])
    for k in sorted(cor):
        for l in sorted(cor[k], key=lambda l: -l["L"]):
            a, b = (l["a"], l["b"]) if zn(l["a"]) == k[0] else (l["b"], l["a"])
            w.writerow([k[0], k[1], nm(a), nm(b), f"{l['L']:.1f}", l["nc"], l["names"]])
with open(os.path.join(HERE, "zone_km.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["zone", "circuit_km_incl_half_ties", "route_km_internal"])
    for z in sorted(zkm): w.writerow([z, f"{zkm[z]:.0f}", f"{zroute[z]:.0f}"])
print(f"segments {len(segs)}, lines {len(lines)}, dangling (OSM gaps) {dangling}")
for k in sorted(cor):
    ls = cor[k]
    print(f"{k[0]:>4s}-{k[1]:<4s} lines {len(ls):2d}  circuits {sum(l['nc'] for l in ls):2d}  "
          f"mean km {sum(l['L'] for l in ls)/len(ls):6.1f}  " +
          "; ".join(f"{nm(l['a'])[:18]}~{nm(l['b'])[:18]} {l['L']:.0f}km x{l['nc']}" for l in sorted(ls, key=lambda l: -l['nc'])[:3]))
print("circuit-km per zone:", dict(sorted((z, round(v)) for z, v in zkm.items())))
