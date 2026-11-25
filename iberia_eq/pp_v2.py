"""Iberian equivalent v2 — pandapower model, FIRST PASS (uncalibrated). Design: V2_BUS_UNIT_LIST.md (Draft 3).

usage: python iberia_eq/pp_v2.py [--q0 0.2] [--vset 1.02] [--kpf -0.175]

Every inferred number is marked [inf] in the tables below; sources are in SOURCES.md.

Data path rules learned in S27 (RUNLOG §22–28):
- transformer taps and magnetising current explicit;
- start from a reasonable initial guess;
- exponential loads (alpha 0.8, beta 4.1) solved by an outer fixed-point loop (pandapower has ZIP loads only).

Calibration is NOT done here. This pass prints the gaps to the targets:
- Fig 2-4 voltages;
- Fig 2-22 border flows;
- Madrid in-feed;
- Table 4-26 fault levels (a later pass).
"""
import argparse, csv, os, numpy as np, pandapower as pp

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--q0", type=float, default=0.20, help="load Q0/P0 at 1 pu [inf placeholder]")
ap.add_argument("--vset", type=float, default=1.02, help="generator AVR set-point pu [inf placeholder]")
ap.add_argument("--kpf", type=float, default=-0.135, help="RES Q/P, absorbing: Fig 4-2 South Spain 2,297 Mvar / 17,020 MW (>5 MW RES) at 12:32:00")
ap.add_argument("--alpha", type=float, default=0.8); ap.add_argument("--beta", type=float, default=4.1)
ap.add_argument("--xk", type=float, default=1.0, help="corridor reactance scale (fault-level calibration)")
ap.add_argument("--frsc", type=float, default=15000, help="France border fault level MVA [inf]")
ap.add_argument("--quick", action="store_true", help="skip the calibration loop (fault levels only)")
ap.add_argument("--kres", type=float, default=1.2, help="inverter fault current, x rated [inf]")
ap.add_argument("--flowcal", action="store_true", help="calibrate the Fig 2-4 corridor flows")
ap.add_argument("--mincirc", type=int, default=1, help="minimum equivalent circuits per inter-zone corridor [inf]")
ap.add_argument("--route", type=float, default=1.2, help="hub-to-hub routing factor on centroid distance [inf]")
ap.add_argument("--tsx", default="BAD:14,WAN:6.8", help="zone:ohm reactance hub -> 400 kV TS bus (Table 4-26 calibration)")
ap.add_argument("--vkg", type=float, default=15.0, help="unit connection reactance %% on rating: step-up + zone-internal network")
a = ap.parse_args()

ES = ["GRA", "WAN", "BAD", "CAC", "SCE", "MAD", "CYL", "NW", "N", "ARA", "CAT", "VAL", "SE"]
BUSES = ES + ["PS-CYL", "PS-ARA", "PS-PT", "PT-N", "PT-S", "FR", "MA-B", "MA"]   # MA-B: Moroccan end of the Strait cables
TSX = {kv.split(":")[0]: float(kv.split(":")[1]) for kv in a.tsx.split(",") if kv}   # 400 kV substation buses of the event zones
BUSES += [f"{z}-TS" for z in TSX]
VB = lambda z: f"{z}-TS" if z in TSX else z                 # where a zone's Fig 2-4 voltage is measured
# MW of the Table 3-3 tripping plants per TS bus: BAD 4a 582 + 4b 145 + 5b1 118 + TS3 (5b4 72, 6a2 20, 6a3 16) 108;
# WAN 5a2 550 + Cadiz 6a6/6a7 153 ([FR] p.144-145)
TS_RES = {"BAD": 953.0, "WAN": 703.0}

# ---- Fig 2-41 area totals at 12:32 (exact, [FR] p.61) ----
AREA = {"N": dict(demand=9030, pv=2420, wind=710), "SW": dict(demand=8260, pv=12860, wind=2810),
        "E": dict(demand=7950, pv=1260, wind=110)}
# region -> area: chosen so that the regional PV shares reproduce Fig 2-41 PV per area (see the note in the RUNLOG)
REG_AREA = {"Andalucia": "SW", "Extremadura": "SW", "Castilla-La Mancha": "SW", "Madrid": "SW",
            "Cataluna": "E", "C. Valenciana": "E", "Murcia": "E",
            "Galicia": "N", "Asturias": "N", "Cantabria": "N", "Pais Vasco": "N", "Navarra": "N", "La Rioja": "N",
            "Castilla y Leon": "N", "Aragon": "N"}
# region -> zone shares [inf: provinces]
REG_ZONE = {"Andalucia": {"WAN": .45, "GRA": .30, "SCE": .15, "SE": .10},       # Sev/Hue/Cad | Gra/Mal/Jae | Cor | Alm
            "Extremadura": {"BAD": .60, "CAC": .40},
            "Castilla-La Mancha": {"SCE": .50, "MAD": .10, "VAL": .40},          # CR | To/Gu | Cu/Ab [inf, cal pass 1]
            "Madrid": {"MAD": 1}, "Castilla y Leon": {"CYL": .75, "NW": .25},    # Leon -> NW
            "Galicia": {"NW": 1}, "Asturias": {"NW": 1}, "Cantabria": {"N": 1}, "Pais Vasco": {"N": 1},
            "Navarra": {"N": 1}, "La Rioja": {"N": 1}, "Aragon": {"ARA": 1}, "Cataluna": {"CAT": 1},
            "C. Valenciana": {"VAL": .65, "SE": .35}, "Murcia": {"SE": 1}}
reg = {r["region"]: r for r in csv.DictReader(open(os.path.join(HERE, "regional_april2025_MWh.csv"), encoding="utf-8"))}


def zone_split(key, area_key):
    """Area total (Fig 2-41) split over zones by regional April-2025 shares (REData) x province shares [inf]."""
    out = {z: 0.0 for z in ES}
    for A, tot in AREA.items():
        regs = [r for r, ar in REG_AREA.items() if ar == A]
        s = sum(float(reg[r][key] or 0) for r in regs)
        for r in regs:
            for z, f in REG_ZONE[r].items():
                out[z] += tot[area_key] * float(reg[r][key] or 0) / s * f
    return out


DEM = zone_split("demand", "demand"); PV = zone_split("pv", "pv"); WIND = zone_split("wind", "wind")

# ---- Fig 2-4 busbar voltages at 12:32 (kV, read +-2; SOURCES.md 5) -> zone targets [inf: zone mean of its substations]
VT = {"GRA": 412, "WAN": 413, "BAD": 412, "CAC": 406, "SCE": 417, "MAD": 405, "CYL": 405, "NW": 405, "N": 409,
      "ARA": 410, "CAT": 400, "VAL": 413, "SE": 408,
      "PT-N": 398, "PT-S": 401}   # Portugal: Fig 2-4 grey area (Lindoso 398 ...; Alqueva 406, Tavira 401, Sines 399) [read]
