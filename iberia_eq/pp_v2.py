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
PT_RES_S = float(os.environ.get("PT_RES_S", 0.6))           # S28 Portugal scan knobs (defaults = S27 values)
PT_LOAD, PT_RES = 5600, {"PT-S": PT_RES_S * (1604 + 2104 + 761), "PT-N": (1 - PT_RES_S) * (1604 + 2104 + 761)}  # Fig 2-16 / 2-19 [read]; split [inf]
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
CORR = os.environ.get("CORR", "v1")                          # v2: corridors_v2.csv / zone_km_v2.csv (build_corridors_v2.py, RUNLOG S28)
SFX = "_v2" if CORR == "v2" else ""
CHG_PHYS = os.environ.get("CHG", "hub") == "phys"            # phys: each corridor's charging = its OSM circuit-km, not hub-to-hub length (S28)
STATE = os.path.join(HERE, os.environ.get("STATE", "pp_v2_state.pkl"))
cor = list(csv.DictReader(open(os.path.join(HERE, f"corridors{SFX}.csv"), encoding="utf-8")))
PTMAP = {"NW": "PT-N", "CYL": "PT-N", "CAC": "PT-N", "BAD": "PT-S", "WAN": "PT-S"}
pairs = {}
for r in cor:
    za, zb = r["zone_a"], r["zone_b"]
    if "PT" in (za, zb):
        z = zb if za == "PT" else za; za, zb = z, PTMAP[z]
    k = tuple(sorted((za, zb))); km, nc = float(r["route_km"]), int(r["circuits"])
    p = pairs.setdefault(k, [0, 0.0]); p[0] += nc; p[1] += km * nc
EXTRA = {("WAN", "MA-B"): (2, 30.0, "cable"), ("MA-B", "MA"): (2, 200.0, "ohl"),
         ("PT-N", "PT-S"): (int(os.environ.get("PT_INT_NC", 3)), float(os.environ.get("PT_INT_KM", 250.0)), "ohl")}
PT_TIE_K = float(os.environ.get("PT_TIE_K", 1.0))          # scale on the hub-to-hub length of the Spain-Portugal ties (S28 scan)
PT_TIE_SW = float(os.environ.get("PT_TIE_SW", 1.0))        # extra scale on the ties from the Spanish SW area (CAC, BAD, WAN) [inf, S28]
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
# CORR_X=fit: corridor reactances from the zonal reduction of the full OSM network (reduce_fullnet.py, RUNLOG S29 sec 8)
CORR_X_FIT = os.environ.get("CORR_X", "hub") == "fit"
XFIT = {}
if CORR_X_FIT:
    fn_ = "corridor_x_fit_open.csv" if os.environ.get("OPEN_LINES", "0") == "1" else "corridor_x_fit.csv"
    XFIT = {tuple(sorted((r["zone_a"], r["zone_b"]))): float(r["x_fit_ohm"]) for r in csv.DictReader(open(os.path.join(HERE, fn_), encoding="utf-8"))}
    if ("CAC", "PT-S") not in pairs: pairs[("CAC", "PT-S")] = [1, 80.0]; OSM_KM[("CAC", "PT-S")] = 80.0   # Cedillo-Falagueira [inf length]
    print(f"CORR_X=fit: {len(XFIT)} corridor reactances from {fn_}")
PHYS_CKM = {k: v[1] for k, v in pairs.items()}             # physical circuit-km per corridor (OSM)
if CORR_X_FIT: PHYS_CKM[("CAC", "PT-S")] = 0.0               # its charging is already counted in CAC-PT-N (OSM mapping)
print("corridor lengths (OSM border-line mean km -> hub-to-hub 1.2 x centroid km):")
for k in list(pairs):
    if any(z.startswith("PT") for z in k) or (HUB_ALL and all(z in CEN for z in k)):
        nc0 = pairs[k][0]; old_km = pairs[k][1] / nc0
        nc = max(nc0, a.mincirc)                            # [inf] equivalent circuits incl. parallel 220 kV paths / OSM gaps
        if CORR_X_FIT and tuple(sorted(k)) in XFIT:        # length such that X_KM * L / nc = fitted reactance
            pairs[k] = [nc, nc * XFIT[tuple(sorted(k))] * nc / X_KM]
        else:
            pairs[k] = [nc, nc * a.route * gc(CEN[k[0]], CEN[k[1]]) * (PT_TIE_K * (PT_TIE_SW if set(k) & {"CAC", "BAD", "WAN"} else 1.0) if any(z.startswith("PT") for z in k) else 1.0)]
        OSM_KM[k] = old_km
        print(f"   {k[0]:>4s}-{k[1]:<5s} x{nc0}->{nc}: {old_km:5.0f} -> {pairs[k][1] / nc:5.0f}")
zkm = {r["zone"]: float(r["circuit_km_incl_half_ties"]) for r in csv.DictReader(open(os.path.join(HERE, f"zone_km{SFX}.csv"), encoding="utf-8"))}
ties_ckm = {z: 0.0 for z in zkm}
for (za, zb), (nc, ckm) in pairs.items():
    for z in (za, zb):
        zz = "PT" if z.startswith("PT") else z
        if zz in ties_ckm: ties_ckm[zz] += (PHYS_CKM[(za, zb)] if CHG_PHYS else ckm) / 2
internal_ckm = {z: max(0.0, zkm[z] - ties_ckm.get(z, 0)) for z in zkm}
# Table 2-12 ([FR] p.114-115): 400 kV lines still open at 12:32 (opened for voltage control, closed later on 28/04).
# Lengths [inf] = straight substation distance x 1.15 (OSM coordinates): Pierola-Sentmenat 26 -> 30 km (CAT),
# Cofrentes-La Muela 11 -> 13 km (VAL), Fuendetodos-Mezquita 69 -> 79 km and Mezquita-Morella 57 -> 66 km (both ARA; Morella
# is ARA's end of the ARA-VAL corridor, so Mezquita-Morella open also removes one equivalent ARA-VAL circuit) (RUNLOG S29)
# PUMP_PT_V=1: Portuguese pump motors hold the PT-N hub target (398 kV) instead of the 408 kV default, which made them
# generate ~1 Gvar against the Portuguese unit (circulating Q, RUNLOG S29) [inf]
OPEN_LINES = os.environ.get("OPEN_LINES", "0") == "1"
if OPEN_LINES:
    if os.environ.get("CORR_X", "hub") == "fit":           # only Pierola-Sentmenat (41 km x2) is in the OSM line list (S29 sec 8)
        internal_ckm["CAT"] = max(0.0, internal_ckm["CAT"] - 82.0)
        print("OPEN_LINES (fit mode): CAT internal charging -82 circuit-km (Pierola-Sentmenat); reactances from the reduced network")
    else:
        for z_, km_ in {"CAT": 30.0, "VAL": 13.0, "ARA": 145.0}.items():
            internal_ckm[z_] = max(0.0, internal_ckm[z_] - km_)
        k_ = ("ARA", "VAL"); nc_, ckm_ = pairs[k_]; n2_ = max(1, nc_ - 1); pairs[k_] = [n2_, ckm_ / nc_ * n2_]
        print(f"OPEN_LINES: internal charging -30/-13/-145 km (CAT/VAL/ARA); ARA-VAL x{nc_} -> x{n2_}")

