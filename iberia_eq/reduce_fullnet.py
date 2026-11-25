"""Zonal reduction of the full OSM 400 kV network: one equivalent reactance per corridor of the 22-bus model.

usage: python iberia_eq/reduce_fullnet.py [--open] [--weights equal|degree]

Why (RUNLOG S29 sec 7-8): with corridor reactances from centroid distance x route factor, two Fig 2-4 corridor flows
(GRA->SE, CAC->CYL) could not be met by any dispatch shift: they are set by the equivalent's impedances. This script
derives the impedances from the physical network instead.

Method (DC, series reactance only; line charging is handled separately in pp_v2 by CHG=phys):
 1. Full network = lines_full_v2.csv (build_corridors_v2.py), main connected component. x = 0.253 ohm/km per circuit
    ([EXT-3]), X_line = x * km / circuits. Portuguese substations are split PT-N / PT-S at 39.9 N [inf]. The French
    border node is dropped (all French ends snap to one node, which would short Argia to Baixas; France keeps its own
    hub-to-hub ties in pp_v2). --open removes the Table 2-12 lines still open at 12:32.
 2. Zonal PTDF and zone-to-reference transfer reactance (w'B+w: angle per unit transfer; it fixes the absolute scale,
    which the PTDF alone cannot) of the full network: a transfer from zone i to the reference zone is injected spread over the zone's
    substations (equal shares, or by node degree), and the flows on the inter-zone lines are summed per zone pair.
 3. The reduced network (one bus per zone, branches only on pp_v2's corridor set) has its own zonal PTDF; its branch
    susceptances are fitted (log-space least squares) to reproduce the full network's.
Output: corridor_x_fit[_open].csv (zone_a, zone_b, x_fit_ohm, x_hub_ohm for comparison) and the PTDF fit quality.
"""
import argparse, csv, math, os, collections
import numpy as np, networkx as nx
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--open", action="store_true", help="remove the Table 2-12 lines open at 12:32")
ap.add_argument("--weights", default="equal", choices=["equal", "degree"])
ap.add_argument("--ref", default="MAD")
a = ap.parse_args()
X_KM = 0.253
OPEN = [("Pierola", "Sentmenat"), ("Cofrentes", "Muela"), ("Fuendetodos", "Mezquita"), ("Mezquita", "Morella")]

L = list(csv.DictReader(open(os.path.join(HERE, "lines_full_v2.csv"), encoding="utf-8")))
zone = {}
for r in L:
    for e in "ab":
        z = r[f"zone_{e}"]
        if z == "PT": z = "PT-N" if float(r[f"lat_{e}"]) >= 39.9 else "PT-S"
        zone[r[e]] = z
removed = []
G = nx.MultiGraph()
for r in L:
    if "FR" in (zone[r["a"]], zone[r["b"]]) or r["a"] == r["b"]: continue
    if a.open and any((p in r["name_a"] and q in r["name_b"]) or (q in r["name_a"] and p in r["name_b"]) for p, q in OPEN):
        removed.append(f"{r['name_a']} - {r['name_b']} ({float(r['km']):.0f} km x{r['circuits']})"); continue
    G.add_edge(r["a"], r["b"], x=X_KM * float(r["km"]) / max(int(r["circuits"]), 1))
main = max(nx.connected_components(G), key=len); G = G.subgraph(main).copy()
nodes = sorted(G); ix = {n: i for i, n in enumerate(nodes)}; N = len(nodes)
print(f"full network: {N} substations, {G.number_of_edges()} lines (main component, France dropped)")
if a.open: print("removed (Table 2-12):", "; ".join(removed) if removed else "none matched")
missing = [f"{p}-{q}" for p, q in OPEN if not any((p in s and q in t) or (q in s and p in t) for s, t in ((r["name_a"], r["name_b"]) for r in L))]
if missing: print("NOT in the OSM line list (cannot be removed):", ", ".join(missing))