# ---- machines (P MW at 12:32) ----
GEN = [("G1 Almaraz II", "CAC", 660), ("G2 Cat nuclear A", "CAT", 1045), ("G3 Cat nuclear B", "CAT", 1692),
       ("G4 N thermal", "NW", 570), ("G5 N hydro", "CYL", 290), ("G6 SW CCGT", "GRA", 320), ("G7 E CCGT", "VAL", 330),
       ("G8 PT conventional", "PT-N", 600)]                      # Fig 2-41, [T3-1], CSN; G8 Fig 2-19 [read]
EMB = [("E1 N embedded", {"NW": .5, "N": .25, "CYL": .25}, 3040),  # [inf] spread
       ("E2 SW embedded", {"SCE": .5, "BAD": .3, "WAN": .2}, 2070), ("E3 E embedded", {"VAL": .5, "CAT": .5}, 1070)]
PUMPS = [("M1 Duero", "PS-CYL", 1049), ("M2 Ebro", "PS-ARA", 1017), ("M3-7 Portugal", "PS-PT", 2098)]
PUMP_LOADS = {"ARA": 234, "CAT": 102, "VAL": 211, "WAN": 75, "NW": 68, "N": 156}   # small stages + cluster 50
# area balance: Fig 2-41 counts 2,040 MW of Spanish pumping (N 860, E 1,180); the model has M1 + M2 + small = 2,912.
# The difference is taken out of the zone demand in proportion (open item: pumping discrepancy, RUNLOG).
pump_model = 1049 + 1017 + sum(PUMP_LOADS.values()); pump_fig = 2040
for z in ES: DEM[z] -= (pump_model - pump_fig) * DEM[z] / sum(DEM.values())

# ---- liberties (user OK 2026-11-25: totals faithful, distribution may move) [inf, RUNLOG S27 sec 32] ----
SHIFT = [("SE", "CAT", float(os.environ.get("SH_SE_CAT", 800))), ("ARA", "NW", float(os.environ.get("SH_ARA_NW", 600)))]
for zf, zt, mw in SHIFT:
    mw = min(mw, DEM[zf] - 100); DEM[zf] -= mw; DEM[zt] += mw
# ---- externals ----
PT_LOAD, PT_RES = 5600, {"PT-S": 0.6 * (1604 + 2104 + 761), "PT-N": 0.4 * (1604 + 2104 + 761)}  # Fig 2-16 / 2-19 [read]; split [inf]
MA_LOAD, MA_EXPORT_FROM_ES = 5000, 750       # [inf] / Fig 2-22
FR_T = float(os.environ.get("FR_T", 1360))   # ES->FR incl. HVDC: Fig 2-41 exact 1,360 at 12:32; [CA] p.104 range 1,500 (12:32:00) -> 450 (12:32:57)
HVDC_FR = 1000                                # [inf] schedule ES->FR on the HVDC; AC ties carry the rest
# connected reactors at 12:32, Mvar ([FR] Table 2-7 / 2-8)
REACT = {"SCE": 250, "MAD": 250, "VAL": 250, "ARA": 250, "N": 300, "CAT": 450, "PT-N": 220, "PT-S": 75}
# Fig 4-2 ([FR] p.216): 1,300 Mvar connected in "South Spain" (S + C + E) vs 750 in Table 2-7 ("main" reactors only).
# The missing 550 Mvar is placed where the calibration already absorbed (WAN +591, SE +201 Mvar DSO shunts) [inf]
if os.environ.get("REAC_FIG42", "1") == "1": REACT["WAN"] = 400; REACT["SE"] = 150

# ---- network ----
R_KM, X_KM, C_NF_KM = 0.03, 0.253, 11.0      # [EXT-3]; r [inf]
cor = list(csv.DictReader(open(os.path.join(HERE, "corridors.csv"), encoding="utf-8")))
PTMAP = {"NW": "PT-N", "CYL": "PT-N", "CAC": "PT-N", "BAD": "PT-S", "WAN": "PT-S"}
pairs = {}
for r in cor:
    za, zb = r["zone_a"], r["zone_b"]
    if "PT" in (za, zb):
        z = zb if za == "PT" else za; za, zb = z, PTMAP[z]
    k = tuple(sorted((za, zb))); km, nc = float(r["route_km"]), int(r["circuits"])
    p = pairs.setdefault(k, [0, 0.0]); p[0] += nc; p[1] += km * nc
EXTRA = {("WAN", "MA-B"): (2, 30.0, "cable"), ("MA-B", "MA"): (2, 200.0, "ohl"), ("PT-N", "PT-S"): (3, 250.0, "ohl")}
# [inf] Strait cables (2 x 30 km), then ~200 km of Moroccan 400 kV network to the Moroccan hub ("weak" link, [FR] p.~187);
# Portuguese internal north-south corridor
# Zonal equivalent: ties to Portugal need HUB-TO-HUB impedance, not the short border lines (5-47 km), otherwise the
# zone-average voltages (Spain 405-413 kV, Portugal 398-401 kV) drive Gvar across them (calibration pass 2b, RUNLOG).
# Length = 1.2 x great-circle distance between zone centroids (substations.csv); Portuguese hubs [inf]: Porto, Lisbon-Setubal.
import math
subs = list(csv.DictReader(open(os.path.join(HERE, "substations.csv"), encoding="utf-8")))
CEN = {z: (np.mean([float(r["lat"]) for r in subs if r["zone"] == z]), np.mean([float(r["lon"]) for r in subs if r["zone"] == z]))
       for z in ES}
CEN.update({"PT-N": (41.2, -8.4), "PT-S": (38.6, -8.9)})
if os.environ.get("FR_HUB", "1") == "1":   # [inf] French 400 kV hub behind BOTH ties (Toulouse area): without it the single France
    CEN["FR"] = (43.6, 1.44)               # bus shorts Argia to Baixas and the HVDC power loops back over Vic-Baixas (RUNLOG S27 sec 35)
def gc(p_, q_):
    la1, lo1, la2, lo2 = map(math.radians, (*p_, *q_))
    return 2 * 6371 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
HUB_ALL = os.environ.get("HUB_ALL", "1") == "1"            # pass 4: hub-to-hub for EVERY inter-zone corridor
OSM_KM = {k: v[1] / v[0] for k, v in pairs.items()}
print("corridor lengths (OSM border-line mean km -> hub-to-hub 1.2 x centroid km):")
for k in list(pairs):
    if any(z.startswith("PT") for z in k) or (HUB_ALL and all(z in CEN for z in k)):
        nc0 = pairs[k][0]; old_km = pairs[k][1] / nc0
        nc = max(nc0, a.mincirc)                            # [inf] equivalent circuits incl. parallel 220 kV paths / OSM gaps
        pairs[k] = [nc, nc * a.route * gc(CEN[k[0]], CEN[k[1]])]
        OSM_KM[k] = old_km
        print(f"   {k[0]:>4s}-{k[1]:<5s} x{nc0}->{nc}: {old_km:5.0f} -> {pairs[k][1] / nc:5.0f}")
