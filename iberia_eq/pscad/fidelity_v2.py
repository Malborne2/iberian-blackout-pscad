r"""Fidelity of a v2 replay run against the ENTSO-E Final Report [FR] (S30 sec 20).

usage: python iberia_eq\pscad\fidelity_v2.py <tag> [--t0 30] [--build build_v2sld_r.out]
Report clock: report time tr = model time - t0 (s after 12:32:00).

Report data (digitised earlier, RUNLOG stage 0 sec 3; t in s after 12:32:00):
  data/targets_fig1-10.csv  Carmona 400 kV voltage, Iberian + CE frequency (50-95 s)
  data/targets_fig3-5.csv   Carmona voltage, Spain net exchange (-4-64 s)
  data/targets_fig3-7a.csv  accumulated generation loss + net load increase, 400 kV maximum (0-80 s)
  data/targets_fig4-89/90/91.csv  frequency, voltage, Spain-France P: [FR] simulation and PMU (76-83 s)
  data/events.csv           Table 3-1 event list (time, type, MW)
  [CA] p.104/105 France export points; [CA] p.57 defence-plan threshold crossings (SOURCES sec 12.5)
Model signals: PMU (pmu.py, 3-cycle) of the bus voltages; machine speeds; RES plant TRIP channels (instances matched to
the named plants by rating: amplitude(IsrcA)/ID is proportional to Sbase); M_ES/M_PT (LFDD), BRKM1/BRKM3/BRKMA, pump
POUT; France multimeter PFR.

Metrics, per phase (P0 0-57.2 s pre-event, P1 57.2-76.4 s between events 3 and 4a, P2 76.4-79.6 s cascade 4a-8b,
P3 79.6-84 s collapse):
  signals: bias, RMSE, max |error|, Pearson r (on the report's sample times);
  sequence: matched events (report <-> model), timing error, order agreement (Kendall tau), MW;
  milestones: first trip, 49.5 / 49.0 / 48.0 Hz crossings, minimum f, RoCoF, peak V, France AC import peak.
Outputs: iberia_eq\pscad\figs\fid_<tag>_{overview,sequence,collapse,score}.png and iberia_eq\pscad\fid_<tag>.md (tables).
"""
import argparse, csv, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legacy_out import load
from pmu import pmu
from scipy.optimize import linear_sum_assignment
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); DATA = os.path.join(ROOT, "data")
ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("--t0", type=float, default=30.0)
ap.add_argument("--build", default="build_v2sld_r.out"); a = ap.parse_args()
plt.style.use("seaborn-v0_8-whitegrid")
CM, CR, CS = "#1f5fbf", "#111111", "#c0392b"            # model, report, report-simulation
PH = [("P0 pre-event", 0, 57.22), ("P1 slow rise", 57.22, 76.443), ("P2 cascade", 76.443, 79.62), ("P3 collapse", 79.62, 84.0)]
PHC = ["#f4f6f8", "#fdf3e1", "#fde3d9", "#f6d5e6"]
md = open(os.path.join(HERE, f"fid_{a.tag}.md"), "w", encoding="utf-8")
def M(*x): print(*x); print(*x, file=md)

# ------------------------------------------------------------------ report data
def rcsv(name):
    r = list(csv.DictReader(open(os.path.join(DATA, name), encoding="utf-8")))
    return {k: np.array([float(x[k]) if x[k] not in ("", None) else np.nan for x in r]) for k in r[0] if k != "source"}
F110, F35, F37, F489, F490, F491 = (rcsv(n) for n in ("targets_fig1-10.csv", "targets_fig3-5.csv", "targets_fig3-7a.csv",
                                                      "targets_fig4-89.csv", "targets_fig4-90.csv", "targets_fig4-91.csv"))
def rtime(s):
    h, m, sec = s.split(":"); return (int(h) - 12) * 3600 + (int(m) - 32) * 60 + float(sec)