# ---- full DC network ----
E = [(ix[u], ix[v], d["x"]) for u, v, d in G.edges(data=True)]
Bm = np.zeros((N, N))
for i, j, x in E: Bm[i, i] += 1 / x; Bm[j, j] += 1 / x; Bm[i, j] -= 1 / x; Bm[j, i] -= 1 / x
Bg = Bm[1:, 1:]; Binv = np.linalg.inv(Bg)                 # node 0 grounded (injections sum to zero)
ZONES = sorted({zone[n] for n in nodes}); nz = len(ZONES); zi = {z: k for k, z in enumerate(ZONES)}
w = np.zeros((nz, N))
for n in nodes:
    w[zi[zone[n]], ix[n]] = G.degree(n) if a.weights == "degree" else 1.0
w /= w.sum(axis=1, keepdims=True)
# pp_v2 corridor set: corridors_v2 pairs with the S27 PT mapping, plus the Portuguese internal corridor
PTMAP = {"NW": "PT-N", "CYL": "PT-N", "CAC": "PT-N", "BAD": "PT-S", "WAN": "PT-S"}
PAIRS = set()
for r in csv.DictReader(open(os.path.join(HERE, "corridors_v2.csv"), encoding="utf-8")):
    za, zb = r["zone_a"], r["zone_b"]
    if "FR" in (za, zb): continue
    if "PT" in (za, zb): z = zb if za == "PT" else za; za, zb = z, PTMAP[z]
    PAIRS.add(tuple(sorted((za, zb))))
PAIRS.add(("PT-N", "PT-S"))
PAIRS.add(("CAC", "PT-S"))   # Cedillo-Falagueira (Caceres - central Portugal); [CA] p.33; S27's PTMAP sent all CAC ties to PT-N
PAIRS = sorted(p for p in PAIRS if p[0] in zi and p[1] in zi)
iso = [z for z in ZONES if not any(z in p for p in PAIRS)]
print("zones:", ZONES, "| corridors:", len(PAIRS), "| zones without a corridor:", iso or "none")
pk = {p: k for k, p in enumerate(PAIRS)}
ref = zi[a.ref]; others = [k for k in range(nz) if k != ref]


def full_ptdf():
    F = np.zeros((len(PAIRS), len(others))); unmapped = collections.Counter()
    for c, k in enumerate(others):
        P = w[k] - w[ref]; th = np.zeros(N); th[1:] = Binv @ P[1:]
        for i, j, x in E:
            za, zb = zone[nodes[i]], zone[nodes[j]]
            if za == zb: continue
            f = (th[i] - th[j]) / x
            p = tuple(sorted((za, zb))); s = 1 if (za, zb) == p else -1
            if p in pk: F[pk[p], c] += s * f
            else: unmapped[p] += abs(f)
    return F, unmapped


def red_ptdf(b):
    Br = np.zeros((nz, nz))
    for (za, zb), bb in zip(PAIRS, b):
        i, j = zi[za], zi[zb]; Br[i, i] += bb; Br[j, j] += bb; Br[i, j] -= bb; Br[j, i] -= bb
    keep = [k for k in range(nz) if k != ref]; Bi = np.linalg.pinv(Br[np.ix_(keep, keep)])
    F = np.zeros((len(PAIRS), len(others)))
    for c, k in enumerate(others):
        P = np.zeros(nz); P[k] = 1; P[ref] = -1; th = np.zeros(nz); th[keep] = Bi @ P[keep]
        for (za, zb), bb, r_ in zip(PAIRS, b, range(len(PAIRS))): F[r_, c] = (th[zi[za]] - th[zi[zb]]) * bb
    return F


Ff, unm = full_ptdf()
Xf = np.zeros(len(others))                                  # full-network transfer reactance zone k -> ref (ohm)
for c, k in enumerate(others):
    P = w[k] - w[ref]; th = np.zeros(N); th[1:] = Binv @ P[1:]; Xf[c] = P @ th


def red_xt(b):
    Br = np.zeros((nz, nz))
    for (za, zb), bb in zip(PAIRS, b):
        i, j = zi[za], zi[zb]; Br[i, i] += bb; Br[j, j] += bb; Br[i, j] -= bb; Br[j, i] -= bb
    keep = [k for k in range(nz) if k != ref]; Bi = np.linalg.pinv(Br[np.ix_(keep, keep)])
    return np.array([Bi[keep.index(k), keep.index(k)] for k in others])
