"""Corridors of the Iberian equivalent from OSM 400 kV geometry -- v2 of build_corridors.py (2026-11-25).

usage: python iberia_eq/build_corridors_v2.py [--jtol 0.3] [--gap 2.0]
Same inputs, substation snapping and zone rule as build_corridors.py. What changes (RUNLOG S28):
  1. Junction endpoints closer than --jtol km are merged (v1 rounded to 0.001 deg, so two ends 50 m apart could stay
     separate and the chain was dropped as "dangling").
  2. A dead-end junction (degree 1) is bridged to the nearest other node within --gap km (OSM mapping gaps).
  3. No chain walk. Each connected group of junction nodes is a "cluster"; the substations attached to it are its
     terminals. 2 terminals -> one line; k > 2 -> the minimum spanning tree of the terminal-to-terminal shortest paths
     (k - 1 lines; a T-junction becomes two lines).
  4. Circuits of a line = max-flow between its two terminals inside the cluster, capacity = circuits per way.
     v1 took the minimum along ONE path, so a double circuit mapped as two separate ways was counted once.
Outputs: corridors_v2.csv, zone_km_v2.csv (same columns as v1), and a diff against corridors.csv on stdout.
"""
import argparse, collections, csv, json, math, os
import networkx as nx

ap = argparse.ArgumentParser()
ap.add_argument("--jtol", type=float, default=0.3); ap.add_argument("--gap", type=float, default=2.0)
ap.add_argument("--snap", type=float, default=1.5)
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); X = os.path.join(HERE, "ext")


def hav(p, q):
    la1, lo1, la2, lo2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


# ---- substations and zones: identical to v1 ----
subs = {}
for fn in ("osm_substations_400kV.json", "osm_substations_ree.json"):
    for e in json.load(open(os.path.join(X, fn), encoding="utf-8"))["elements"]:
        t = e.get("tags", {}); c = e.get("center", e)
        if "400000" not in t.get("voltage", ""): continue
        subs[f"{e['type']}/{e['id']}"] = dict(name=t.get("name", "?"), op=t.get("operator", ""), p=(c["lat"], c["lon"]))
fig = [r for r in csv.DictReader(open(os.path.join(HERE, "substations.csv"), encoding="utf-8")) if r["lat"]]
for r in fig: r["p"] = (float(r["lat"]), float(r["lon"]))


def zone_of(s):
    nm = s["name"]
    if "REN" in s["op"] or nm.startswith(("Subestação", "Posto de Corte", "Subestaçao")) or "ção" in nm: return "PT"
    if "RTE" in s["op"]: return "FR"
    return min(fig, key=lambda r: hav(s["p"], r["p"]))["zone"]


for s in subs.values(): s["zone"] = zone_of(s)
SL = list(subs.items())


def snap(p):
    k, s = min(SL, key=lambda kv: hav(p, kv[1]["p"]))
    return k if hav(p, s["p"]) <= a.snap else None