EV = []
for x in csv.DictReader(open(os.path.join(DATA, "events.csv"), encoding="utf-8")):
    try: tt = rtime(x["time"].strip())
    except Exception: continue
    try: mw = float(x["mw_imbalance"].replace(",", "")) if x["mw_imbalance"] not in ("", "—", "-") else np.nan
    except ValueError: mw = np.nan
    EV.append(dict(cl=x["cluster"], c=x["country"], t=tt, ty=x["type"], d=x["description"], mw=mw))

# ------------------------------------------------------------------ model data
t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.tag), "v2"); tr = t - a.t0
def g(n): return next((c[k] for k in c if k == n or k.endswith(":" + n)), None)
def pv(b, cyc=3):
    r = pmu(t, *(c[f"V_{b}[{k}]"] for k in (1, 2, 3)), cycles=cyc); return r["t"] - a.t0, r["V"], r["f"]
buses = sorted({k[2:-3] for k in c if k.startswith("V_") and k.endswith("[1]")})
PV = {b: pv(b) for b in buses}; tp = PV[buses[0]][0]
Vmax = np.max([PV[b][1] for b in buses], axis=0)
tw, Vw, fw = PV["WAN"]                                     # Carmona (Sevilla 400 kV) ~ model bus WAN
_, _, fmad = PV["MAD"]
inst = sorted({k.split(":")[0] for k in c if k.startswith("SyncUnit(")})
Fm = np.array([c[f"{i}:Wspd"] for i in inst]) / (2 * np.pi); Fmean = Fm.mean(axis=0)
pfr, mhv = g("PFR"), g("MHV")
M(f"# Fidelity of `{a.tag}` against the Final Report\n\nmodel samples to t = {t[-1]:.2f} s (report time {tr[-1]:.2f} s); t0 = {a.t0} s = 12:32:00\n")

# RES instance -> plant (rating) by amplitude(IsrcA)/ID in a pre-event window
RES = []
for ln in open(os.path.join(HERE, a.build), encoding="utf-8", errors="replace"):
    m = re.match(r"RES (\S+)\s+at (\S+)\s+([\d.]+) MW\s+S\s+([\d.]+)", ln.strip())
    if m: RES.append(dict(name=m.group(1), bus=m.group(2), mw=float(m.group(3)), S=float(m.group(4))))
ri = sorted({k.split(":")[0] for k in c if k.startswith("RES_Plant(")}, key=lambda s: int(re.search(r"\d+", s).group()))
w0 = (tr > -1.5) & (tr < -0.5)
score = {}
for i in ri:
    ia = c[f"{i}:IsrcA"][w0]; idd = c[f"{i}:ID"][w0].mean(); score[i] = (np.percentile(np.abs(ia), 99) / max(idd, 1e-3))
Cm = np.array([[abs(np.log(score[i]) - np.log(p["S"])) for p in RES] for i in ri]); r_, c_ = linear_sum_assignment(Cm)
k_ = np.median([score[ri[x]] / RES[y]["S"] for x, y in zip(r_, c_)])
MAP = {ri[x]: RES[y] for x, y in zip(r_, c_)}
bad = [(i, MAP[i]["name"], score[i] / k_, MAP[i]["S"]) for i in ri if abs(np.log(score[i] / k_ / MAP[i]["S"])) > 0.15]
M(f"RES instance matching by rating: {len(MAP)} plants, scale {k_:.4g}; uncertain matches (>15 % off): {len(bad)}")
for b_ in bad: M(f"  {b_[0]} -> {b_[1]}: estimated S {b_[2]:.0f} vs {b_[3]:.0f} MVA")

# ------------------------------------------------------------------ model events
def first_rise(x, thr=0.5):
    j = np.argmax(x > thr); return tr[j] if x[j] > thr else np.nan
MEV = []
for i in ri:
    tt = first_rise(c[f"{i}:TRIP"])
    if np.isfinite(tt): MEV.append(dict(kind="RES trip", name=MAP[i]["name"], t=tt, mw=MAP[i]["mw"]))
