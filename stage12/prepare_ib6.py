"""S25 (Claude): build `ib6` from the S24 working ib5 (which carries the executor's 15 recorders).

Why (measured in S24/S25, see RUNLOG Session 25):
  * ib5 cold starts were not a valid initialisation: the SyncUnits run as free machines from t=0
    (machsw=1, Enab=1), the Iberian Ph0 were the OLD import-case angles (-4..+2 deg vs France) while
    the export dispatch needs +18..+24 deg (stage12/dcflow.py), and the plants ramp from 0 at 0.1-0.6 s
    against 28 GW of load that is on from t=0. Every run therefore started with a multi-GW kick.
  * the IEEE-39 equivalent was scaled to 25 GW (base 410.4 MVA = 4.104 x 100); ib5 carries
    32.6 GW (Iberia 28.1 + France 4.5) = 1.30x, with the same ohms -> 1.69x reactive losses, 1.3x
    angles; the reactors (5.95 Gvar) were sized for the 25 GW ib4hv state.

What this script does (no physical machine/plant parameter is changed):
  1. dispatch back to the S23 report split (sync 11,950 MW, plants at the S23 Pref, France 3,195.8);
     executor's diagnostic leftovers reset (BRK31 trip at 1 s -> 1e6; OOS arm 0.5 -> 11.0 s).
  2. network base x KNET (default 1.30) for every line except the two France ties (WP8-calibrated):
     R, L / KNET, C x KNET; every transformer Tmva x KNET (pu reactance kept);
     every shunt reactor (SH30/31/32/37/19 and the bus-9 bank) QO x KNET.
  3. machine angles Ph0 from the DC power flow of the scaled network; Iberian V0 = 1.03 (412 kV).
  4. start-up sequence in the SyncUnit definition:
        0 .. TS2M   machine = ideal source at V0/Ph0          (machsw = S2M)
        TS2M .. TREL machine model, rotor LOCKED at 50 Hz      (Enab = L2N)  -> acts as a slack,
                    absorbs the plant ramp, exciters/PLLs settle
        TREL ..     free rotor; turbine power = electrical power at the release instant
                    (sample-and-hold of filtered POUT -> PMH), so the release is bumpless.
     plants ramp 0.3 -> 1.5 s.
usage: python stage12/prepare_ib6.py --src C:/PSCAD_work/s23/ib5.pscx --dst C:/PSCAD_work/s25/ib6.pscx
"""
import argparse, copy, random, re, xml.etree.ElementTree as ET

G = 18
SYNC_REPORT = {  # id: (P0 MW, Pmec pu)  -- S23 values (stage11/ib5_s23_prepared.pscx)
    "993049547": (1528.9, 0.25011), "1404126973": (3387.6, 0.25004),
    "489869766": (3823.5, 0.25003), "650097263": (3210.0, 0.25004)}
UPRAMP_REPORT = {"476430100": 0.887500, "1701983861": 0.890000, "1700000008": 0.895349,
    "1700000017": 0.898204, "1700000026": 0.899667, "1700000036": 0.647941, "1700000045": 0.644718,
    "1700000054": 0.647766, "1700000063": 0.647386, "1700000072": 0.648063, "1700000081": 0.648275,
    "1700000090": 0.648094, "1700000100": 0.898693, "1700000109": 0.899231, "1700000118": 0.899960,
    "1700000128": 0.899830, "1700000137": 0.899425, "1700000146": 0.899745}
TIES = {"1600000039", "1600000099"}
REACTORS = {"969776013", "1104658829", "537126178", "1035318058", "1786223168", "1566437801"}
# v2 set-points from the AC power flow (stage12/ib6_setpoints.py ... 1.06 750 500 1000 ->
# stage12/ib6_setpoints_v2.txt): units P0/Q0/Ph0 (V0 1.06), France Q0, loads PO at operating V,
# reactors: bus 9 1000 Mvar, bus 29 750 (SH30 element re-labelled SH29), bus 1 500 (SH31 element -> SH01),
# SH37/SH32/SH19 elements ~0 (kept in place, 0.001 Mvar/phase).
UNIT_V2 = {"993049547": (1609.3, -807.8, 0.36135), "1404126973": (3565.8, -51.5, 0.38408),
           "489869766": (4024.6, -149.8, 0.42230), "650097263": (3378.8, -879.3, 0.46613)}
FR_Q0 = -930.0
LOAD_V2 = {"744210529": 549.863, "1004648478": 404.547, "1522722771": 903.818, "1862156076": 12.938,
    "914258219": 559.526, "1925407754": 581.780, "1087233095": 270.471, "2071274910": 1294.095,
    "775660433": 492.935, "553408281": 456.128, "1468690411": 547.996, "1275297413": 376.228,
    "979306711": 227.056, "768585174": 468.165, "2117866167": 340.174, "427020063": 476.857,
    "1446795315": 16.106, "2035760321": 858.923, "576505807": 1480.659}
REAC_V2 = {"969776013": 1000 / 3, "1104658829": 750 / 3, "537126178": 500 / 3,
           "1035318058": 0.001, "1786223168": 0.001, "1566437801": 0.001}