if unm: print("full-network inter-zone flows on pairs NOT in pp_v2's corridor set (|PTDF| summed):",
              ", ".join(f"{p[0]}-{p[1]} {v:.2f}" for p, v in unm.most_common()))
# start: the physical boundary-line susceptance of each pair
b0 = np.full(len(PAIRS), 1e-3)
for i, j, x in E:
    p = tuple(sorted((zone[nodes[i]], zone[nodes[j]])))
    if p in pk: b0[pk[p]] += 1 / x
# bounded, with a weak pull (0.01 per e-fold) toward the physical boundary-line susceptance: corridors that the PTDF
# cannot identify (radial in the zonal graph) stay physical instead of drifting
lb0 = np.log(b0)
res_ = lambda lb: np.concatenate([(red_ptdf(np.exp(lb)) - Ff).ravel(), np.log(red_xt(np.exp(lb)) / Xf),   # flow split + transfer reactance
                                  0.01 * (lb - lb0)])
sol = least_squares(res_, lb0, bounds=(lb0 - 4, lb0 + 4), method="trf", max_nfev=5000)
b = np.exp(sol.x); Fr = red_ptdf(b)
print(f"PTDF fit: rms error {np.sqrt(np.mean((Fr - Ff) ** 2)):.3f}, max {np.abs(Fr - Ff).max():.3f} (per unit transfer)")
Xr = red_xt(b)
print("transfer reactance to " + a.ref + " (ohm, full / reduced): " + "  ".join(f"{ZONES[k]} {xf:.1f}/{xr:.1f}" for k, xf, xr in zip(others, Xf, Xr)))

# ---- compare with the hub-to-hub reactance pp_v2 uses (route 1.0 x centroid km, mincirc 2, PT_TIE_SW 2.6) ----
subs = list(csv.DictReader(open(os.path.join(HERE, "substations.csv"), encoding="utf-8")))
CEN = {z: (np.mean([float(r["lat"]) for r in subs if r["zone"] == z and r["lat"]]), np.mean([float(r["lon"]) for r in subs if r["zone"] == z and r["lat"]]))
       for z in {r["zone"] for r in subs if r["lat"]}}
CEN.update({"PT-N": (41.2, -8.4), "PT-S": (38.6, -8.9)})
def gc(p, q):
    la1, lo1, la2, lo2 = map(math.radians, (*p, *q))
    return 2 * 6371 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
nc_v2 = collections.Counter()
for r in csv.DictReader(open(os.path.join(HERE, "corridors_v2.csv"), encoding="utf-8")):
    za, zb = r["zone_a"], r["zone_b"]
    if "FR" in (za, zb): continue
    if "PT" in (za, zb): z = zb if za == "PT" else za; za, zb = z, PTMAP[z]
    nc_v2[tuple(sorted((za, zb)))] += int(r["circuits"])
out = os.path.join(HERE, f"corridor_x_fit{'_open' if a.open else ''}.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f); wr.writerow(["zone_a", "zone_b", "x_fit_ohm", "x_hub_ohm", "ratio"])
    print(f"{'corridor':12s} {'X fit':>8s} {'X hub':>8s} {'fit/hub':>8s}   (ohm; hub = pp_v2 base: 1.0 x centroid km, >=2 circuits, PT SW ties x2.6)")
    for p, bb in zip(PAIRS, b):
        nc = max(nc_v2.get(p, 3 if p == ("PT-N", "PT-S") else 1), 2)
        km = 250.0 if p == ("PT-N", "PT-S") else gc(CEN[p[0]], CEN[p[1]]) * (2.6 if ("PT" in p[0] + p[1] and set(p) & {"CAC", "BAD", "WAN"}) else 1.0)
        xh = X_KM * km / nc
        wr.writerow([p[0], p[1], f"{1 / bb:.2f}", f"{xh:.2f}", f"{(1 / bb) / xh:.2f}"])
        print(f"{p[0]:>4s}-{p[1]:<6s} {1 / bb:8.1f} {xh:8.1f} {(1 / bb) / xh:8.2f}")
print("written", os.path.basename(out))