for n_, lab in (("BRKM1", "pump M1 Duero (49.5 Hz)"), ("BRKM3", "pump M3 PT (49.8 Hz)"), ("BRKMA", "Morocco tie open")):
    v = g(n_)
    if v is not None:
        tt = first_rise(v)
        if np.isfinite(tt): MEV.append(dict(kind="breaker", name=lab, t=tt, mw=np.nan))
for n_, cty in (("M_ES", "ES"), ("M_PT", "PT")):
    v = g(n_)
    if v is not None:
        dv = np.diff(v); js = np.where(np.abs(dv) > 1e-4)[0]
        for j in js: MEV.append(dict(kind=f"LFDD {cty}", name=f"{cty} load factor {v[j]:.3f}->{v[j + 1]:.3f}", t=tr[j + 1], mw=np.nan))
MEV.sort(key=lambda e: e["t"])
M(f"\n## Model events ({len(MEV)})\n\n| t report [s] | 12:3x clock | kind | element | MW |\n|---|---|---|---|---|")
def clk(s): return f"12:{32 + int((s) // 60):02d}:{(s) % 60:06.3f}"
for e in MEV: M(f"| {e['t']:.3f} | {clk(e['t'])} | {e['kind']} | {e['name']} | {e['mw'] if np.isfinite(e['mw']) else ''} |")

# ------------------------------------------------------------------ signal metrics
def sig_metrics(name, trep, yrep, tmod, ymod):
    rows = []
    for ph, a0, a1 in PH + [("all", -5, 90)]:
        m = (trep >= a0) & (trep <= a1) & np.isfinite(yrep) & (trep <= tmod[-1]) & (trep >= tmod[0])
        if m.sum() < 3: rows.append((ph, None)); continue
        ym = np.interp(trep[m], tmod, ymod); e = ym - yrep[m]
        r = np.corrcoef(ym, yrep[m])[0, 1] if np.std(ym) > 0 and np.std(yrep[m]) > 0 else np.nan
        rows.append((ph, dict(n=int(m.sum()), bias=e.mean(), rmse=np.sqrt((e ** 2).mean()), maxe=np.abs(e).max(), r=r)))
    return name, rows
SIG = [sig_metrics("400 kV maximum voltage [kV] (Fig 3-7a)", F37["t_sim_s"], F37["Vmax_400kV"], tp, Vmax),
       sig_metrics("Carmona 400 kV voltage [kV] (Fig 1-10 + 3-5)", np.r_[F35["t_sim_s"], F110["t_sim_s"]],
                   np.r_[F35["V_carmona_kV"], F110["V_carmona_kV"]], tw, Vw),
       sig_metrics("Iberian frequency [Hz] (Fig 1-10)", F110["t_sim_s"], F110["f_iberia_Hz"], tr, Fmean),
       sig_metrics("Frequency vs PMU [Hz] (Fig 4-89)", F489["t_sim_s"], F489["f_pmu_Hz"], tr, Fmean),
       sig_metrics("Voltage vs PMU [pu] (Fig 4-90, Carmona)", F490["t_sim_s"], F490["V_pmu_pu"], tw, Vw / 400.0)]
if pfr is not None:
    SIG.append(sig_metrics("Spain-France P vs PMU [MW] (Fig 4-91, + = ES->FR)", F491["t_sim_s"], F491["P_pmu_MW"], tr, pfr + 1000.0 * mhv))
M("\n## Signal metrics (model - report)\n\n| signal | phase | n | bias | RMSE | max abs err | r |\n|---|---|---|---|---|---|---|")
for name, rows in SIG:
    for ph, d in rows:
        if d: M(f"| {name} | {ph} | {d['n']} | {d['bias']:+.3g} | {d['rmse']:.3g} | {d['maxe']:.3g} | {d['r']:.2f} |")
        else: M(f"| {name} | {ph} | 0 | | | | |")

# cumulative generation loss: report Fig 3-7a vs model RES trips (+ event-1 317 MW the model would have to produce)
cumt = np.array([e["t"] for e in MEV if e["kind"] == "RES trip"]); cumw = np.array([e["mw"] for e in MEV if e["kind"] == "RES trip"])
def mcum(x): return np.array([cumw[cumt <= xx].sum() for xx in x])

