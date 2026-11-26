r"""Prepare a v2 replay variant from the replay case + its settle run (S30 sec 19).

usage: python iberia_eq\pscad\make_replay.py <name> --settle rp_settle30 [--relays] [--nuclear]
Copies C:\PSCAD_work\v2sld_r\v2.pscx to C:\PSCAD_work\<name>\ and applies:
  --nuclear : SyncUnit Ttrip/Ptrip for the trips of Table 3-1 41a/41c/46 (t0 + report seconds; torque removed);
  --relays  : RES OV relays of the plants named in Table 3-3 (design change B, V2_BUS_UNIT_LIST §3A):
              threshold = model pre-event bus V (PMU mean 26-28 s of the settle run)
                          + (report V at trip - report pre-event V at that substation, Fig 2-4 SCADA 12:32:00)
              measured at the POI (MeasSide 1), Trel 0.05 s (measurement filter, RUNLOG S30 sec 17), Tt1 0.1 s;
              Granada (event 3, 220 kV-side instantaneous OV of the evacuation transformer) Tt1 0.02 s.
              The zone aggregates (A*) stay parked at 1.5 pu.
Writes <name>\replay_settings.txt (every threshold with its derivation).
"""
import argparse, os, re, shutil, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from legacy_out import load
from pmu import pmu

ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("--settle", required=True)
ap.add_argument("--relays", action="store_true"); ap.add_argument("--nuclear", action="store_true"); a = ap.parse_args()
T0 = 30.0
DST = os.path.join(r"C:\PSCAD_work", a.name); os.makedirs(DST, exist_ok=True); PSCX = os.path.join(DST, "v2.pscx")
shutil.copy(r"C:\PSCAD_work\v2sld_r\v2.pscx", PSCX); rep = open(os.path.join(DST, "replay_settings.txt"), "w")
def R(*x): print(*x); print(*x, file=rep)
R(f"variant {a.name} from C:\\PSCAD_work\\v2sld_r, settle {a.settle}, t0 = {T0} s = 12:32:00")
def sup(defn, match, sets):
    r = subprocess.run([sys.executable, os.path.join(HERE, "set_unit_params.py"), "--pscx", PSCX, "--defn", defn, "--match", *match, "--set", *sets],
                       capture_output=True, text=True); R("  " + (r.stdout.strip() or r.stderr.strip()))
    if r.returncode: raise SystemExit(1)
if a.nuclear:                       # Table 3-1: 41a 12:33:22.702 1,045 MW; 41c 23.515 653 MW (Almaraz II, model 660); 46 23.590 1,692 MW
    for p0, s, ts in ((1045.0, 1222.2, 82.702), (660.0, 1111.1, 83.515), (1692.0, 2144.4, 83.590)):
        sup("SyncUnit", [f"P0={p0}"], [f"Ttrip={T0 + ts:.3f}", f"Ptrip={-p0 / s:.4f}"])
if a.relays:
    t, c = load(os.path.join(r"C:\PSCAD_work\v2_runs", a.settle), "v2")
    def vpre(b):
        r = pmu(t, *(c[f"V_{b}[{k}]"] for k in (1, 2, 3)), cycles=3); w = (r["t"] >= 26) & (r["t"] <= 28); return float(r["V"][w].mean())
    # plant (Sbase in the case) : (model bus, report V at trip [kV, 400 kV equiv.], report pre-event V [kV], event, Tt1)
    # 220 kV readings are converted at their own pu (V/220 * 400); pre-event SCADA values from SOURCES §5 (Fig 2-4)
    PL = {"394.44": ("GRA", 417.9, 409.0, "3 TS1-Granada", 0.02),
          "646.67": ("BAD_TS", 435.0, 412.5, "4a TS1-Badajoz (432.6-437.3)", 0.1),
          "161.11": ("BAD_TS", 438.7, 412.5, "4b TS2-Badajoz", 0.1),
          "131.11": ("BAD_TS", 443.0, 412.5, "5b1 TS1-Badajoz", 0.1),
          "120.00": ("BAD_TS", 447.7, 412.5, "6a3 TS3-Badajoz", 0.1),
          "611.11": ("WAN_TS", 437.7, 413.5, "5a2 TS1-Sevilla", 0.1),
          "170.00": ("WAN_TS", 248.2 / 220 * 400, 414.0, "6a7 TS1-Cadiz 220 kV 248.2", 0.1),
          "87.22": ("CAC", 444.3, 406.0, "6a4 TS2-Caceres", 0.1),
          "130.00": ("CYL", 436.5, 405.0, "5a1 TS1-Segovia (wind)", 0.1),
          "171.11": ("GRA", 448.6, 415.0, "6a8 TS1-Malaga", 0.1),
          "588.89": ("VAL", 448.6, 413.0, "6b TS1-Cuenca ([CA] Olmedilla 413 at 12:32:00)", 0.1)}
    for sb, (bus, vtrip, vrep, ev, tt) in PL.items():
        vm = vpre(bus); thr = vm + (vtrip - vrep)
        R(f"  relay {ev:42s} bus {bus:7s} model pre {vm:6.1f} kV + ({vtrip:6.1f} - {vrep:6.1f}) = {thr:6.1f} kV = {thr / 400:.4f} pu, Tt1 {tt}")
        sup("RES_Plant", [f"Sbase={sb}"], [f"Vt1={thr / 400:.4f}", f"Tt1={tt}", "MeasSide=1", "Trel=0.05", "Nsub=1", "Share1=1.0"])
R("done")