net = pp.create_empty_network(f_hz=50, sn_mva=100)
B = {b: pp.create_bus(net, vn_kv=400, name=b) for b in BUSES}
CTOT = {}                                                    # line index -> total nF (CHG=phys keeps it through the continuation)
for (za, zb), (nc, ckm) in pairs.items():
    i_ = pp.create_line_from_parameters(net, B[za], B[zb], length_km=ckm / nc, r_ohm_per_km=R_KM, x_ohm_per_km=a.xk * X_KM,
                                        c_nf_per_km=C_NF_KM * (PHYS_CKM[(za, zb)] / ckm if CHG_PHYS else 1.0), max_i_ka=2.0,
                                        parallel=nc, name=f"{za}-{zb}")
    if CHG_PHYS: CTOT[i_] = C_NF_KM * PHYS_CKM[(za, zb)]
for (za, zb), (nc, km, kind) in EXTRA.items():
    c = 230.0 if kind == "cable" else C_NF_KM; x = 0.12 if kind == "cable" else a.xk * X_KM      # [inf] 400 kV cable
    if CORR_X_FIT and tuple(sorted((za, zb))) in XFIT and kind == "ohl":
        x = XFIT[tuple(sorted((za, zb)))] * nc / km
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
# EMB_KPF: embedded cogeneration / waste / small hydro / solar thermal follow the RD 413/2014 PF band like RES ([CA] p.66,
# p.112); value [inf] = the Fig 4-2 RES ratio -0.135 when set to "fig42". Default 0 (S27/S28 behaviour). RUNLOG S29 sec 6
EMB_KPF = os.environ.get("EMB_KPF", "0"); EMB_KPF = a.kpf if EMB_KPF == "fig42" else float(EMB_KPF)
for n, sp, p in EMB:
    for z, f in sp.items(): pp.create_sgen(net, B[z], p_mw=p * f, q_mvar=EMB_KPF * p * f, name=f"{n} {z}")
for n, z, p in PUMPS: pp.create_gen(net, B[z], p_mw=-p, vm_pu=VT.get({"PS-CYL": "CYL", "PS-ARA": "ARA", **({"PS-PT": "PT-N"} if os.environ.get("PUMP_PT_V", "0") == "1" else {})}.get(z, ""), 408) / 400, name=n)
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


CNT = {"runpp": 0, "resid": 0, "t_pf": 0.0}               # cost counters (S28 profiling)
import time


FAST = os.environ.get("FAST", "0") == "1"                 # fastpf.py: own Newton on pandapower's Ybus, exponential loads exact (S28)
FP = None


def solve(full=False):
    """One load flow + one exponential-load update (full=True: iterate the loads to convergence)."""
    global FP
    if FAST:
        if FP is None:
            from fastpf import FastPF
            pp.runpp(net, init="results" if net.converged else "auto", max_iteration=50)
            FP = FastPF(net, [CAL[z] for z in CAL], LIDX, a.alpha, a.beta)
        sc_ = np.array([scale.get(z, 1) for z in LZ])
        t_ = time.perf_counter(); CNT["runpp"] += 1
        try:
            it = FP.solve(sc_ * np.array([P0[z] for z in LZ]), sc_ * np.array([Q0[z] for z in LZ]))
            CNT["t_pf"] += time.perf_counter() - t_
            return it
        except (RuntimeError, np.linalg.LinAlgError):              # fall back to pandapower + the fixed-point load loop
            CNT["fallback"] = CNT.get("fallback", 0) + 1
            for it in range(30):
                pp.runpp(net, init="results" if net.converged else "auto", max_iteration=50)
                v = net.res_bus.vm_pu.values[LZB]
                np_, nq = sc_ * np.array([P0[z] for z in LZ]) * v ** a.alpha, sc_ * np.array([Q0[z] for z in LZ]) * v ** a.beta
                dv = max(np.abs(np_ - net.load.loc[LIDX, "p_mw"].values).max(), np.abs(nq - net.load.loc[LIDX, "q_mvar"].values).max())
                net.load.loc[LIDX, "p_mw"] = np_; net.load.loc[LIDX, "q_mvar"] = nq
                if dv < 0.02: break
            FP.V = net._ppc["internal"]["V"].copy()
            return it + 1
    for it in range(30 if full else 1):
        t_ = time.perf_counter(); CNT["runpp"] += 1
        pp.runpp(net, init="results" if net.converged else "auto", max_iteration=50)
        CNT["t_pf"] += time.perf_counter() - t_
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
RESTS_I = {n.split()[-1]: i_ for i_, n in zip(net.sgen.index, net.sgen.name) if n.startswith("RESTS ")}


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


OBJ2 = os.environ.get("OBJ", "1") == "2"                   # objective v2: identifiability terms (S28)
QEX_T = float(os.environ.get("QEX", -2500))                 # Spanish TSO-DSO net Q, Mvar (+ absorbing): Fig 4-84 -1.0..-1.8 Gvar at the
                                                            # 400 kV interface (8.7 of 24 GW), scaled -2.8..-5.0 [inf]; soft, +-500
TRIPCAL = os.environ.get("TRIPCAL", "0") == "1"             # trip-sensitivity residuals + unit connection X as a knob (S28)
KNOB_VKG = False                                            # switched on after the continuation (final fit and resume only)
VKG = [a.vkg]
TRIP_T = {"E4": float(os.environ.get("TRIP_E4", 4.9)), "E3": float(os.environ.get("TRIP_E3", 1.44))}   # kV: Fig 3-7a; 48 Mvar x 30 kV/Gvar