zkm = {r["zone"]: float(r["circuit_km_incl_half_ties"]) for r in csv.DictReader(open(os.path.join(HERE, "zone_km.csv"), encoding="utf-8"))}
ties_ckm = {z: 0.0 for z in zkm}
for (za, zb), (nc, ckm) in pairs.items():
    for z in (za, zb):
        zz = "PT" if z.startswith("PT") else z
        if zz in ties_ckm: ties_ckm[zz] += ckm / 2
internal_ckm = {z: max(0.0, zkm[z] - ties_ckm.get(z, 0)) for z in zkm}

net = pp.create_empty_network(f_hz=50, sn_mva=100)
B = {b: pp.create_bus(net, vn_kv=400, name=b) for b in BUSES}
for (za, zb), (nc, ckm) in pairs.items():
    pp.create_line_from_parameters(net, B[za], B[zb], length_km=ckm / nc, r_ohm_per_km=R_KM, x_ohm_per_km=a.xk * X_KM,
                                   c_nf_per_km=C_NF_KM, max_i_ka=2.0, parallel=nc, name=f"{za}-{zb}")
for (za, zb), (nc, km, kind) in EXTRA.items():
    c = 230.0 if kind == "cable" else C_NF_KM; x = 0.12 if kind == "cable" else a.xk * X_KM      # [inf] 400 kV cable
    pp.create_line_from_parameters(net, B[za], B[zb], length_km=km, r_ohm_per_km=0.02, x_ohm_per_km=x,
                                   c_nf_per_km=c, max_i_ka=2.0, parallel=nc, name=f"{za}-{zb}")
for z, x in TSX.items():                                   # hub -> TS: equivalent 400 kV line, X calibrated to Table 4-26
    pp.create_line_from_parameters(net, B[z], B[f"{z}-TS"], length_km=x / X_KM, r_ohm_per_km=R_KM, x_ohm_per_km=X_KM,
                                   c_nf_per_km=C_NF_KM, max_i_ka=4.0, parallel=1, name=f"{z}-{z}TS")
for z, ckm in internal_ckm.items():                       # charging of lines inside each zone, as a shunt
    b_ = "PT-N" if z == "PT" else z
    if b_ in B: pp.create_shunt(net, B[b_], q_mvar=-2 * np.pi * 50 * C_NF_KM * 1e-9 * ckm * 400 ** 2, name=f"Cint {z}")
for z, q in REACT.items(): pp.create_shunt(net, B[z], q_mvar=q, name=f"Reac {z}")
for ps, z in (("PS-CYL", "CYL"), ("PS-ARA", "ARA"), ("PS-PT", "PT-N")):   # pump station transformers [inf] x 15 %
    pp.create_transformer_from_parameters(net, B[z], B[ps], sn_mva=2500, vn_hv_kv=400, vn_lv_kv=400, vk_percent=a.vkg * 15 / 15,
                                          vkr_percent=0.3, pfe_kw=0, i0_percent=0.5, name=f"T {ps}")
pp.create_ext_grid(net, B["FR"], vm_pu=1.0, name="France", s_sc_max_mva=a.frsc, rx_max=0.1)
PMAX = {"G1 Almaraz II": 1000, "G2 Cat nuclear A": 1100, "G3 Cat nuclear B": 1930, "G4 N thermal": 1450,
        "G5 N hydro": 1100, "G6 SW CCGT": 760, "G7 E CCGT": 820, "G8 PT conventional": 1500,
        "M1 Duero": 1200, "M2 Ebro": 1450, "M3-7 Portugal": 2300, "Morocco": 5000}   # online Pmax [inf from Fig 2-41 / CSN / Table 3-1]
GTERM = {}
for n, z, p in GEN:                                       # units behind their step-up transformers (15 % on rating) [inf]
    tb = pp.create_bus(net, vn_kv=400, name=f"{n} term"); GTERM[n] = tb
    pp.create_transformer_from_parameters(net, B[z], tb, sn_mva=PMAX[n] / 0.9, vn_hv_kv=400, vn_lv_kv=400, vk_percent=a.vkg,
                                          vkr_percent=0.3, pfe_kw=0, i0_percent=0.0, name=f"T {n}")
    pp.create_gen(net, tb, p_mw=p, vm_pu=(VT[z] / 400 if z in VT else a.vset), name=n)
for n, sp, p in EMB:
    for z, f in sp.items(): pp.create_sgen(net, B[z], p_mw=p * f, q_mvar=0, name=f"{n} {z}")
for n, z, p in PUMPS: pp.create_gen(net, B[z], p_mw=-p, vm_pu=VT.get({"PS-CYL": "CYL", "PS-ARA": "ARA"}.get(z, ""), 408) / 400, name=n)
mt = pp.create_bus(net, vn_kv=400, name="Morocco term")
pp.create_transformer_from_parameters(net, B["MA"], mt, sn_mva=PMAX["Morocco"] / 0.9, vn_hv_kv=400, vn_lv_kv=400, vk_percent=15,
                                      vkr_percent=0.3, pfe_kw=0, i0_percent=0.0, name="T Morocco")
pp.create_gen(net, mt, p_mw=MA_LOAD - MA_EXPORT_FROM_ES, vm_pu=1.0, name="Morocco")
RES = {z: PV[z] + WIND[z] for z in ES}
for z in ES:
    if RES[z] > 0:
        pts = min(TS_RES.get(z, 0), RES[z])               # the report's tripping plants sit at the zone's TS bus (Table 3-3)
        pp.create_sgen(net, B[z], p_mw=RES[z] - pts, q_mvar=a.kpf * (RES[z] - pts), name=f"RES {z}")
        if pts > 0: pp.create_sgen(net, B[f"{z}-TS"], p_mw=pts, q_mvar=a.kpf * pts, name=f"RESTS {z}")