RELABEL = {"1108394361": ("SH29", (1188, 360)), "383551939": ("SH01", (504, 630))}  # reactor-side label, new bus-side label (px)
PH0 = {i: v[2] for i, v in UNIT_V2.items()}


def P(el):
    return {q.get("name"): q for q in el.find("paramlist").findall("param")}


def f(v):
    return float(str(v).split("[")[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True)
    ap.add_argument("--knet", type=float, default=2.6, help="series strength factor (R, L / knet; Tmva x knet)")
    ap.add_argument("--kc", type=float, default=1.3, help="line charging factor (C x kc)")
    ap.add_argument("--sp", default=None, help="set-point JSON from ib6_setpoints.py (default: the v2 constants)")
    ap.add_argument("--ts2m", type=float, default=0.52)
    ap.add_argument("--trel", type=float, default=5.0)
    ap.add_argument("--v0", type=float, default=1.06)
    ap.add_argument("--ramp0", type=float, default=0.3)
    ap.add_argument("--vdc", type=float, default=800.0)
    ap.add_argument("--ramp1", type=float, default=1.5)
    ap.add_argument("--trim", default=None, help='JSON {unit_id: trim MW} applied as Pmec = MW/Sbase after release')
    a = ap.parse_args()
    import json as _j
    SBASE = {"993049547": 6113, "1404126973": 13548, "489869766": 15292, "650097263": 12838, "1766995819": 200000}
    TRIM = {k: v / SBASE[k] for k, v in (_j.load(open(a.trim)).items() if a.trim else [])}
    global UNIT_V2, FR_Q0, LOAD_V2, REAC_V2
    if a.sp:
        import json
        js = json.load(open(a.sp))
        UNIT_V2 = {k: tuple(v) for k, v in js["units"].items()}; FR_Q0 = js["fr_q0"]
        LOAD_V2 = js["loads"]; REAC_V2 = js["reactors"]
        UPRAMP_REPORT.update(js.get("ramps", {}))
    txt = open(a.src, encoding="utf-8").read()
    txt = txt.replace('<project name="ib5"', '<project name="ib6"').replace('"ib5:', '"ib6:')
    root = ET.fromstring(txt)
    D = {d.get("name"): d for d in root.iter("Definition")}
    M = D["Main"].find("schematic")
    byid = {c.get("id"): c for c in M}

    # 1. dispatch + leftovers
    for i, (p0, q0, ph0) in UNIT_V2.items():
        pp = P(byid[i]); pp["P0"].set("value", str(p0)); pp["Q0"].set("value", str(q0))
        pp["Pmec"].set("value", f"{TRIM.get(i, 0.0):.6f}")   # Pmec = dispatch trim [pu of Sbase], ramped in after release
        pp["Ph0"].set("value", f"{ph0:.5f}"); pp["V0"].set("value", f"{a.v0:.4f}")
    P(byid["1766995819"])["Q0"].set("value", str(FR_Q0))
    # France covers its own load minus the AC tie only (the HVDC power ends in the ideal DC source):
    # 4,530.8 - 335 = 4,195.8 MW (S23 had 3,195.8, which wrongly assumed the HVDC delivered to France)
    P(byid["1766995819"])["P0"].set("value", "4195.8"); P(byid["1766995819"])["Pmec"].set("value", f"{TRIM.get('1766995819', 0.0):.6f}")
    for i, po in LOAD_V2.items():
        P(byid[i])["PO"].set("value", f"{po:.4f}")
    for i, y2 in UPRAMP_REPORT.items():
        pp = P(byid[i]); pp["Y2"].set("value", f"{y2:.6f}")
        pp["X1"].set("value", str(a.ramp0)); pp["X2"].set("value", str(a.ramp1))
    P(byid["1407146800"])["X"].set("value", "1.0e6")
    P(byid["1092099223"])["X"].set("value", "11.0")

    # 1b. converter DC headroom: shared DC source 800 kV -> vdc; every converter's Kmod x 800/vdc,
    #     so the AC volts per pu of reference are unchanged and the modulation ceiling rises from
    #     400/326.6 = 1.22 pu to (vdc/2)/326.6 pu.
    nk = 0
    for c in M:
        if c.get("defn") == "master:source1":
            P(c)["Esd"].set("value", f"{a.vdc:g} [kV]")
        if c.get("defn") in ("ib6:RES_Plant", "ib6:HVDC_T"):
            pp = P(c); pp["Kmod"].set("value", repr(f(pp["Kmod"].get("value")) * 800.0 / a.vdc)); nk += 1
    assert nk == 19, nk
    # 2. network base
    nl = nx = nr = 0
    for c in M:
        d = c.get("defn")
        if d == "master:pi_section" and c.get("id") not in TIES:
            pp = P(c)
            for k in ("Rp1", "Lp1", "XLp1", "RPUP1", "XLPUP1", "Rz1", "Lz1", "XLz1", "RPUZ1", "XLPUZ1"):
                pp[k].set("value", repr(f(pp[k].get("value")) / a.knet))
            for k in ("XCp1", "XCPUP1", "XCz1", "XCPUZ1"):
                pp[k].set("value", repr(f(pp[k].get("value")) / a.kc))
            for k in ("Cp1", "BPUP1", "Cz1", "BPUZ1"):
                pp[k].set("value", repr(f(pp[k].get("value")) * a.kc))
            nl += 1
        elif d == "master:xfmr-3p2w":
            pp = P(c); pp["Tmva"].set("value", repr(f(pp["Tmva"].get("value")) * a.knet)); nx += 1
        elif c.get("id") in REACTORS:
            pp = P(c); pp["QO"].set("value", f"{REAC_V2[c.get('id')]:.4f}"); nr += 1
    assert (nl, nx, nr) == (32, 12, 6), (nl, nx, nr)
    for lid, (nm, (x, y)) in RELABEL.items():
        lab = byid[lid]; P(lab)["Name"].set("value", nm)
        new = copy.deepcopy(lab); new.set("id", str(int(lid) + 7)); new.set("x", str(x)); new.set("y", str(y))
        M.append(new)

    # 4. SyncUnit start-up sequence
    S = D["SyncUnit"].find("schematic")
    sb = {c.get("id"): c for c in S}
    mp = P(next(c for c in S if c.get("defn") == "master:sync_machine"))
    mp["machsw"].set("value", "S2M"); mp["Enab"].set("value", "L2N")
    used = set(sb); rnd = random.Random(25)

    def nid():
        while True:
            i = str(rnd.randint(1_000_000_000, 2_000_000_000))
            if i not in used:
                used.add(i); return i
    tm = {}
    for k in ("master:datalabel", "master:time-sig", "master:realpole", "master:sandhdefn",
              "master:upramp", "master:gain", "master:sumjct"):
        tm[k] = next(c for c in S if c.get("defn") == k)
    tm["master:compare"] = next(c for c in M if c.get("defn") == "master:compare")

    def place(kind, x, y, **vals):
        el = copy.deepcopy(tm["master:" + kind]); el.set("id", nid())
        el.set("x", str(x * G)); el.set("y", str(y * G)); el.set("orient", "0")
        pp = P(el)
        for k, v in vals.items():
            pp[k].set("value", str(v))
        S.append(el); return el
    for y, xt, nm in ((66, a.ts2m, "S2M"), (70, a.trel, "L2N")):
        place("time-sig", 15, y); place("compare", 19, y, X=xt, OL=0, OH=1); place("datalabel", 21, y, Name=nm)
    place("datalabel", 24, 76, Name="POUT"); place("realpole", 26, 76, G=1, T=0.1, Limit=0, Max=10, Min=-10)   # no limit (the template is the governor pole, limited at GovLim)
    place("sandhdefn", 30, 76, Iand=1)
    place("datalabel", 30, 78, Name="L2N"); place("datalabel", 32, 76, Name="PMH")
    # turbine setpoint: the Pmec import at (48,52) (output port (50,52), wire to the TMECH sum) is
    # moved aside (kept: the parameter must stay referenced) and the held value PMH takes its port
    imp = next(c for c in S if c.get("defn") == "master:import" and P(c)["Name"].get("value") == "Pmec")
    imp.set("x", str(48 * G)); imp.set("y", str(90 * G)); place("datalabel", 50, 90, Name="PMEC0")
    place("datalabel", 50, 52, Name="PMT")
    # dispatch trim: TRIM = Pmec * ramp(TREL -> TREL+2 s); PMT = PMH + TRIM feeds the TMECH sum.
    # Pmec is a run-time parameter: a trim can be changed and applied from a snapshot (warm re-settle).
    place("time-sig", 15, 82); place("upramp", 19, 82, X1=a.trel, X2=a.trel + 2.0, Y2=1.0)
    place("gain", 23, 82, G="Pmec"); place("datalabel", 25, 82, Name="TRIM")
    place("datalabel", 28, 86, Name="PMH"); place("datalabel", 30, 88, Name="TRIM")
    place("sumjct", 30, 86, A=0, B=0, C=0, D=1, E=0, F=1, G=0); place("datalabel", 32, 86, Name="PMT")

    snap = root.find("paramlist")
    for q in snap.findall("param"):
        n = q.get("name")
        if n == "snapshot_filename": q.set("value", "ib6_settle12.snp")
        if n == "time_duration": q.set("value", "14")
        if n == "StartType": q.set("value", "0")
        if n == "SnapType": q.set("value", "1")
        if n == "SnapTime": q.set("value", "12")
    open(a.dst, "w", encoding="utf-8").write(ET.tostring(root, encoding="unicode"))
    print(f"written {a.dst}: lines {nl}, xfmr {nx} series x{a.knet}, charging x{a.kc}, reactors {nr} (sp {a.sp}); Vdc {a.vdc}; ramp {a.ramp0}-{a.ramp1}; TS2M {a.ts2m} TREL {a.trel}")


if __name__ == "__main__":
    main()