# ------------------------------------------------------------------ sequence matching (Table 3-3 / 3-1)
T33 = {"R1_Granada": "3", "R2_Badajoz4a": "4a", "R3_Badajoz4b": "4b", "R4_Badajoz5b1": "5b1", "R7_BadajozTS3": "6a3",
       "R6_Sevilla": "5a2", "R9_Cadiz": "6a7", "R8_Caceres": "6a4", "R5_Segovia": "5a1", "R10_Malaga": "6a8", "R11_Cuenca": "6b"}
rep_t = {}
for e in EV:
    if e["ty"].startswith("Generation loss") and e["cl"] not in rep_t: rep_t[e["cl"]] = e["t"]
SEQ = []
for nm, cl in T33.items():
    mt = next((e["t"] for e in MEV if e["kind"] == "RES trip" and e["name"] == nm), np.nan)
    SEQ.append(dict(cl=cl, plant=nm, trep=rep_t.get(cl, np.nan), tmod=mt))
# defence plan / ties / nuclear (report times from Table 3-1 and [CA] p.55-57)
def cross(fsig, thr):
    j = np.argmax(fsig < thr); return tr[j] if fsig[j] < thr else np.nan
DP = [("49.5 Hz crossed (pump step 1)", 80.180, cross(Fmean, 49.5)), ("49.0 Hz crossed (LFDD step 1)", 80.600, cross(Fmean, 49.0)),
      ("48.8 Hz crossed", 80.760, cross(Fmean, 48.8)), ("48.6 Hz crossed", 81.000, cross(Fmean, 48.6)),
      ("48.4 Hz crossed", 81.380, cross(Fmean, 48.4)), ("48.2 Hz crossed", 81.820, cross(Fmean, 48.2)),
      ("48.0 Hz crossed", 82.040, cross(Fmean, 48.0)),
      ("Morocco tie 16a", 80.229, next((e["t"] for e in MEV if e["name"] == "Morocco tie open"), np.nan)),
      ("France AC separation 31b", 81.535, np.nan)]
M("\n## Sequence: Table 3-3 plant trips\n\n| event | plant | report t [s] | model t [s] | error [s] |\n|---|---|---|---|---|")
for s in sorted(SEQ, key=lambda s: s["trep"]):
    M(f"| {s['cl']} | {s['plant']} | {s['trep']:.3f} | {s['tmod']:.3f} | {s['tmod'] - s['trep']:+.3f} |" if np.isfinite(s["tmod"])
      else f"| {s['cl']} | {s['plant']} | {s['trep']:.3f} | not tripped | |")
M("\n## Sequence: defence plan, ties\n\n| milestone | report t [s] | model t [s] | error [s] |\n|---|---|---|---|")
for n_, trp, tm in DP:
    M(f"| {n_} | {trp:.3f} | {tm:.3f} | {tm - trp:+.3f} |" if np.isfinite(tm) else f"| {n_} | {trp:.3f} | not reached / not modelled | |")
both = [s for s in SEQ if np.isfinite(s["tmod"])]
if len(both) >= 3:
    from scipy.stats import kendalltau
    tau = kendalltau([s["trep"] for s in both], [s["tmod"] for s in both]).statistic
else: tau = np.nan
M(f"\nTable 3-3 trips reproduced: {len(both)} of {len(SEQ)}; order agreement Kendall tau = {tau:.2f}" if np.isfinite(tau)
  else f"\nTable 3-3 trips reproduced: {len(both)} of {len(SEQ)}")

# milestones
rocof = np.gradient(np.convolve(Fmean, np.ones(2500) / 2500, mode="same"), t)
MS = [("minimum frequency [Hz]", np.nanmin(F110["f_iberia_Hz"]), Fmean.min()),
      ("maximum 400 kV voltage [kV]", np.nanmax(F37["Vmax_400kV"]), Vmax.max()),
      ("Carmona voltage at 12:32:56 [kV]", float(np.interp(56, F110["t_sim_s"], F110["V_carmona_kV"])) if F110["t_sim_s"][0] < 56 else float(np.interp(56, F35["t_sim_s"], F35["V_carmona_kV"])),
       float(np.interp(56, tw, Vw)))]