for z, p in PT_RES.items(): pp.create_sgen(net, B[z], p_mw=p, q_mvar=a.kpf * p, name=f"RES {z}")
L = {}
for z in ES: L[z] = pp.create_load(net, B[z], p_mw=DEM[z], q_mvar=a.q0 * DEM[z], name=f"Load {z}")
for z in ("PT-N", "PT-S"): L[z] = pp.create_load(net, B[z], p_mw=PT_LOAD / 2, q_mvar=a.q0 * PT_LOAD / 2, name=f"Load {z}")
L["MA"] = pp.create_load(net, B["MA"], p_mw=MA_LOAD, q_mvar=a.q0 * MA_LOAD, name="Load MA")
for z, p in PUMP_LOADS.items(): pp.create_load(net, B[z], p_mw=p, q_mvar=0, name=f"Pump {z}")
pp.create_load(net, B["CAT"], p_mw=HVDC_FR, q_mvar=0, name="HVDC to FR"); pp.create_sgen(net, B["FR"], p_mw=HVDC_FR, q_mvar=0, name="HVDC from ES")

import pandapower.shortcircuit as sc


def sc_report():
    XDSS = 0.20                                                                           # [inf] typical subtransient
    for i, n in zip(net.gen.index, net.gen.name):
        net.gen.at[i, "sn_mva"] = PMAX[n] / 0.9; net.gen.at[i, "vn_kv"] = 400
        net.gen.at[i, "xdss_pu"] = XDSS; net.gen.at[i, "rdss_ohm"] = 0.0; net.gen.at[i, "cos_phi"] = 0.9
    net.sgen["sn_mva"] = net.sgen.p_mw.abs() / 0.95; net.sgen["k"] = a.kres; net.sgen["generator_type"] = "current_source"

    SC_T = {"MAD": 10555, "VAL": 11167, "N": 10158, "CAT": (8830 + 11104) / 2, "NW": 9665, "WAN": 12271, "BAD": 8386}
    sc.calc_sc(net, case="max", ip=False, ith=False, branch_results=False)
    print("\nshort-circuit (MVA, IEC 60909 max): zone  model  Table 4-26")
    for z, t in SC_T.items():
        sk = net.res_bus_sc.at[B[VB(z)], "ikss_ka"] * np.sqrt(3) * 400
        print(f"   {z:4s} {sk:7.0f} {t:8.0f}  ({100 * (sk / t - 1):+.0f} %)")


if a.quick:
    sc_report(); raise SystemExit(0)
P0 = {z: net.load.at[i, "p_mw"] for z, i in L.items()}; Q0 = {z: net.load.at[i, "q_mvar"] for z, i in L.items()}
PQZ = [z for z in ES if z not in {g[1] for g in GEN}] + ["PT-S"]   # zones without a voltage-controlling unit
# per-zone distribution-network shunt (DSO cable charging / capacitor banks, V^2), calibrated: + absorbing, - injecting
CAL = {z: pp.create_shunt(net, B[z], q_mvar=0.0, name=f"Qdso {z}") for z in ES + ["PT-S", "PT-N"]}
# conventional-unit Q per area at 12:30-12:32 (Figs 2-84..2-86 [read]; units > 100 MW incl. pumped storage) [Mvar]
QAREA = {"N": -400, "SW": -150, "E": -600}
GEN_AREA = {"G4 N thermal": "N", "G5 N hydro": "N", "M1 Duero": "N", "M2 Ebro": "N",
            "G1 Almaraz II": "SW", "G6 SW CCGT": "SW", "G2 Cat nuclear A": "E", "G3 Cat nuclear B": "E", "G7 E CCGT": "E"}
GEN_ZONE = {n: z for n, z, _ in GEN}; GEN_ZONE.update({"M1 Duero": "CYL", "M2 Ebro": "ARA", "M3-7 Portugal": "PT-N", "Morocco": "MA"})
GZ = sorted({GEN_ZONE[n] for n in GEN_AREA})


LIDX = np.array([L[z] for z in L]); LZB = np.array([B[z if z in B else "MA"] for z in L])
LP0 = np.array([P0[z] for z in L]); LQ0 = np.array([Q0[z] for z in L]); LZ = list(L)


def solve(full=False):
    """One load flow + one exponential-load update (full=True: iterate the loads to convergence)."""
    for it in range(30 if full else 1):
        pp.runpp(net, init="results" if net.converged else "auto", max_iteration=50)
        v = net.res_bus.vm_pu.values[LZB]
        sc_ = np.array([scale.get(z, 1) for z in LZ]); p0 = np.array([P0[z] for z in LZ]); q0 = np.array([Q0[z] for z in LZ])
        np_, nq = sc_ * p0 * v ** a.alpha, sc_ * q0 * v ** a.beta
        dv = max(np.abs(np_ - net.load.loc[LIDX, "p_mw"].values).max(), np.abs(nq - net.load.loc[LIDX, "q_mvar"].values).max())
        net.load.loc[LIDX, "p_mw"] = np_; net.load.loc[LIDX, "q_mvar"] = nq
        if dv < (0.02 if full else 0.5): return it + 1
    return 30


LNF = np.array([net.bus.at[b, "name"] for b in net.line.from_bus]); LNT = np.array([net.bus.at[b, "name"] for b in net.line.to_bus])


def flow(za, zb):
    zb = list(zb); m1 = (LNF == za) & np.isin(LNT, zb); m2 = (LNT == za) & np.isin(LNF, zb)
    return net.res_line.p_from_mw.values[m1].sum() + net.res_line.p_to_mw.values[m2].sum()


def qflow(za, zb):
    zb = list(zb); m1 = (LNF == za) & np.isin(LNT, zb); m2 = (LNT == za) & np.isin(LNF, zb)
    return net.res_line.q_from_mvar.values[m1].sum() + net.res_line.q_to_mvar.values[m2].sum()


# tie reactive flows at 12:30 (Figs 2-92..2-94 [read]): ES->FR +300, ES->PT +100, ES->MA -360 Mvar
QTIE = {"FR": 300, "MA": -360}           # ES->PT (+100) is a CHECK, not a knob
iMA = net.gen.index[net.gen.name == "Morocco"][0]; iPT = net.gen.index[net.gen.name == "G8 PT conventional"][0]
scale = {}; qt = {}; NR = 0
GI = {n: i_ for i_, n in zip(net.gen.index, net.gen.name)}
# Fig 2-4 corridor flow targets at 12:32 ([read], RUNLOG S27 sec 32) and the knob for each:
# (kind, zone that gives, zone that takes) -- both zones in the same Fig 2-41 area
FLOWT = {("CAC", "MAD"): 3227}                                             # calibrated (demand WAN <-> MAD)
FCHK = {("BAD", "CAC"): 1850, ("GRA", "SE"): 900, ("VAL", "ARA"): 0, ("CAC", "CYL"): 1200}   # checks; Badajoz RES stays fixed (event plants)
KNOB = {("CAC", "MAD"): ("dem", "WAN", "MAD"),      # more Madrid demand pulls the corridor (SW area)
        ("BAD", "CAC"): ("res", "WAN", "BAD"),      # more Badajoz RES pushes north (SW area)
        ("GRA", "SE"): ("dem", "CAT", "SE"),        # flow too high -> SE demand moves to Catalonia (E area)
        ("VAL", "ARA"): ("dem", "NW", "ARA"),       # flow too high -> Aragon demand moves to the NW (N area)
        ("CAC", "CYL"): ("res", "SCE", "CAC")}      # flow too high -> Caceres RES moves to SCE (SW area)