def XNAMES():
    return ["mor"] + (["pt"] if PTSPLIT else []) + (["fbad", "fse", "fcac"] if FLOW2 else []) + ([f"d_{z}" for z in DKN] if DISPATCH else []) + (["vkg"] if KNOB_VKG else [])


def set_vkg(v):
    """Connection reactance of the SPANISH units G1-G7, %: pandapower table + fast-solver Ybus (no rebuild needed).
    Portugal's unit and the pump stations keep the continuation value (S28: the knob on G8 fought the PT reactive terms)."""
    if abs(v - VKG[0]) < 1e-12: return
    TVK = [i_ for i_ in TV if net.trafo.at[i_, "name"].split()[1] in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")]
    if FP is not None: FP.set_trafo_vk(TVK, v)
    for i_ in TVK: net.trafo.at[i_, "vk_percent"] = v
    VKG[0] = v


TRIPV = []


def trip_dv():
    """Static dV (kV) at GRA for E3 (Granada 355 MW) and at BAD-TS for 4a+4b (727 MW) alone; state restored after."""
    ig, ib = RESI["GRA"], RESTS_I["BAD"]; keep = net.sgen.loc[[ig, ib], ["p_mw", "q_mvar"]].values.copy()
    Vk = FP.V.copy() if FP is not None else None; v0 = net.res_bus.vm_pu.values.copy()
    try:
        net.sgen.at[ig, "p_mw"] -= 355; net.sgen.at[ig, "q_mvar"] -= a.kpf * 355; solve(full=True); v3 = net.res_bus.vm_pu.values.copy()
        net.sgen.at[ib, "p_mw"] -= 727; net.sgen.at[ib, "q_mvar"] -= a.kpf * 727; solve(full=True); v4 = net.res_bus.vm_pu.values.copy()
    finally:
        net.sgen.loc[[ig, ib], ["p_mw", "q_mvar"]] = keep
        if Vk is not None: FP.V = Vk
        solve(full=True)
    TRIPV[:] = [v0, v3, v4]                                  # kept for the system-maximum check (S29 sec 10)
    return 400 * (v3[B["GRA"]] - v0[B["GRA"]]), 400 * (v4[B["BAD-TS"]] - v3[B["BAD-TS"]])


PTSPLIT = os.environ.get("PTSPLIT", "0") == "1"             # knob: Portuguese load north share; target North -> PT 200 MW (S28)
# FLOW2=1: the remaining Fig 2-4 corridor checks become soft targets (/100 MW), each with one area-preserving shift knob
# [liberty, user OK S27: distribution inside an area may move, totals faithful] (RUNLOG S29 sec 7):
#   fbad: zone RES BAD hub -> WAN hub      (BAD->CAC 1,850; the Table 3-3 plants at BAD-TS stay fixed)
#   fse : demand SE -> CAT (East area)     (GRA->SE 900)
#   fcac: zone RES CAC -> SCE              (CAC->CYL 1,200)
FLOW2 = os.environ.get("FLOW2", "0") == "1"
F2 = {"fbad": 0.0, "fse": 0.0, "fcac": 0.0}                 # GW
F2T = {"fbad": (("BAD", "CAC"), 1850), "fse": (("GRA", "SE"), 900), "fcac": (("CAC", "CYL"), 1200)}
RESP0 = {z: net.sgen.at[RESI[z], "p_mw"] for z in ("BAD", "WAN", "CAC", "SCE")}
P0_SE0, P0_CAT0 = P0["SE"], P0["CAT"]
# DISPATCH=1: zero-sum net-injection shifts between the zones of each Fig 2-41 area (area totals unchanged) [liberty, user OK
# S27], realised as RES moved between zones (P + fixed-PF Q), weakly penalised (1 per 0.5 GW). Targets: the Fig 2-4 split of
# the Portuguese border between its ties, scaled to the 2,100 MW total (RUNLOG S29 sec 9). The last zone of each group takes
# minus the sum of the others.
DISPATCH = os.environ.get("DISPATCH", "0") == "1"
DSP_PTSPLIT = os.environ.get("DSP_PTSPLIT", "1") == "1"     # 0: the Fig 2-4 PT tie split is a check only (S29 sec 10)
DSP_W = float(os.environ.get("DSP_W", 0.5))                  # GW per unit of shift penalty
DGRP = [["WAN", "GRA", "SCE", "BAD", "CAC", "MAD"], ["VAL", "SE", "CAT"], ["CYL", "NW", "N", "ARA"]]
DKN = [z for g in DGRP for z in g[:-1]]                     # 10 free knobs (GW)
DSH = {z: 0.0 for g in DGRP for z in g}
DSG = {z: pp.create_sgen(net, B[z], p_mw=0.0, q_mvar=0.0, name=f"DSP {z}") for g in DGRP for z in g} if DISPATCH else {}
# Fig 2-4 ties to Portugal at 12:32 [read]: Cartelle-Lindoso 102, Aldeadavila-Lagoaca 652, Cedillo-Falagueira 1,124,
# Brovales-Alqueva ~131 (label unclear), P.Guzman-Tavira 772 -> shares of 2,781, applied to the 2,100 MW target
PTSH = {("NW", "PT-N"): 102, ("CYL", "PT-N"): 652, ("CAC", "PT-S"): 1124, ("BAD", "PT-S"): 131, ("WAN", "PT-S"): 772}
PTSH = {k: 2100 * v / sum(PTSH.values()) for k, v in PTSH.items()}


def set_dsp(vals):
    for z, v in zip(DKN, vals): DSH[z] = float(v)
    for g in DGRP: DSH[g[-1]] = -sum(DSH[z] for z in g[:-1])
    for z, i_ in DSG.items(): net.sgen.at[i_, "p_mw"] = 1000 * DSH[z]; net.sgen.at[i_, "q_mvar"] = a.kpf * 1000 * DSH[z]


def set_f2(fb, fs, fc):
    global P0_SE0, P0_CAT0
    net.sgen.at[RESI["BAD"], "p_mw"] = RESP0["BAD"] - 1000 * fb; net.sgen.at[RESI["WAN"], "p_mw"] = RESP0["WAN"] + 1000 * fb
    net.sgen.at[RESI["CAC"], "p_mw"] = RESP0["CAC"] - 1000 * fc; net.sgen.at[RESI["SCE"], "p_mw"] = RESP0["SCE"] + 1000 * fc
    for z in ("BAD", "WAN", "CAC", "SCE"): net.sgen.at[RESI[z], "q_mvar"] = a.kpf * net.sgen.at[RESI[z], "p_mw"]
    P0["SE"] = P0_SE0 - 1000 * fs; P0["CAT"] = P0_CAT0 + 1000 * fs
    Q0["SE"] = a.q0 * P0["SE"]; Q0["CAT"] = a.q0 * P0["CAT"]
    F2.update(fbad=fb, fse=fs, fcac=fc)


def getx():
    return np.concatenate([[net.shunt.at[CAL[z], "q_mvar"] / 1000 for z in KZ], [net.gen.at[GI[n], "vm_pu"] for n in KG],
                           [scale.get("GRA", 1), scale.get("PT-N", 1), net.ext_grid.at[0, "vm_pu"], net.gen.at[iMA, "vm_pu"],
                            (P0["MAD"] - P0_MAD0) / 1000, net.gen.at[iMA, "p_mw"] / 1000]] + ([[P0["PT-N"] / PT_LOAD]] if PTSPLIT else []) + ([[F2["fbad"], F2["fse"], F2["fcac"]]] if FLOW2 else []) + ([[DSH[z] for z in DKN]] if DISPATCH else []) + ([[VKG[0] / 100]] if KNOB_VKG else []))


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
    if PTSPLIT and len(x) > k + 6:                                                   # Portuguese load north share (S28)
        P0["PT-N"] = PT_LOAD * x[k + 6]; P0["PT-S"] = PT_LOAD * (1 - x[k + 6])
        Q0["PT-N"] = a.q0 * P0["PT-N"]; Q0["PT-S"] = a.q0 * P0["PT-S"]
    if FLOW2:
        j_ = k + 6 + (1 if PTSPLIT else 0)
        if len(x) >= j_ + 3: set_f2(x[j_], x[j_ + 1], x[j_ + 2])
    if DISPATCH:
        j_ = k + 6 + (1 if PTSPLIT else 0) + (3 if FLOW2 else 0)
        if len(x) >= j_ + len(DKN): set_dsp(x[j_:j_ + len(DKN)])
    if KNOB_VKG: set_vkg(100 * x[-1])



UNITQ_HV = os.environ.get("UNITQ_HV", "0") == "1"   # compare unit Q at the 400 kV side of the step-up ([FR] Figs 2-84..86 are
                                                    # defined on the 400 kV band -> connection point [inf]); RUNLOG S29 sec 6
def unitq():
    """Unit Q per name (Mvar): terminal Q, or with UNITQ_HV the Q delivered into the 400 kV bus (terminal Q - step-up I2X)."""
    q = dict(zip(net.gen.name, net.res_gen.q_mvar))
    if UNITQ_HV:
        vt = dict(zip(net.gen.name, net.res_gen.vm_pu)); pg = dict(zip(net.gen.name, net.res_gen.p_mw))
        for i_, tn in zip(net.trafo.index, net.trafo.name):
            g = tn[2:]
            if tn.startswith("T ") and g in q and g in vt:
                q[g] -= (pg[g] ** 2 + q[g] ** 2) / max(vt[g], 0.5) ** 2 * net.trafo.at[i_, "vk_percent"] / 100 / net.trafo.at[i_, "sn_mva"]
    return q

def resid(x):
    CNT["resid"] += 1
    setx(x)
    try:
        solve(full=True)
    except Exception as ex_:
        if os.environ.get("LSDBG"): print("  resid exception:", type(ex_).__name__, str(ex_)[:120], flush=True)
        net.converged = False; return np.full(NRES, 50.0)
    V = net.res_bus.vm_pu; qg = unitq()
    r = [400 * (V[B[VB(z)]] - VT[z] / 400) for z in VT]                                       # kV
    r += [(sum(qg[n] for n, ar in GEN_AREA.items() if ar == A) - t) / 50 for A, t in QAREA.items()]    # 50 Mvar ~ 1 kV
    pt = sum(flow(z, {"PT-N", "PT-S"}) for z in ES); fr = sum(flow(z, {"FR"}) for z in ES) + HVDC_FR
    ma = flow("WAN", {"MA-B"})
    r += [(pt - 2100) / 50, (fr - FR_T) / 50, (ma - 750) / 50, (flow("N", {"FR"}) - 310) / 50]   # west tie: Fig 2-41 North->France 310
    qfr = sum(qflow(z, {"FR"}) for z in ES); qma = qflow("WAN", {"MA-B"}); qpt = sum(qflow(z, {"PT-N", "PT-S"}) for z in ES)
    r += [(-(qg["G1 Almaraz II"] + qg["G6 SW CCGT"] + qg["G7 E CCGT"]) - 74) / 50]   # Fig 4-2: PO 7.4 units, South Spain, 74 Mvar absorbed
    r += [(qfr - QTIE["FR"]) / 50, (qma - QTIE["MA"]) / 50, (qpt - 100) / 50]          # ES->PT tie Q now a target (Fig 2-93)
    if a.flowcal: r += [(flow("CAC", {"MAD"}) - FLOWT[("CAC", "MAD")]) / float(os.environ.get("MADW", 50))]   # MADW: weight (MW per unit)
    if float(os.environ.get("MADREG", 0)) > 0: r += [float(os.environ["MADREG"]) * (P0["MAD"] - P0_MAD0) / 1000]   # penalty per GW of Madrid shift (S29 sec 8)
    if FLOW2: r += [(flow(k_[0], {k_[1]}) - t_) / 100 for k_, t_ in F2T.values()]
    if DISPATCH:
        if DSP_PTSPLIT: r += [(flow(za_, {zb_}) - t_) / (200 if za_ == "BAD" else 100) for (za_, zb_), t_ in PTSH.items()]   # Fig 2-4 PT tie split
        else: r += [0.0] * len(PTSH)
        r += [DSH[z] / DSP_W for z in DSH]                                                                # 1 per DSP_W GW moved
    if PTSPLIT: r += [(flow("NW", {"PT-N"}) + flow("CYL", {"PT-N"}) - 200) / 50]       # Fig 2-41 exact: North -> Portugal 200 MW
    if OBJ2:                                                 # identifiability terms (S28): pin the null directions found by SVD=1
        for A, t in QAREA.items():                           # each unit's share of its area's Q, by |P| (as the S27 one-knob loop)
            nm_ = [n for n, ar in GEN_AREA.items() if ar == A]; tp = sum(abs(net.gen.at[GI[n], "p_mw"]) for n in nm_)
            r += [(qg[n] - t * abs(net.gen.at[GI[n], "p_mw"]) / tp) / 100 for n in nm_]
        vv = net.res_bus.vm_pu.values
        qex = {z: net.load.at[L[z], "q_mvar"] + net.shunt.at[CAL[z], "q_mvar"] * vv[B[z]] ** 2 for z in CAL}   # load + DSO shunt, Mvar
        pz = {z: net.load.at[L[z], "p_mw"] for z in CAL}; pes = sum(pz[z] for z in ES)
        r += [(sum(qex[z] for z in ES) - QEX_T) / 500]                                          # Fig 4-84 scaled [inf]
        r += [(qex[z] - pz[z] * QEX_T / pes) / 300 for z in CAL]                                 # exchange ~ demand, per zone [inf]
        r += [qg["G8 PT conventional"] / 300]                                                    # Portuguese unit: no data -> near 0 [inf]
    if TRIPCAL:
        if KNOB_VKG: d3, d4 = trip_dv(); r += [(d4 - TRIP_T["E4"]) / 1.0, (d3 - TRIP_T["E3"]) / 0.5]   # kV; Granada band 0.86-2.0 kV
        else: r += [0.0, 0.0]
    r += list(0.02 * (x[:len(KZ)]))                                                          # mild preference for small shunts
    return np.array(r)


P0_MAD0, P0_WAN0 = P0["MAD"], P0["WAN"]
NRES = len(VT) + len(QAREA) + 8 + (1 if a.flowcal else 0) + (1 if float(os.environ.get('MADREG', 0)) > 0 else 0) + len(KZ) + (1 if PTSPLIT else 0) + (2 if TRIPCAL else 0) + (3 if FLOW2 else 0) + ((len(PTSH) + len(DSH)) if DISPATCH else 0) + ((len(GEN_AREA) + 1 + len(CAL) + 1) if OBJ2 else 0)


def calib_ls(tag=""):
    x0 = getx()
    lo = np.concatenate([np.full(len(KZ), -6.0), np.full(len(KG), 0.85), [0.7, 0.5, 0.9, 0.85, -1.5, 3.0]] + ([[0.45]] if PTSPLIT else []) + ([[-1.0, -1.5, -1.5]] if FLOW2 else []) + ([[-1.5] * len(DKN)] if DISPATCH else []) + ([[0.03]] if KNOB_VKG else []))
    hi = np.concatenate([np.full(len(KZ), 6.0), np.full(len(KG), 1.15), [1.3, 1.5, 1.1, 1.15, 1.5, 6.0]] + ([[0.70]] if PTSPLIT else []) + ([[1.0, 1.5, 1.5]] if FLOW2 else []) + ([[1.5] * len(DKN)] if DISPATCH else []) + ([[0.25]] if KNOB_VKG else []))
    x0 = np.clip(x0, lo + 1e-6, hi - 1e-6)
    if os.environ.get("RESDUMP"):                           # print the residual groups at the start and the end
        RD_ = lambda r_: f"V {np.sum(r_[:len(VT)]**2):.1f} | other {np.sum(r_[len(VT):]**2):.1f}"
    c0 = dict(CNT); t0 = time.perf_counter()
    # frozen knobs are taken OUT of the optimisation (a knob squeezed between near-equal bounds, or one resting on a
    # bound, made trf stop after 2-3 evaluations: S29 sec 8). MADFIX=1 freezes the Madrid demand shift at 0.
    free = np.ones(len(x0), bool)
    if os.environ.get("MADFIX") == "1":
        im_ = len(KZ) + len(KG) + 4; x0[im_] = 0.0; free[im_] = False
    def _fill(xf):
        xx = x0.copy(); xx[free] = xf; return xx
    tol_ = float(os.environ.get("LSTOL", 1e-8))
    if os.environ.get("LSPROBE"):
        r0_ = resid(_fill(x0[free]))
        for j_, nm_ in ((0, "shunt GRA +0.1 Gvar"), (len(KZ), "vm G1 +0.005")):
            xp_ = x0.copy(); xp_[j_] += 0.1 if j_ == 0 else 0.005; r1_ = resid(xp_)
            print(f"  PROBE {nm_}: |dr| {np.abs(r1_ - r0_).max():.4g}, V GRA {400 * net.res_bus.vm_pu[B['GRA']]:.2f} kV, FAST {FP is not None}", flush=True)
        xf0_ = x0[free].copy(); r0_ = resid(_fill(xf0_)); g_ = np.zeros(len(xf0_)); J_ = []
        for j_ in range(len(xf0_)):
            h_ = 1e-3 * max(1.0, abs(xf0_[j_])); xp_ = xf0_.copy(); xp_[j_] += h_; J_.append((resid(_fill(xp_)) - r0_) / h_)
        J_ = np.array(J_).T; g_ = J_.T @ r0_
        print(f"  PROBE manual: |r| {np.linalg.norm(r0_):.3g}, |J^T r| {np.abs(g_).max():.3g} (knob {int(np.argmax(np.abs(g_)))}), "
              f"rank J {np.linalg.matrix_rank(J_, 1e-6)} of {len(xf0_)}; r0 repeat diff {np.abs(resid(_fill(xf0_)) - r0_).max():.2e}", flush=True)
        resid(x0)
    sol = least_squares(lambda xf: resid(_fill(xf)), x0[free], bounds=(lo[free], hi[free]), x_scale=("jac" if os.environ.get("LSXS", "jac") == "jac" else 1.0), method=os.environ.get("LSMETHOD", "trf"),
                        diff_step=float(os.environ.get("DSTEP", 1e-3)), max_nfev=int(os.environ.get("LSNFEV", 400)), xtol=tol_, ftol=tol_, gtol=tol_)
    xs = _fill(sol.x); setx(xs); solve(full=True)
    if os.environ.get("LSDBG"): print(f"  least_squares status {sol.status}: {sol.message}; free knobs {int(free.sum())}; |grad| {np.abs(sol.grad).max():.3g}; active {np.flatnonzero(sol.active_mask).tolist()}", flush=True)
    r = resid(xs)
    print(f"  {tag} least_squares: nfev {sol.nfev}, max |V err| {np.abs(r[:len(VT)]).max():.2f} kV, "
          f"max other err {np.abs(r[len(VT):len(VT) + len(QAREA) + 9]).max() * 50:.0f} (MW/Mvar) | njev {sol.njev}, "
          f"resid calls {CNT['resid'] - c0['resid']}, load flows {CNT['runpp'] - c0['runpp']} "
          f"({CNT['t_pf'] - c0['t_pf']:.1f} s of {time.perf_counter() - t0:.1f} s wall), cost {sol.cost:.2f}", flush=True)
    return sol.nfev


# continuation: calibrate at physical settings (corridor X x1, unit connection 15 %), then step to the fitted
# fault-level settings (--xk, --vkg), re-calibrating at each step from the previous solution (RUNLOG S27 sec 31)
LX = net.line.x_ohm_per_km.copy(); XK1 = {i_: (1.0 if n == "WAN-MA-B" else a.xk) for i_, n in zip(net.line.index, net.line.name)}   # the cable is not scaled
TV = {i_: net.trafo.at[i_, "vk_percent"] for i_ in net.trafo.index if net.trafo.at[i_, "name"].startswith("T ") and net.trafo.at[i_, "vk_percent"] == a.vkg}
RESUME = os.environ.get("RESUME") and os.path.exists(STATE)
if RESUME and not a.quick:                                # start from the saved solved state (full lengths, full unit-X)
    import pickle; st = pickle.load(open(STATE, "rb"))
    P0.update(st["P0"]); Q0.update(st["Q0"]); x_ = st["x"]
    d_ = 1000 * x_[len(KZ) + len(KG) + 4]                                      # the Madrid knob (NOT x[-1]: that is the Morocco P knob)
    P0_MAD0, P0_WAN0 = P0["MAD"] - d_, P0["WAN"] + d_                          # saved P0 already holds the Madrid shift
    NB_ = len(KZ) + len(KG) + 5                                                    # knobs up to the Madrid knob
    tail = dict(zip(st.get("xnames", ["mor", "pt"][:len(x_) - NB_]), x_[NB_:]))       # older states: Morocco P, then PT share
    if "vkg" in tail or st.get("vkg"): set_vkg(100 * tail.get("vkg", st.get("vkg", a.vkg) / 100))
    if os.environ.get("VKG"): set_vkg(float(os.environ["VKG"]))   # force the Spanish unit connection X (%) on resume (S29 sec 10)
    if TRIPCAL: KNOB_VKG = True
    if FLOW2:
        P0_SE0, P0_CAT0 = P0["SE"] + 1000 * tail.get("fse", 0.0), P0["CAT"] - 1000 * tail.get("fse", 0.0)
    x_ = np.concatenate([x_[:NB_], [tail.get("mor", net.gen.at[iMA, "p_mw"] / 1000)]] + ([[tail.get("pt", 0.5)]] if PTSPLIT else [])
                        + ([[tail.get("fbad", 0.0), tail.get("fse", 0.0), tail.get("fcac", 0.0)]] if FLOW2 else [])
                        + ([[tail.get(f"d_{z}", 0.0) for z in DKN]] if DISPATCH else [])
                        + ([[VKG[0] / 100]] if KNOB_VKG else []))
    setx(x_)
    import pandas as pd                                     # warm start from the saved solved voltages
    net.res_bus = pd.DataFrame({"vm_pu": st["vm"], "va_degree": st["va"], "p_mw": 0.0, "q_mvar": 0.0}, index=net.bus.index)
    net.converged = True
    solve(full=True); print("resumed from pp_v2_state.pkl", flush=True)
    NR += calib_ls("resume-final")
    import pickle; pickle.dump({"x": getx(), "xnames": XNAMES(), "vkg": VKG[0], "P0": P0, "Q0": Q0, "vm": net.res_bus.vm_pu.values, "va": net.res_bus.va_degree.values}, open(STATE, "wb"))
elif not a.quick:
    HUB_KM = {i_: net.line.at[i_, "length_km"] for i_ in net.line.index}
    OSMI = {i_: OSM_KM.get(tuple(net.line.at[i_, "name"].split("-", 1)) if net.line.at[i_, "name"].count("-") == 1 else None, HUB_KM[i_])
            for i_ in net.line.index}
    for i_, n in zip(net.line.index, net.line.name):        # PT ties: names like "CAC-PT-N"
        za = n.split("-")[0]; zb = n[len(za) + 1:]
        OSMI[i_] = OSM_KM.get((za, zb), OSM_KM.get((zb, za), HUB_KM[i_])) if (za, zb) in OSM_KM or (zb, za) in OSM_KM else HUB_KM[i_]
    if CORR_X_FIT: OSMI = dict(HUB_KM)                    # fitted reactances: no length continuation, lengths fixed (S29 sec 8)
    def setstep(fl, fv):
        for i_ in net.line.index:
            net.line.at[i_, "length_km"] = OSMI[i_] + (HUB_KM[i_] - OSMI[i_]) * fl
            k_ = XK1[i_]; net.line.at[i_, "x_ohm_per_km"] = LX[i_] / k_ * (1 + (k_ - 1) * fv)
            if i_ in CTOT: net.line.at[i_, "c_nf_per_km"] = CTOT[i_] / (net.line.at[i_, "length_km"] * net.line.at[i_, "parallel"])
        for i_ in TV: net.trafo.at[i_, "vk_percent"] = 15 + (a.vkg - 15) * fv
        VKG[0] = 15 + (a.vkg - 15) * fv
        if FP is not None: FP.rebuild()
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
    if TRIPCAL: KNOB_VKG = True                              # trip gate + vkg knob in the final fit only
    NR += calib_ls("final"); print(f"  final calibration: total evaluations {NR}", flush=True)
    import pickle; pickle.dump({"x": getx(), "xnames": XNAMES(), "vkg": VKG[0], "P0": P0, "Q0": Q0, "vm": net.res_bus.vm_pu.values, "va": net.res_bus.va_degree.values}, open(STATE, "wb"))
outer = NR
if os.environ.get("SVD") == "1":                            # identifiability: SVD of the residual Jacobian at the final state (S28)
    x_ = getx(); r_ = resid(x_); h_ = 1e-4; Jm = np.zeros((len(r_), len(x_)))
    for j_ in range(len(x_)):
        xp = x_.copy(); xp[j_] += h_; Jm[:, j_] = (resid(xp) - r_) / h_
    resid(x_); Js = Jm[:-len(KZ)]   # without the shunt regulariser rows
    KN = [f"dso {z}" for z in KZ] + [f"vm {n.split()[0]}" for n in KG] + ["dem ES", "dem PT", "V FR", "V MA", "MAD shift", "P MA"] + XNAMES()[1:]
    cs = np.linalg.norm(Js, axis=0); U_, sv, Vt = np.linalg.svd(Js / np.where(cs > 0, cs, 1), full_matrices=False)
    print(f"Jacobian (targets only, columns normalised): {Js.shape}, cond {sv[0] / sv[-1]:.1e}; smallest singular values:")
    for k_ in range(1, 6):
        v_ = Vt[-k_]; top = np.argsort(-np.abs(v_))[:4]
        print(f"   s = {sv[-k_]:.2e}: " + "  ".join(f"{v_[t]:+.2f} {KN[t]}" for t in top))
if FAST and FP is not None:                                 # final state through pandapower itself (all res_* tables), cross-checked
    vf = net.res_bus.vm_pu.values.copy(); qf = net.res_gen.q_mvar.values.copy(); FAST = False
    pp.runpp(net, init="results")
    print(f"fastpf vs pandapower at the final state: max dV {np.abs(vf - net.res_bus.vm_pu.values).max():.1e} pu, "
          f"max d gen Q {np.abs(qf - net.res_gen.q_mvar.values).max():.1e} Mvar; total load flows {CNT['runpp']} in {CNT['t_pf']:.1f} s, fallbacks {CNT.get('fallback', 0)}")
if os.environ.get("DRIFTCHK", "1") == "1":                 # static 12:32:00 -> 12:32:57 drift check (RUNLOG S29 sec 11)
    # drivers, imposed statically: RES set-point down-ramp ~270 MW ([CA] p.88: 480 MW observable RES incl. the 208 MW of
    # trips), trips 2a north / 2b south 104 + 104 MW [inf split] ([FR] p.122), +317 MW net load from lost rooftop PV
    # (event 1, [FR] p.122; emergent in PSCAD, imposed here) spread with demand. Report response: France export -1,030 MW,
    # Olmedilla (VAL) 413 -> 428 kV, S.Servan (BAD) 411 -> 424 kV ([CA] p.39, p.87-88), 400 kV max 421.8 kV at 12:32:57 (Fig 3-7a).
    NOR_, SOU_ = {"CYL", "NW", "N", "ARA", "CAT"}, {"WAN", "GRA", "SCE", "BAD", "CAC"}
    ires_ = [i_ for i_, n in zip(net.sgen.index, net.sgen.name) if n.startswith("RES") and n.split()[-1] in ES]
    keep_s = net.sgen.loc[ires_, ["p_mw", "q_mvar"]].copy(); keep_p = dict(P0); Vk_ = FP.V.copy() if FP is not None else None
    keep_vm = net.gen.vm_pu.copy(); Q_U0 = [net.res_gen.at[GI[n], "q_mvar"] for n in ("G1 Almaraz II", "G2 Cat nuclear A", "G3 Cat nuclear B", "G4 N thermal", "G5 N hydro", "G6 SW CCGT", "G7 E CCGT")]
    v0_ = net.res_bus.vm_pu.values.copy()
    def xfer():
        return (sum(flow(z, {"FR"}) for z in ES) + HVDC_FR, sum(flow(z, {"PT-N", "PT-S"}) for z in ES), flow("WAN", {"MA-B"}))
    f0_ = xfer(); tot_ = net.sgen.loc[ires_, "p_mw"].sum()
    for i_ in ires_:
        z = net.sgen.at[i_, "name"].split()[-1]; p = net.sgen.at[i_, "p_mw"]
        zt = sum(net.sgen.at[j, "p_mw"] for j in ires_ if net.sgen.at[j, "name"].split()[-1] in (NOR_ if z in NOR_ else SOU_))
        cut = 270 * p / tot_ + (104 * p / zt if z in NOR_ | SOU_ else 0)
        net.sgen.at[i_, "p_mw"] = p - cut; net.sgen.at[i_, "q_mvar"] = a.kpf * (p - cut)
    pes_ = sum(P0[z] for z in ES)
    for z in ES: P0[z] += 317 * keep_p[z] / pes_
    solve(full=True)
    if os.environ.get("DRIFT_QHOLD", "0") == "1":           # units keep their 12:32:00 Q (no AVR action), the report's
        GU_ = [GI[n] for n in ("G1 Almaraz II", "G2 Cat nuclear A", "G3 Cat nuclear B", "G4 N thermal", "G5 N hydro", "G6 SW CCGT", "G7 E CCGT")]
        q00_ = {i_: q for i_, q in zip(GU_, Q_U0)}          # "insufficient absorption / flat Q" ([CA] p.111-112) as a bound
        KD_ = float(os.environ.get("DRIFT_DROOP", 0))       # Mvar/kV per GW of unit P: Q = Q0 - KD * P/1000 * dV(400 kV side)
        hv_ = {i_: B[GEN_ZONE[n]] for n, i_ in GI.items() if i_ in GU_}; vh0_ = {i_: v0_[hv_[i_]] for i_ in GU_}
        for it_ in range(200):
            tq_ = {i_: q00_[i_] - KD_ * abs(net.gen.at[i_, "p_mw"]) / 1000 * 400 * (net.res_bus.vm_pu[hv_[i_]] - vh0_[i_]) for i_ in GU_}
            dq_ = {i_: net.res_gen.at[i_, "q_mvar"] - tq_[i_] for i_ in GU_}
            if max(abs(v) for v in dq_.values()) < 1.0: break
            for i_ in GU_: net.gen.at[i_, "vm_pu"] -= float(np.clip(dq_[i_] / 8000.0, -0.003, 0.003))   # absorbing more (dq<0) -> raise set-point
            solve(full=True)
        print(f"   DRIFT_QHOLD (droop {KD_} Mvar/kV per GW): unit Q law met after {it_ + 1} iterations (max dQ {max(abs(v) for v in dq_.values()):.1f} Mvar)")
    v1_ = net.res_bus.vm_pu.values.copy(); f1_ = xfer()
    SPB_ = [B[z] for z in ES] + [B[f"{z}-TS"] for z in TSX]; nmb_ = {B[z]: z for z in ES}; nmb_.update({B[f"{z}-TS"]: f"{z}-TS" for z in TSX})
    m0_, m1_ = max(SPB_, key=lambda b: v0_[b]), max(SPB_, key=lambda b: v1_[b])
    print(f"drift check 12:32:00->57 (static): France export {f0_[0]:.0f} -> {f1_[0]:.0f} ({f1_[0] - f0_[0]:+.0f}; report -1,030), "
          f"PT {f1_[1] - f0_[1]:+.0f}, MA {f1_[2] - f0_[2]:+.0f} MW | VAL (Olmedilla) {400 * (v1_[B['VAL']] - v0_[B['VAL']]):+.1f} kV (report +15), "
          f"BAD-TS (S.Servan) {400 * (v1_[B['BAD-TS']] - v0_[B['BAD-TS']]):+.1f} kV (report +13) | max {400 * v0_[m0_]:.1f} at {nmb_[m0_]} -> "
          f"{400 * v1_[m1_]:.1f} at {nmb_[m1_]} (report 421.8 at 12:32:57)")
    print("   zone dV: " + "  ".join(f"{nmb_[b]} {400 * (v1_[b] - v0_[b]):+.1f}" for b in SPB_))
    net.sgen.loc[ires_, ["p_mw", "q_mvar"]] = keep_s.values; P0.update(keep_p)
    net.gen.vm_pu = keep_vm
    if Vk_ is not None: FP.V = Vk_
    solve(full=True)
if TRIPCAL or os.environ.get("TRIPCHK", "1") == "1":
    d3, d4 = trip_dv(); print(f"trip gate: 4a+4b at BAD-TS {d4:+.2f} kV (target {TRIP_T['E4']}), Granada at GRA {d3:+.2f} kV "
                              f"= {d3 / (-a.kpf * 355) * 1000:.0f} kV/Gvar (report 18-42); unit connection X {VKG[0]:.2f} %")
    SPB_ = [B[z] for z in ES] + [B[f"{z}-TS"] for z in TSX]; nm_ = {B[z]: z for z in ES}; nm_.update({B[f"{z}-TS"]: f"{z}-TS" for z in TSX})
    mx_ = [max(SPB_, key=lambda b: v[b]) for v in TRIPV]
    print("trip gate, like Fig 3-7a (maximum Spanish 400 kV voltage): " + " -> ".join(f"{400 * v[b]:.1f} kV at {nm_[b]}" for v, b in zip(TRIPV, mx_))
          + f" | rise over 4a+4b {400 * (TRIPV[2][mx_[2]] - TRIPV[1][mx_[1]]):+.2f} kV (report +4.9: 427.8 -> 432.7)")
it = solve(full=True)
print(f"calibration pass 3: {outer} rounds; Portuguese load x{scale.get('PT-N', 1):.3f}, Spanish demand x{scale.get('GRA', 1):.3f}")
print("DSO shunts at 1 pu (Mvar, + absorbing): " + "  ".join(f"{z} {net.shunt.at[CAL[z], 'q_mvar']:+.0f}" for z in CAL))
qg = unitq()
print(("unit Q at 400 kV" if UNITQ_HV else "unit Q") + " per area: " + "  ".join(f"{A} {sum(qg[n] for n, ar in GEN_AREA.items() if ar == A):+.0f} (target {t:+d})" for A, t in QAREA.items()))
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
print("   Portugal ties ES->PT: " + "  ".join(f"{z} {flow(z, {'PT-N', 'PT-S'}):+.0f}" for z in ES if abs(flow(z, {'PT-N', 'PT-S'})) > 0.5) +
      f" | North area -> PT {flow('NW', {'PT-N'}) + flow('CYL', {'PT-N'}):+.0f} (Fig 2-41: +200) | PT load north share {P0['PT-N'] / (P0['PT-N'] + P0['PT-S']):.2f}")
sw_mad = flow("CAC", {"MAD"}) + flow("SCE", {"MAD"})
print("corridor flows vs Fig 2-4: " + "  ".join(f"{k[0]}->{k[1]} {flow(k[0], {k[1]}):+.0f} ({t})" for k, t in {**FLOWT, **FCHK}.items()))
print("zone demand now: " + "  ".join(f"{z} {P0[z] * scale.get(z, 1):.0f}" for z in ES))
if DISPATCH:
    print("dispatch shifts (MW, + = more net injection): " + "  ".join(f"{z} {1000 * DSH[z]:+.0f}" for z in DSH))
    print("PT ties vs Fig 2-4 split: " + "  ".join(f"{a_}->{b_} {flow(a_, {b_}):+.0f} ({t_:.0f})" for (a_, b_), t_ in PTSH.items()))
print("zone RES now:    " + "  ".join(f"{z} {net.sgen.at[RESI[z], 'p_mw']:.0f}" for z in ES if z in RESI))
print(f"Madrid net in-feed {mad_in:6.0f} MW; SW corridor CAC+SCE -> MAD {sw_mad:6.0f} MW (Fig 2-4: 3,227 on the six circuits)")
print("generator Q [Mvar]: " + "  ".join(f"{n.split()[0]} {q:+.0f}" for n, q in zip(net.gen.name, net.res_gen.q_mvar)))
print(f"France slack P {net.res_ext_grid.p_mw.iloc[0]:+.0f} MW, Q {net.res_ext_grid.q_mvar.iloc[0]:+.0f} Mvar")
qt = {"FR": sum(qflow(z, {"FR"}) for z in ES), "PT": sum(qflow(z, {"PT-N", "PT-S"}) for z in ES), "MA": qflow("WAN", {"MA-B"})}
if qt: print("tie Q ES->X: " + "  ".join(f"{k} {v:+.0f} (target {QTIE.get(k, 100):+d})" for k, v in qt.items()) +
      f" | set-points FR {net.ext_grid.at[0, 'vm_pu'] * 400:.1f} kV, MA {net.gen.at[iMA, 'vm_pu'] * 400:.1f} kV, PT {net.gen.at[iPT, 'vm_pu'] * 400:.1f} kV")
if os.environ.get("QBAL", "1") == "1":                      # reactive-power balance by source (RUNLOG S27 sec 35)
    import pandas as pd; qg_ = unitq()
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
if os.environ.get("DUMP_NET"):                              # solved net for offline diagnostics (pp_v2_diag.py)
    pp.to_pickle(net, os.environ["DUMP_NET"]); print("net saved to", os.environ["DUMP_NET"])