M("\n## Milestones\n\n| quantity | report | model |\n|---|---|---|")
for n_, rv, mv in MS: M(f"| {n_} | {rv:.3f} | {mv:.3f} |")

# ------------------------------------------------------------------ FIGURE 1: overview
def phases(ax_):
    for (n_, a0, a1), col in zip(PH, PHC): ax_.axvspan(a0, a1, color=col, zorder=0)
def evlines(ax_):
    for tt, lab in ((57.22, "3"), (76.443, "4a"), (79.62, "max import"), (81.535, "FR sep.")): ax_.axvline(tt, color="#888", lw=0.7, ls="--")
fig, ax = plt.subplots(5, 1, figsize=(13, 17), sharex=True)
VALID = None
for a_ in ax: phases(a_); evlines(a_)
ax[0].plot(F37["t_sim_s"], F37["Vmax_400kV"], color=CR, lw=2, label="Report: 400 kV maximum (Fig 3-7a)")
ax[0].plot(tp, Vmax, color=CM, lw=1.2, label="Model: max of 24 buses (PMU 3-cycle)")
ax[0].set_ylabel("400 kV maximum [kV]"); ax[0].legend(loc="upper left"); ax[0].set_ylim(395, 475)
ax[1].plot(F35["t_sim_s"], F35["V_carmona_kV"], color=CR, lw=2, label="Report: Carmona (Fig 3-5)")
ax[1].plot(F110["t_sim_s"], F110["V_carmona_kV"], color=CR, lw=2, ls=(0, (4, 1)), label="Report: Carmona (Fig 1-10)")
ax[1].plot(tw, Vw, color=CM, lw=1.2, label="Model: WAN (Sevilla) bus")
ax[1].set_ylabel("Carmona 400 kV [kV]"); ax[1].legend(loc="upper left"); ax[1].set_ylim(395, 475)
ax[2].plot(F110["t_sim_s"], F110["f_iberia_Hz"], color=CR, lw=2, label="Report: Iberia (Fig 1-10)")
ax[2].plot(F110["t_sim_s"], F110["f_CE_Hz"], color="#7f8c8d", lw=1.5, label="Report: Continental Europe")
ax[2].fill_between(tr, Fm.min(axis=0), Fm.max(axis=0), color=CM, alpha=0.3, label="Model: machines min..max")
ax[2].plot(tr, Fmean, color=CM, lw=1.2, label="Model: mean")
for f_ in (49.5, 49.0, 48.0): ax[2].axhline(f_, color="#aaa", lw=0.6, ls=":")
ax[2].set_ylabel("frequency [Hz]"); ax[2].legend(loc="lower left"); ax[2].set_ylim(46.5, 51.5)
x37 = F37["t_sim_s"]; ax[3].step(x37, F37["cum_imbalance_MW"], where="post", color=CR, lw=2, label="Report: accumulated loss + net load increase (Fig 3-7a)")
xs = np.linspace(-2, tr[-1], 600); ax[3].step(xs, mcum(xs), where="post", color=CM, lw=1.0, ls="--", label="Model: RES plant trips (relays)")
drv = np.zeros_like(tr)
for gname, gmw in (("RF_N", 2622.0), ("RF_S", 12943.0), ("RF_O", 5025.0)):   # MW of each driver group (build log)
    v = g(gname)
    if v is not None: drv = drv + (1.0 - v) * gmw
ax[3].plot(tr, drv + np.interp(tr, xs, mcum(xs)), color=CM, lw=1.6, label="Model: forced drivers (2a/2b + 270 MW ramp) + relay trips")
ax[3].set_ylabel("accumulated loss [MW]"); ax[3].legend(loc="upper left")
if pfr is not None:
    n = 1000; tot = np.convolve(pfr + 1000.0 * mhv, np.ones(n) / n, mode="same")
    ax[4].plot(tr, tot, color=CM, lw=1.4, label="Model: Spain->France AC + HVDC (0.2 s mean)")