RESI = {n.split()[-1]: i_ for i_, n in zip(net.sgen.index, net.sgen.name) if n.startswith("RES ")}


def calib(maxr):
    """One calibration run (the targets of passes 1-2); returns the number of rounds used."""
    global qt
    gain = {}
    for outer in range(maxr):
        if outer % 100 == 0:                                  # measured sensitivity dV(zone)/dQ(its shunt) -> loop gain
            solve(full=True)
            for z in PQZ:
                v0_ = net.res_bus.vm_pu[B[VB(z)]]; net.shunt.at[CAL[z], "q_mvar"] += 100.0; solve(full=True)
                sens = (v0_ - net.res_bus.vm_pu[B[VB(z)]]) / 100.0          # pu per Mvar (absorbing lowers V)
                net.shunt.at[CAL[z], "q_mvar"] -= 100.0
                gain[z] = 0.5 / max(sens, 1e-6)                  # half a Newton step, Mvar per pu
                if os.environ.get("CALDBG") and outer in (0, 500): print(f"      sens {z}: {sens * 4e5:+.1f} kV/Gvar at {400 * v0_:.1f} kV", flush=True)
            solve(full=True)
        solve()
        V = net.res_bus.vm_pu
        for z in PQZ:                                          # voltage at load-only zones -> Fig 2-4
            net.shunt.at[CAL[z], "q_mvar"] += float(np.clip(gain[z] * (V[B[VB(z)]] - VT[z] / 400), -250, 250))
        for n, z, _ in GEN:                                    # zones with units: unit set-point -> hub voltage on Fig 2-4
            i_ = GI[n]
            net.gen.at[i_, "vm_pu"] += float(np.clip(0.7 * (VT[z] / 400 - V[B[z]]), -0.01, 0.01))
        qg = dict(zip(net.gen.name, net.res_gen.q_mvar))       # unit Q per area -> Figs 2-84..2-86, shared by P rating
        for A, tgt in QAREA.items():
            names = [n for n, ar in GEN_AREA.items() if ar == A]; tot_p = sum(abs(net.gen.at[GI[n], "p_mw"]) for n in names)
            for n in names:
                share = abs(net.gen.at[GI[n], "p_mw"]) / tot_p
                net.shunt.at[CAL[GEN_ZONE[n]], "q_mvar"] -= float(np.clip(0.2 * (qg[n] - tgt * share), -250, 250))
        pt = sum(flow(z, {"PT-N", "PT-S"}) for z in ES); fr = sum(flow(z, {"FR"}) for z in ES) + HVDC_FR
        k_pt = scale.get("PT-N", 1) * (1 - 0.6 * (pt - 2100) / (PT_LOAD + 2098))
        scale["PT-N"] = scale["PT-S"] = k_pt                    # Portuguese load -> ES->PT 2,100 (Fig 2-22)
        k_es = scale.get("GRA", 1) * (1 + 0.6 * (fr - 1175) / sum(P0[z] for z in ES))
        for z in ES: scale[z] = k_es                            # Spanish demand -> ES->FR 1,175 (Fig 2-22)
        # Fig 2-4 corridor flows (read) via paired MW shifts inside one Fig 2-41 area (area totals unchanged)
        cf = {k: flow(k[0], {k[1]}) for k in FLOWT}
        if a.flowcal:
            for (za, zb), tgt in FLOWT.items():
                kind, dn, up = KNOB[(za, zb)]; d_ = float(np.clip(0.25 * (tgt - cf[(za, zb)]), -60, 60))
                if kind == "dem":
                    if P0[up] + d_ > 50 and P0[dn] - d_ > 50: P0[up] += d_; P0[dn] -= d_; Q0[up] = a.q0 * P0[up]; Q0[dn] = a.q0 * P0[dn]
                else:
                    iu, idn = RESI[up], RESI[dn]
                    if net.sgen.at[iu, "p_mw"] + d_ > 50 and net.sgen.at[idn, "p_mw"] - d_ > 50:
                        net.sgen.at[iu, "p_mw"] += d_; net.sgen.at[idn, "p_mw"] -= d_
                        net.sgen.at[iu, "q_mvar"] = a.kpf * net.sgen.at[iu, "p_mw"]; net.sgen.at[idn, "q_mvar"] = a.kpf * net.sgen.at[idn, "p_mw"]
        qt = {"FR": sum(qflow(z, {"FR"}) for z in ES), "PT": sum(qflow(z, {"PT-N", "PT-S"}) for z in ES), "MA": qflow("WAN", {"MA-B"})}
        net.ext_grid.at[0, "vm_pu"] += float(np.clip(2e-5 * (qt["FR"] - QTIE["FR"]), -0.005, 0.005))   # too much Q out -> raise V
        net.gen.at[iMA, "vm_pu"] += float(np.clip(2e-5 * (qt["MA"] - QTIE["MA"]), -0.005, 0.005))
        err = max(abs(400 * (V[B[VB(z)]] - VT[z] / 400)) for z in VT)
        qerr = max(abs(sum(qg[n] for n, ar in GEN_AREA.items() if ar == A) - t) for A, t in QAREA.items())
        terr = max(abs(qt[k] - QTIE[k]) for k in QTIE)
        ferr = max(abs(cf[k] - t) for k, t in FLOWT.items()) if a.flowcal else 0
        if os.environ.get("CALDBG") and (outer % 250 == 0 or outer == maxr - 1):
            worst = max(VT, key=lambda z: abs(400 * (V[B[VB(z)]] - VT[z] / 400)))
            print(f"    round {outer}: V err {err:.1f} kV (worst {worst} {400 * V[B[VB(worst)]]:.1f}/{VT[worst]})  unitQ err {qerr:.0f}  tieQ err {terr:.0f}  "
                  f"PT {pt:.0f} FR {fr:.0f}  flow err {ferr:.0f}  gen vm " + " ".join(f"{v:.3f}" for v in net.gen.vm_pu), flush=True)
        if outer > 3 and err < 0.5 and qerr < 20 and terr < 20 and abs(pt - 2100) < 20 and abs(fr - 1175) < 20 and ferr < 30: return outer + 1
    return maxr


# ---- simultaneous calibration (scipy least_squares over all knobs; replaces the one-knob loops, RUNLOG S27 sec 33) ----
from scipy.optimize import least_squares
KZ = list(CAL)                                              # DSO shunts (Mvar)
KG = [n for n, _, _ in GEN]                                 # unit set-points (pu)