# ---- segments: identical filter to v1 ----
segs = []
for w in json.load(open(os.path.join(X, "osm_lines_400kV.json"), encoding="utf-8"))["elements"]:
    g = w.get("geometry"); t = w["tags"]
    if not g or len(g) < 2: continue
    if t.get("operator", "").startswith("RTE") and "REE" not in t.get("operator", "") and "Red El" not in t.get("operator", ""):
        if min(p["lat"] for p in g) > 42.6: continue
    L = sum(hav((g[i]["lat"], g[i]["lon"]), (g[i + 1]["lat"], g[i + 1]["lon"])) for i in range(len(g) - 1))
    try: nc = int(t["circuits"])
    except Exception:
        try: nc = max(1, int(t.get("cables", "3")) // 3)
        except Exception: nc = 1
    segs.append(dict(id=w["id"], a=(g[0]["lat"], g[0]["lon"]), b=(g[-1]["lat"], g[-1]["lon"]), L=L, nc=nc, name=t.get("name", "")))

# ---- nodes: substation, France, or a merged junction ----
jpts = []                                                    # junction points, merged by union-find within jtol
par = []


def find(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i


grid = collections.defaultdict(list); CELL = 0.01          # ~1 km cells


def jid(p):
    i = len(jpts); jpts.append(p); par.append(i)
    cx, cy = int(p[0] / CELL), int(p[1] / CELL)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for j in grid[(cx + dx, cy + dy)]:
                if hav(p, jpts[j]) <= a.jtol: par[find(i)] = find(j)
    grid[(cx, cy)].append(i)
    return i


ends = []
for s in segs:
    e = []
    for p in (s["a"], s["b"]):
        k = snap(p)
        if k: e.append(("S", k))
        elif p[0] > 42.6 and p[1] > -2.0: e.append(("S", "FR"))
        else: e.append(("J", jid(p)))
    ends.append(e)
node = lambda e: e[1] if e[0] == "S" else f"J{find(e[1])}"
G = nx.MultiGraph()
for i, (s, e) in enumerate(zip(segs, ends)):
    G.add_edge(node(e[0]), node(e[1]), L=s["L"], nc=s["nc"], seg=i)
pos = {f"J{find(i)}": jpts[i] for i in range(len(jpts))}
pos.update({k: s["p"] for k, s in subs.items()})
# ---- bridge dead-end junctions (OSM gaps) ----
bridged = 0
dead = [n for n in G if n.startswith("J") and G.degree(n) == 1]
for n in dead:
    nb = next(iter(G[n]))
    cand = [(hav(pos[n], pos[m]), m) for m in pos if m != n and m != nb and m in G and hav(pos[n], pos[m]) <= a.gap]
    if cand:
        d, m = min(cand); G.add_edge(n, m, L=d, nc=99, seg=-1); bridged += 1
is_t = lambda n: not n.startswith("J")
# ---- clusters of junctions -> lines between terminals ----
lines = []
direct = [(u, v, d) for u, v, d in G.edges(data=True) if is_t(u) and is_t(v) and u != v]
for u, v, d in direct:
    lines.append(dict(a=u, b=v, L=d["L"], nc=d["nc"], names=segs[d["seg"]]["name"] if d["seg"] >= 0 else ""))
J = G.subgraph([n for n in G if not is_t(n)])
n_dang = 0
for comp in nx.connected_components(J):
    terms = sorted({m for n in comp for m in G[n] if is_t(m)})
    if len(terms) < 2: n_dang += len(terms) == 1; continue
    H = nx.Graph()                                          # simple graph: parallel ways add circuits, shortest L kept
    for u, v, d in G.subgraph(list(comp) + terms).edges(data=True):
        if is_t(u) and is_t(v): continue                     # direct lines handled above
        if H.has_edge(u, v): H[u][v]["nc"] += d["nc"]; H[u][v]["L"] = min(H[u][v]["L"], d["L"])
        else: H.add_edge(u, v, L=d["L"], nc=d["nc"], names={segs[d["seg"]]["name"]} if d["seg"] >= 0 else set())
    # paths between two terminals may not pass through a third terminal (that would be two lines, not one)
    T = nx.Graph(); jn = [n for n in H if not is_t(n)]
    for i, s in enumerate(terms):
        for t in terms[i + 1:]:
            try: T.add_edge(s, t, L=nx.dijkstra_path_length(H.subgraph(jn + [s, t]), s, t, weight="L"))
            except nx.NetworkXNoPath: pass
    for s, t, d in nx.minimum_spanning_edges(T, weight="L", data=True):
        Hp = H.subgraph([n for n in H if not is_t(n) or n in (s, t)])
        try: fl = nx.maximum_flow_value(Hp.to_directed(), s, t, capacity="nc")
        except nx.NetworkXError: continue
        lines.append(dict(a=s, b=t, L=d["L"], nc=min(int(fl), 8), names=""))
zn = lambda n: "FR" if n == "FR" else subs[n]["zone"]
nm = lambda n: "FR" if n == "FR" else subs[n]["name"]
cor = collections.defaultdict(list); zkm = collections.Counter(); zroute = collections.Counter()
for l in lines:
    za, zb = zn(l["a"]), zn(l["b"])
    if za == zb: zkm[za] += l["L"] * l["nc"]; zroute[za] += l["L"]
    else:
        k = tuple(sorted((za, zb))); cor[k].append(l)
        for z in k: zkm[z] += l["L"] * l["nc"] / 2
with open(os.path.join(HERE, "corridors_v2.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["zone_a", "zone_b", "sub_a", "sub_b", "route_km", "circuits", "osm_names"])
    for k in sorted(cor):
        for l in sorted(cor[k], key=lambda l: -l["L"]):
            x, y = (l["a"], l["b"]) if zn(l["a"]) == k[0] else (l["b"], l["a"])
            w.writerow([k[0], k[1], nm(x), nm(y), f"{l['L']:.1f}", l["nc"], l["names"]])
with open(os.path.join(HERE, "zone_km_v2.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["zone", "circuit_km_incl_half_ties", "route_km_internal"])
    for z in sorted(zkm): w.writerow([z, f"{zkm[z]:.0f}", f"{zroute[z]:.0f}"])
print(f"segments {len(segs)}, junction nodes {len(set(find(i) for i in range(len(jpts))))}, bridged gaps {bridged}, "
      f"dangling clusters {n_dang}, lines {len(lines)}")
old = collections.defaultdict(lambda: [0, 0.0])
for r in csv.DictReader(open(os.path.join(HERE, "corridors.csv"), encoding="utf-8")):
    o = old[(r["zone_a"], r["zone_b"])]; o[0] += int(r["circuits"]); o[1] += float(r["route_km"]) * int(r["circuits"])
print("corridor        v1 circ  v1 km |  v2 circ  v2 km   main v2 paths")
for k in sorted(set(cor) | set(old)):
    ls = cor.get(k, []); c2 = sum(l["nc"] for l in ls); km2 = sum(l["L"] * l["nc"] for l in ls) / max(c2, 1)
    c1, km1 = old[k][0], old[k][1] / max(old[k][0], 1)
    flag = "  <-- NEW" if c1 == 0 else ("  <-- gone" if c2 == 0 else ("  *" if c1 != c2 else ""))
    print(f"{k[0]:>4s}-{k[1]:<5s}  {c1:6d} {km1:6.0f} | {c2:7d} {km2:6.0f}   " +
          "; ".join(f"{nm(l['a'])[:16]}~{nm(l['b'])[:16]} {l['L']:.0f}x{l['nc']}" for l in sorted(ls, key=lambda l: -l["nc"])[:3]) + flag)
tot = lambda d: sum(v for z, v in d.items() if z not in ("PT", "FR"))
print("Spain circuit-km: v1", sum(int(r['circuit_km_incl_half_ties']) for r in csv.DictReader(open(os.path.join(HERE, 'zone_km.csv'))) if r['zone'] not in ('PT', 'FR')),
      " v2", round(tot(zkm)))