ax[4].plot(F491["t_sim_s"], F491["P_pmu_MW"], "o", color=CR, ms=4, label="Report PMU: Spain-France P (Fig 4-91)")
ax[4].plot(F491["t_sim_s"], F491["P_sim_MW"], "-", color=CS, lw=1.2, label="Report simulation (Fig 4-91)")
ax[4].plot([0, 56.5, 58], [1500, 450, 0], "*", color=CR, ms=12, label="[CA] p.104: total export")
ax[4].plot([79.62], [-3807], "v", color=CR, ms=10, label="[CA] p.105: net import peak 3,807 MW")
ax[4].set_ylim(-5000, 6000); ax[4].set_ylabel("Spain->France [MW]"); ax[4].legend(loc="lower left", ncol=2); ax[4].set_xlabel("report time [s after 12:32:00]")
for (n_, a0, a1) in PH: ax[0].text((a0 + a1) / 2, ax[0].get_ylim()[1], n_, ha="center", va="bottom", fontsize=9)
ax[0].set_title(f"Model {a.tag} vs Final Report, 12:32:00 - 12:33:24", pad=18, fontsize=13)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "figs", f"fid_{a.tag}_overview.png"), dpi=110); plt.close(fig)

# ------------------------------------------------------------------ FIGURE 2: sequence of events
fig, ax = plt.subplots(figsize=(13, 9)); phases(ax)
rows = sorted(SEQ, key=lambda s: s["trep"]) + [dict(cl=n_, plant="", trep=trp, tmod=tm) for n_, trp, tm in DP]
for k, s in enumerate(rows):
    y = len(rows) - k
    ax.plot(s["trep"], y, "s", color=CR, ms=9)
    if np.isfinite(s["tmod"]):
        ax.plot(s["tmod"], y, "o", color=CM, ms=9); ax.annotate("", xy=(s["tmod"], y), xytext=(s["trep"], y), arrowprops=dict(arrowstyle="->", color="#555", lw=1))
        ax.text(max(s["trep"], s["tmod"]) + 0.4, y, f"{s['tmod'] - s['trep']:+.2f} s", va="center", fontsize=8)
    else:
        ax.text(s["trep"] + 0.4, y, "not reproduced" if s["plant"] else "not reached / not modelled", va="center", fontsize=8, color="#999")
    ax.text(-1, y, f"{s['cl']} {s['plant']}", ha="right", va="center", fontsize=9)
ax.set_yticks([]); ax.set_xlim(-30, 86); ax.set_xlabel("report time [s after 12:32:00]")
ax.legend(handles=[Line2D([], [], marker="s", color=CR, ls="", label="Report (Table 3-1/3-3, [CA])"),
                   Line2D([], [], marker="o", color=CM, ls="", label=f"Model {a.tag}")], loc="upper center")
ax.set_title("Sequence of events: plant trips (Table 3-3), defence-plan thresholds, ties", fontsize=13)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "figs", f"fid_{a.tag}_sequence.png"), dpi=110); plt.close(fig)