def getx():
    return np.concatenate([[net.shunt.at[CAL[z], "q_mvar"] / 1000 for z in KZ], [net.gen.at[GI[n], "vm_pu"] for n in KG],
                           [scale.get("GRA", 1), scale.get("PT-N", 1), net.ext_grid.at[0, "vm_pu"], net.gen.at[iMA, "vm_pu"],
                            (P0["MAD"] - P0_MAD0) / 1000, net.gen.at[iMA, "p_mw"] / 1000]])


def setx(x):
    k = 0
    for z in KZ: net.shunt.at[CAL[z], "q_mvar"] = 1000 * x[k]; k += 1
    for n in KG: net.gen.at[GI[n], "vm_pu"] = x[k]; k += 1
    for z in ES: scale[z] = x[k]
    scale["PT-N"] = scale["PT-S"] = x[k + 1]
    net.ext_grid.at[0, "vm_pu"] = x[k + 2]; net.gen.at[iMA, "vm_pu"] = x[k + 3]
    d = 1000 * x[k + 4]; P0["MAD"] = P0_MAD0 + d; P0["WAN"] = P0_WAN0 - d        # Madrid corridor knob (SW area)
    Q0["MAD"] = a.q0 * P0["MAD"]; Q0["WAN"] = a.q0 * P0["WAN"]
    if len(x) > k + 5: net.gen.at[iMA, "p_mw"] = 1000 * x[k + 5]                    # Morocco unit P -> ES->MA export


def resid(x):
    setx(x)
    try:
        solve(full=True)
    except Exception:
        net.converged = False; return np.full(NRES, 50.0)
    V = net.res_bus.vm_pu; qg = dict(zip(net.gen.name, net.res_gen.q_mvar))
    r = [400 * (V[B[VB(z)]] - VT[z] / 400) for z in VT]                                       # kV
    r += [(sum(qg[n] for n, ar in GEN_AREA.items() if ar == A) - t) / 50 for A, t in QAREA.items()]    # 50 Mvar ~ 1 kV
    pt = sum(flow(z, {"PT-N", "PT-S"}) for z in ES); fr = sum(flow(z, {"FR"}) for z in ES) + HVDC_FR
    ma = flow("WAN", {"MA-B"})
    r += [(pt - 2100) / 50, (fr - FR_T) / 50, (ma - 750) / 50, (flow("N", {"FR"}) - 310) / 50]   # west tie: Fig 2-41 North->France 310
    qfr = sum(qflow(z, {"FR"}) for z in ES); qma = qflow("WAN", {"MA-B"}); qpt = sum(qflow(z, {"PT-N", "PT-S"}) for z in ES)
    r += [(-(qg["G1 Almaraz II"] + qg["G6 SW CCGT"] + qg["G7 E CCGT"]) - 74) / 50]   # Fig 4-2: PO 7.4 units, South Spain, 74 Mvar absorbed
    r += [(qfr - QTIE["FR"]) / 50, (qma - QTIE["MA"]) / 50, (qpt - 100) / 50]          # ES->PT tie Q now a target (Fig 2-93)
    if a.flowcal: r += [(flow("CAC", {"MAD"}) - FLOWT[("CAC", "MAD")]) / 50]
    r += list(0.02 * (x[:len(KZ)]))                                                          # mild preference for small shunts
    return np.array(r)


P0_MAD0, P0_WAN0 = P0["MAD"], P0["WAN"]
NRES = len(VT) + len(QAREA) + 8 + (1 if a.flowcal else 0) + len(KZ)


def calib_ls(tag=""):
    x0 = getx()
    lo = np.concatenate([np.full(len(KZ), -6.0), np.full(len(KG), 0.85), [0.7, 0.5, 0.9, 0.85, -1.5, 3.0]])
    hi = np.concatenate([np.full(len(KZ), 6.0), np.full(len(KG), 1.15), [1.3, 1.5, 1.1, 1.15, 1.5, 6.0]])
    x0 = np.clip(x0, lo + 1e-6, hi - 1e-6)
    sol = least_squares(resid, x0, bounds=(lo, hi), x_scale="jac", diff_step=float(os.environ.get("DSTEP", 1e-3)), max_nfev=400)
    setx(sol.x); solve(full=True)
    r = resid(sol.x)
    print(f"  {tag} least_squares: nfev {sol.nfev}, max |V err| {np.abs(r[:len(VT)]).max():.2f} kV, "
          f"max other err {np.abs(r[len(VT):len(VT) + len(QAREA) + 9]).max() * 50:.0f} (MW/Mvar)", flush=True)
    return sol.nfev


# continuation: calibrate at physical settings (corridor X x1, unit connection 15 %), then step to the fitted
# fault-level settings (--xk, --vkg), re-calibrating at each step from the previous solution (RUNLOG S27 sec 31)
LX = net.line.x_ohm_per_km.copy(); XK1 = {i_: (1.0 if n == "WAN-MA-B" else a.xk) for i_, n in zip(net.line.index, net.line.name)}   # the cable is not scaled
TV = {i_: net.trafo.at[i_, "vk_percent"] for i_ in net.trafo.index if net.trafo.at[i_, "name"].startswith("T ") and net.trafo.at[i_, "vk_percent"] == a.vkg}
RESUME = os.environ.get("RESUME") and os.path.exists(os.path.join(HERE, "pp_v2_state.pkl"))
if RESUME and not a.quick:                                # start from the saved solved state (full lengths, full unit-X)
    import pickle; st = pickle.load(open(os.path.join(HERE, "pp_v2_state.pkl"), "rb"))
    P0.update(st["P0"]); Q0.update(st["Q0"]); x_ = st["x"]
    d_ = 1000 * x_[-1]; P0_MAD0, P0_WAN0 = P0["MAD"] - d_, P0["WAN"] + d_      # saved P0 already holds the Madrid shift
    if len(x_) == len(getx()) - 1: x_ = np.append(x_, net.gen.at[iMA, "p_mw"] / 1000)   # state saved before the Morocco knob
    setx(x_)
    import pandas as pd                                     # warm start from the saved solved voltages
    net.res_bus = pd.DataFrame({"vm_pu": st["vm"], "va_degree": st["va"], "p_mw": 0.0, "q_mvar": 0.0}, index=net.bus.index)
    net.converged = True
    solve(full=True); print("resumed from pp_v2_state.pkl", flush=True)
    NR += calib_ls("resume-final")
    import pickle; pickle.dump({"x": getx(), "P0": P0, "Q0": Q0, "vm": net.res_bus.vm_pu.values, "va": net.res_bus.va_degree.values}, open(os.path.join(HERE, "pp_v2_state.pkl"), "wb"))
elif not a.quick:
    HUB_KM = {i_: net.line.at[i_, "length_km"] for i_ in net.line.index}
    OSMI = {i_: OSM_KM.get(tuple(net.line.at[i_, "name"].split("-", 1)) if net.line.at[i_, "name"].count("-") == 1 else None, HUB_KM[i_])
            for i_ in net.line.index}
    for i_, n in zip(net.line.index, net.line.name):        # PT ties: names like "CAC-PT-N"
        za = n.split("-")[0]; zb = n[len(za) + 1:]
        OSMI[i_] = OSM_KM.get((za, zb), OSM_KM.get((zb, za), HUB_KM[i_])) if (za, zb) in OSM_KM or (zb, za) in OSM_KM else HUB_KM[i_]
    def setstep(fl, fv):
        for i_ in net.line.index:
            net.line.at[i_, "length_km"] = OSMI[i_] + (HUB_KM[i_] - OSMI[i_]) * fl
            k_ = XK1[i_]; net.line.at[i_, "x_ohm_per_km"] = LX[i_] / k_ * (1 + (k_ - 1) * fv)
        for i_ in TV: net.trafo.at[i_, "vk_percent"] = 15 + (a.vkg - 15) * fv
    steps = [(0.0, 0.0)] + [(round(f, 2), 0.0) for f in np.arange(0.1, 1.0001, 0.1)] + [(1.0, round(f, 2)) for f in np.arange(0.1, 1.0001, 0.1)]
    last = None
    for fl, fv in steps:
        setstep(fl, fv)
        try:
            NR += (calib(600) if (fl == 0.0 and fv == 0.0) else 0) + calib_ls(f"lengths {fl:.1f} / unit-X {fv:.1f}"); last = (fl, fv)
            if os.environ.get("PROBE") and fl >= float(os.environ["PROBE"]):
                solve(); v0 = net.res_bus.vm_pu[B["BAD-TS"]]; q0_ = net.shunt.at[CAL["BAD"], "q_mvar"]
                net.shunt.at[CAL["BAD"], "q_mvar"] += 1000; solve(); v1 = net.res_bus.vm_pu[B["BAD-TS"]]
                print(f"PROBE: BAD shunt {q0_:+.0f} -> {q0_ + 1000:+.0f} Mvar: BAD-TS {400 * v0:.2f} -> {400 * v1:.2f} kV; converged {net.converged}")
                print("PROBE shunts:", net.shunt[["name", "bus", "q_mvar", "step", "in_service"]].tail(16).to_string())
                raise SystemExit(0)
        except Exception as ex_:
            print(f"  continuation lengths {fl:.1f} / unit-X {fv:.1f} FAILED: {type(ex_).__name__}; last good {last}", flush=True)
            top = net.res_line.loading_percent.sort_values(ascending=False).head(6).index
            for i_ in top: print(f"     {net.line.at[i_, 'name']:12s} x{int(net.line.at[i_, 'parallel'])} {net.line.at[i_, 'length_km']:.0f} km  P {net.res_line.at[i_, 'p_from_mw']:+7.0f} MW  {net.res_line.at[i_, 'loading_percent']:.0f} %")
            raise SystemExit(1)
    NR += calib_ls("final"); print(f"  final calibration: total evaluations {NR}", flush=True)
    import pickle; pickle.dump({"x": getx(), "P0": P0, "Q0": Q0, "vm": net.res_bus.vm_pu.values, "va": net.res_bus.va_degree.values}, open(os.path.join(HERE, "pp_v2_state.pkl"), "wb"))
outer = NR
it = solve(full=True)
print(f"calibration pass 3: {outer} rounds; Portuguese load x{scale.get('PT-N', 1):.3f}, Spanish demand x{scale.get('GRA', 1):.3f}")
print("DSO shunts at 1 pu (Mvar, + absorbing): " + "  ".join(f"{z} {net.shunt.at[CAL[z], 'q_mvar']:+.0f}" for z in CAL))
qg = dict(zip(net.gen.name, net.res_gen.q_mvar))
print("unit Q per area: " + "  ".join(f"{A} {sum(qg[n] for n, ar in GEN_AREA.items() if ar == A):+.0f} (target {t:+d})" for A, t in QAREA.items()))
qload = sum(net.res_load.q_mvar[[L[z] for z in ES]]); qdso = sum(net.res_shunt.q_mvar[[CAL[z] for z in ES]])
pload = sum(net.res_load.p_mw[[L[z] for z in ES]])
print(f"Spanish distribution exchange: P {pload:.0f} MW, Q {qload + qdso:+.0f} Mvar (load {qload:+.0f}, DSO shunts {qdso:+.0f}); "
      f"Fig 4-84 (400 kV interface only, ~8.7 GW): Q -1,000 ... -1,800 Mvar")
V = net.res_bus.vm_pu
V = net.res_bus.vm_pu
print("zone  V[kV] target  demand   RES")
for z in BUSES:
    print(f"{z:6s} {400 * V[B[z]]:6.1f} {VT.get(z, '')!s:>6s}  {DEM.get(z, 0) * scale.get(z, 1):6.0f} {RES.get(z, 0):6.0f}")
es = set(ES)
pt = sum(flow(z, {"PT-N", "PT-S"}) for z in ES); ma = flow("WAN", {"MA-B"}); fr_ac = sum(flow(z, {"FR"}) for z in ES)
mad_in = -sum(flow("MAD", {z}) for z in ES if z != "MAD")
print(f"\nborders ES->PT {pt:6.0f} MW (target ~2,100) | ES->MA {ma:5.0f} (~750) | ES->FR AC {fr_ac:5.0f} + HVDC {HVDC_FR} "
      f"= {fr_ac + HVDC_FR:5.0f} (target {FR_T:.0f})")
for i_, n in zip(net.line.index, net.line.name):
    if "FR" in n: print(f"   tie {n:10s} x{int(net.line.at[i_, 'parallel'])} {net.line.at[i_, 'length_km']:5.0f} km  P {net.res_line.at[i_, 'p_from_mw']:+6.0f} MW  Q {net.res_line.at[i_, 'q_from_mvar']:+6.0f}")