# ------------------------------------------------------------------ FIGURE 3: collapse zoom vs PMU
fig, ax = plt.subplots(3, 1, figsize=(12, 11), sharex=True)
ax[0].plot(F489["t_sim_s"], F489["f_pmu_Hz"], "o-", color=CR, ms=4, lw=1.5, label="PMU (Fig 4-89)")
ax[0].plot(F489["t_sim_s"], F489["f_sim_Hz"], "-", color=CS, lw=1.2, label="[FR] simulation")
ax[0].plot(tr, Fmean, color=CM, lw=1.4, label="Model: machine mean"); ax[0].set_ylabel("frequency [Hz]")
ax[1].plot(F490["t_sim_s"], F490["V_pmu_pu"], "o-", color=CR, ms=4, lw=1.5, label="PMU (Fig 4-90)")
ax[1].plot(F490["t_sim_s"], F490["V_sim_pu"], "-", color=CS, lw=1.2, label="[FR] simulation")
ax[1].plot(tw, Vw / 400.0, color=CM, lw=1.4, label="Model: WAN (Sevilla)"); ax[1].set_ylabel("voltage [pu]")
ax[2].plot(F491["t_sim_s"], F491["P_pmu_MW"], "o-", color=CR, ms=4, lw=1.5, label="PMU (Fig 4-91)")
ax[2].plot(F491["t_sim_s"], F491["P_sim_MW"], "-", color=CS, lw=1.2, label="[FR] simulation")
if pfr is not None: ax[2].plot(tr, pfr + 1000.0 * mhv, color=CM, lw=1.0, label="Model: AC + HVDC")
ax[2].set_ylabel("Spain->France [MW]"); ax[2].set_xlabel("report time [s after 12:32:00]")
for a_ in ax: a_.set_xlim(75.5, 84); a_.legend(loc="lower left"); evlines(a_)
ax[0].set_title("Collapse window 12:33:15.5 - 12:33:24: model vs PMU and vs the report's own simulation", fontsize=13)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "figs", f"fid_{a.tag}_collapse.png"), dpi=110); plt.close(fig)

# ------------------------------------------------------------------ FIGURE 4: scorecard
fig, ax = plt.subplots(1, 2, figsize=(14, 6.5))
lab, val, scal = [], [], []
for name, rows in SIG:
    for ph, d in rows:
        if d and ph != "all": lab.append(f"{name.split('[')[0].strip()} | {ph.split()[0]}"); val.append(d["rmse"]); scal.append(name)
unit_scale = {"400 kV": 10.0, "Carmona": 10.0, "Iberian": 0.1, "Frequency vs PMU": 0.1, "Voltage vs PMU": 0.025, "Spain-France": 500.0}
nv = []
for l_, v_ in zip(lab, val):
    sc = next((s for k, s in unit_scale.items() if l_.startswith(k)), 1.0); nv.append(v_ / sc)
cols_ = ["#27ae60" if x <= 0.5 else ("#f39c12" if x <= 1.0 else "#c0392b") for x in nv]
ax[0].barh(range(len(nv)), nv, color=cols_); ax[0].set_yticks(range(len(nv))); ax[0].set_yticklabels(lab, fontsize=8)
ax[0].axvline(0.5, color="#27ae60", ls="--", lw=1); ax[0].axvline(1.0, color="#c0392b", ls="--", lw=1); ax[0].invert_yaxis()
ax[0].set_xlabel("RMSE / tolerance  (tolerance: 10 kV, 0.1 Hz, 0.025 pu, 500 MW)"); ax[0].set_title("Signal fidelity per phase")
seq_err = [abs(s["tmod"] - s["trep"]) for s in SEQ if np.isfinite(s["tmod"])]
cats = ["plant trips\nreproduced", "defence-plan\nthresholds reached", "median |timing\nerror| [s]"]
dpr = sum(np.isfinite(tm) for _, _, tm in DP[:7])
vals = [len(seq_err) / len(SEQ), dpr / 7.0, (np.median(seq_err) if seq_err else np.nan)]
ax[1].bar(cats[:2], vals[:2], color=[CM, CM]); ax[1].set_ylim(0, 1.05); ax[1].set_ylabel("fraction of report events")
for k, v in enumerate(vals[:2]): ax[1].text(k, v + 0.02, f"{v:.0%}", ha="center")
ax[1].set_title(f"Sequence fidelity  (median |Δt| of reproduced trips: {vals[2]:.2f} s; Kendall τ {tau:.2f})" if np.isfinite(vals[2])
                else "Sequence fidelity")
fig.suptitle(f"Fidelity scorecard: {a.tag}", fontsize=14); fig.tight_layout(); fig.savefig(os.path.join(HERE, "figs", f"fid_{a.tag}_score.png"), dpi=110)
M(f"\nfigures: iberia_eq/pscad/figs/fid_{a.tag}_overview.png, _sequence.png, _collapse.png, _score.png")