print(f"   Morocco unit P {net.gen.at[iMA, 'p_mw']:.0f} MW, Moroccan load {net.res_load.at[L['MA'], 'p_mw']:.0f} MW")
sw_mad = flow("CAC", {"MAD"}) + flow("SCE", {"MAD"})
print("corridor flows vs Fig 2-4: " + "  ".join(f"{k[0]}->{k[1]} {flow(k[0], {k[1]}):+.0f} ({t})" for k, t in {**FLOWT, **FCHK}.items()))
print("zone demand now: " + "  ".join(f"{z} {P0[z] * scale.get(z, 1):.0f}" for z in ES))
print("zone RES now:    " + "  ".join(f"{z} {net.sgen.at[RESI[z], 'p_mw']:.0f}" for z in ES if z in RESI))
print(f"Madrid net in-feed {mad_in:6.0f} MW; SW corridor CAC+SCE -> MAD {sw_mad:6.0f} MW (Fig 2-4: 3,227 on the six circuits)")
print("generator Q [Mvar]: " + "  ".join(f"{n.split()[0]} {q:+.0f}" for n, q in zip(net.gen.name, net.res_gen.q_mvar)))
print(f"France slack P {net.res_ext_grid.p_mw.iloc[0]:+.0f} MW, Q {net.res_ext_grid.q_mvar.iloc[0]:+.0f} Mvar")
qt = {"FR": sum(qflow(z, {"FR"}) for z in ES), "PT": sum(qflow(z, {"PT-N", "PT-S"}) for z in ES), "MA": qflow("WAN", {"MA-B"})}
if qt: print("tie Q ES->X: " + "  ".join(f"{k} {v:+.0f} (target {QTIE.get(k, 100):+d})" for k, v in qt.items()) +
      f" | set-points FR {net.ext_grid.at[0, 'vm_pu'] * 400:.1f} kV, MA {net.gen.at[iMA, 'vm_pu'] * 400:.1f} kV, PT {net.gen.at[iPT, 'vm_pu'] * 400:.1f} kV")
if os.environ.get("QBAL", "1") == "1":                      # reactive-power balance by source (RUNLOG S27 sec 35)
    import pandas as pd; qg_ = dict(zip(net.gen.name, net.res_gen.q_mvar))
    SW_Z = ["GRA", "WAN", "BAD", "CAC", "SCE"]; ES_B = set(ES) | {f"{z}-TS" for z in TSX}
    bn = lambda b: net.bus.at[b, "name"]
    def qsum(df, res, pred, col="q_mvar"):
        return sum(res.at[i_, col] for i_ in df.index if pred(df.at[i_, "bus"], df.at[i_, "name"]))
    for tag, zs in (("Spain", ES_B), ("South-West", set(SW_Z) | {f"{z}-TS" for z in TSX})):
        lc = 0.0
        for i_ in net.line.index:                           # charging of the modelled 400 kV corridors, half to each end
            vf, vt = net.res_bus.vm_pu[net.line.at[i_, "from_bus"]], net.res_bus.vm_pu[net.line.at[i_, "to_bus"]]
            bq = 2 * np.pi * 50 * net.line.at[i_, "c_nf_per_km"] * 1e-9 * net.line.at[i_, "length_km"] * net.line.at[i_, "parallel"] * 400 ** 2
            lc += bq / 2 * ((vf ** 2 if bn(net.line.at[i_, "from_bus"]) in zs else 0) + (vt ** 2 if bn(net.line.at[i_, "to_bus"]) in zs else 0))
        cint = -qsum(net.shunt, net.res_shunt, lambda b, n: n.startswith("Cint") and bn(b) in zs)
        reac = qsum(net.shunt, net.res_shunt, lambda b, n: n.startswith("Reac") and bn(b) in zs)
        dso = qsum(net.shunt, net.res_shunt, lambda b, n: n.startswith("Qdso") and bn(b) in zs)
        ld = qsum(net.load, net.res_load, lambda b, n: n.startswith("Load") and bn(b) in zs)
        res_ = -qsum(net.sgen, net.res_sgen, lambda b, n: n.startswith("RES") and bn(b) in zs)
        resp = qsum(net.sgen, net.res_sgen, lambda b, n: n.startswith("RES") and bn(b) in zs, "p_mw")
        un = -sum(net.res_gen.at[i_, "q_mvar"] for i_, n in zip(net.gen.index, net.gen.name) if n in GEN_ZONE and GEN_ZONE[n] in zs)
        print(f"\nreactive balance {tag} (Mvar):")
        print(f"   generated: 400 kV corridor charging {lc:6.0f}   zone-internal 400 kV charging {cint:6.0f}")
        print(f"   absorbed : reactors {reac:6.0f}  loads {ld:6.0f}  RES {res_:6.0f} (P {resp:.0f}, Q/P {res_ / max(resp, 1):.3f})  "
              f"units {un:6.0f}  DSO shunts {dso:+6.0f}  (+ = absorbing)")
    ql = net.res_line.q_from_mvar + net.res_line.q_to_mvar           # net Q consumed by each line (I2X - charging)
    lc_all = pd.Series({i_: 2 * np.pi * 50 * net.line.at[i_, "c_nf_per_km"] * 1e-9 * net.line.at[i_, "length_km"] * net.line.at[i_, "parallel"]
                        * 400 ** 2 * (net.res_bus.vm_pu[net.line.at[i_, "from_bus"]] ** 2 + net.res_bus.vm_pu[net.line.at[i_, "to_bus"]] ** 2) / 2 for i_ in net.line.index})
    i2x = ql + lc_all
    print("");print(f"series reactive losses I2X, all lines: {i2x.sum():.0f} Mvar (charging {lc_all.sum():.0f}); largest:")
    for i_ in i2x.sort_values(ascending=False).index[:10]:
        print(f"   {net.line.at[i_, 'name']:12s} x{int(net.line.at[i_, 'parallel'])} {net.line.at[i_, 'length_km']:4.0f} km  P {net.res_line.at[i_, 'p_from_mw']:+6.0f} MW  I2X {i2x[i_]:5.0f}  charging {lc_all[i_]:4.0f} Mvar")
    qtr = (net.res_trafo.q_hv_mvar + net.res_trafo.q_lv_mvar).sum()
    print(f"   transformer reactive losses {qtr:.0f} Mvar")
    SS = {"GRA", "WAN", "BAD", "CAC", "SCE", "MAD", "VAL", "SE", "BAD-TS", "WAN-TS"}   # Fig 4-2 "South Spain" = S + C + E
    rq = -qsum(net.sgen, net.res_sgen, lambda b, n: n.startswith("RES") and bn(b) in SS)
    rp = qsum(net.sgen, net.res_sgen, lambda b, n: n.startswith("RES") and bn(b) in SS, "p_mw")
    rx = qsum(net.shunt, net.res_shunt, lambda b, n: n.startswith("Reac") and bn(b) in SS)
    po = -(qg_["G1 Almaraz II"] + qg_["G6 SW CCGT"] + qg_["G7 E CCGT"])
    print(f"Fig 4-2 South Spain 12:32:00: RES {rq:.0f} Mvar on {rp:.0f} MW (report 2,297 on 17,020) | reactors {rx:.0f} (1,300) | PO 7.4 units {po:.0f} (74)")
sc_report()
