"""S23 (Claude): build the `ib5` case from the adopted S22 point (stage5/ib4hv_lever3_pod04.pscx).

Everything here is a parameter / topology edit made on the UNLOADED XML (rule P12). Nothing was
simulated before writing it: the first run of ib5 is the settle run of PLAN v1.0 S0 (WP7).

  1. Breakers on all five SyncUnits (`master:breaker3`, signal 0 = closed, 1 = open, proven S18).
     Buses 31/32/37: the series survey multimeter is REPLACED by the breaker (0 extra nodes).
     Bus 30 (6113 MVA unit): breaker inserted, the unit moved 3 grid up (+3 nodes).
     France: its multimeter is kept (it makes `Ph39` and now the tie meter PTIE/QTIE, MW / Mvar)
     and a breaker is added on the bus-39 side (+3 nodes) = the TIE BREAKER.
     The shunt-reactor labels SH30/31/32/37 move from the machine terminal to the 400 kV bus side,
     so a tripped unit does not take its reactor with it.
     Control: BRK30/31/32/37 = compare(time > T_trip) (default 1e6 s = never; set X to replay a trip).
  2. Out-of-step (loss-of-synchronism) relay for the tie:
       cos(Ph39 - Ph9) < cos(OOS_DEG)  AND  time > T_ARM  -> latch -> BRKFR = 1 (tie opens, stays open).
     cos() removes the +-180 deg wrap of the two multimeter angles.
  3. Tie strength: T1_39 and T9_39 series R, L scaled by K_TIE (X/R and line charging unchanged).
     Default K_TIE = 9.23: 9.75 -> 90 ohm each, ~45 ohm in parallel, Pmax ~ 420^2/45 = 3.9 GW,
     i.e. the -3.6..-3.9 GW import at which the report's ties lost synchronism (Fig 4-91).
  4. The 4,531 MW load at bus 39 becomes FRENCH local load: moved to the France terminal node
     (HE39_2, machine side of the tie breaker), so it leaves with France when the tie opens.
  5. Iberian demand: the other 18 loads are scaled so they carry Spain 25,237.5 MW + the constant
     exports Portugal 2,100 + Morocco 750 MW (report p.134) = 28,087.5 MW at 1 pu voltage.
  6. Generation: the four Iberian SyncUnits to the report's synchronous total 11,950 MW (Fig 1-4:
     nuclear, CCGT, coal, hydro, pumped-gen, solar-thermal, cogeneration, thermal RES), Pmec = P0/Sbase.
     The 18 plants are uprated x K_PLANT (Sbase, Ki, Lf, Cf; Rf unchanged) to the report's PV+wind
     level and their Pref restored to the pre-lever-3 values (lever 3 undone).
  7. France: P0/Pmec = French load - AC export to France (335 MW) - HVDC 1,000 MW (the far end).
     Spain therefore EXPORTS 4,185 MW in total (Fig 3-5): 2,850 to Portugal/Morocco (as load),
     1,000 HVDC, 335 AC.
  8. HVDC left in PMODE 1 = constant P 1,000 MW (the report's 12:09 switch from AC emulation).
  9. Ph31/Ph32/Ph37 recorders removed (their multimeters are now breakers).

usage: python stage11\\prepare_ib5.py --src stage5\\ib4hv_lever3_pod04.pscx --dst C:\\PSCAD_work\\s23\\ib5.pscx
       [--k-tie 9.23] [--k-plant 1.30] [--oos-deg 120] [--t-arm 2.0] [--dry]
"""
import argparse, copy, math, random
import xml.etree.ElementTree as ET

G = 18
SYNC_TARGET_MW = 11950.0
IBERIA_LOAD_MW = 25237.5 + 2100.0 + 750.0
AC_EXPORT_MW, HVDC_MW = 335.0, 1000.0
LEVER3_PU = 2500.0 / 16549.0          # S22 lever 3: -0.1511 pu on all 18 plant upramps
FR_LOAD_ID = "576505807"
TIE_PI = ("1600000039", "1600000099")  # T1_39, T9_39 (the only two pi sections with the IEEE 1-39/9-39 L)
FR_ID = "1766995819"

BRK_XML = """<User classid="UserCmp" id="0" name="master:breaker3" x="0" y="0" w="41" h="80" z="-1" orient="1" defn="master:breaker3" link="-1" disable="false"><paramlist name="" link="-1" crc="72525059">
<param name="Ctrl" value="0" /><param name="OPCUR" value="1" /><param name="ENAB" value="0" /><param name="CLVL" value="0.0" />
<param name="View" value="1" /><param name="ViewB" value="1" /><param name="DisPQ" value="0" /><param name="NAME" value="BRK" />
<param name="NAMEA" value="BRKA" /><param name="NAMEB" value="BRKB" /><param name="NAMEC" value="BRKC" /><param name="ROFF" value="1.0e6" />
<param name="RON" value="0.005" /><param name="PRER" value="0.5" /><param name="TDA" value="0.0" /><param name="TDB" value="0.0" />
<param name="TDC" value="0.0" /><param name="TDRA" value="0.05" /><param name="TDRB" value="0.05" /><param name="TDRC" value="0.05" />
<param name="PostIns" value="0" /><param name="TDBOA" value="0.005" /><param name="IBRA" value="" /><param name="IBRB" value="" />
<param name="IBRC" value="" /><param name="IBR0" value="" /><param name="SBRA" value="" /><param name="SBRB" value="" /><param name="SBRC" value="" />
<param name="BP" value="" /><param name="BQ" value="" /><param name="Vbr" value="" /><param name="BOpen1" value="0" /><param name="BOpen2" value="0" />
<param name="BOpen3" value="0" /><param name="P" value="0.0" /><param name="Q" value="0.0" /></paramlist></User>"""
TRIG_XML = """<User classid="UserCmp" id="0" name="master:trig" x="0" y="0" w="80" h="36" z="-1" orient="0" defn="master:trig" link="-1" disable="false"><paramlist name="" link="-1" crc="14542488">
<param name="Name" value="" /><param name="Type" value="2" /><param name="Mode" value="1" /><param name="COM" value="Trig-Func" /><param name="Dim" value="1" /><param name="const" value="false" /></paramlist></User>"""
SUM_XML = """<User classid="UserCmp" id="0" name="master:sumjct" x="0" y="0" w="80" h="64" z="-1" orient="0" defn="master:sumjct" link="-1" disable="false"><paramlist name="" link="-1" crc="44632040">
<param name="Name" value="" /><param name="DPath" value="1" /><param name="Dim" value="1" /><param name="A" value="0" /><param name="B" value="0" /><param name="C" value="0" />
<param name="D" value="1" /><param name="E" value="0" /><param name="F" value="-1" /><param name="G" value="0" /></paramlist></User>"""
WIRE_XML = """<Wire classid="WireOrthogonal" id="0" name="" x="0" y="0" w="10" h="10" orient="0" layer="" disable="false"><vertex x="0" y="0" /><vertex x="0" y="0" /></Wire>"""


def P(el):
    return {q.get("name"): q for q in el.find("paramlist").findall("param")}


def f(v):
    return float(str(v).split("[")[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True)
    ap.add_argument("--k-tie", type=float, default=9.23)
    ap.add_argument("--k-plant", type=float, default=1.30)
    ap.add_argument("--oos-deg", type=float, default=120.0)
    ap.add_argument("--t-arm", type=float, default=11.0)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    tree = ET.parse(a.src); root = tree.getroot()
    main_def = [d for d in root.iter("Definition") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")
    byid = {c.get("id"): c for c in sch}
    used = set(byid)
    rnd = random.Random(23)

    def nid():
        while True:
            i = str(rnd.randint(1_000_000_000, 2_000_000_000))
            if i not in used:
                used.add(i); return i

    tmpl = {d: copy.deepcopy(next(c for c in sch if c.get("defn") == d))
            for d in ("master:datalabel", "master:nodelabel", "master:compare", "master:pi_ctlr", "master:time-sig")}

    def place(kind, x, y, orient=0, **vals):
        el = ET.fromstring({"brk": BRK_XML, "trig": TRIG_XML, "sum": SUM_XML}[kind]) if kind in ("brk", "trig", "sum") \
            else copy.deepcopy(tmpl["master:" + kind])
        el.set("id", nid()); el.set("x", str(x * G)); el.set("y", str(y * G))
        if kind != "brk":
            el.set("orient", str(orient))
        pp = P(el)
        for k, v in vals.items():
            if k not in pp:
                raise SystemExit(f"{kind}: no param {k}")
            pp[k].set("value", str(v))
        sch.append(el); return el

    def wire(x0, y0, x1, y1):
        el = ET.fromstring(WIRE_XML); el.set("id", nid()); el.set("x", str(x0 * G)); el.set("y", str(y0 * G))
        v = el.findall("vertex"); v[1].set("x", str((x1 - x0) * G)); v[1].set("y", str((y1 - y0) * G))
        sch.append(el)

    def drop(*ids):
        for i in ids:
            sch.remove(byid[i])

    def move(i, x, y):
        byid[i].set("x", str(x * G)); byid[i].set("y", str(y * G))

    # ---- 1. machine breakers -----------------------------------------------------------------
    # bus 37: MM 1837570401 (32,7) ports (32,6)/(32,8); wire (32,8)-(32,10) to Bus37 bar y=10
    drop("1837570401", "1574300847"); place("brk", 32, 8, NAME="BRK37"); move("2065599253", 30, 10)
    # bus 32: MM 351692673 (43,97) ports (43,98)/(43,96); wire (43,96)-(43,94) to Bus32 bar y=94
    drop("351692673", "212646822"); place("brk", 43, 96, NAME="BRK32"); move("1831958963", 45, 94)
    # bus 31: MM 827627569 (33,85) ports (33,86)/(33,84); wire (33,84)-(33,83) to Bus31 bar y=83
    drop("827627569", "1595009737"); place("brk", 33, 84, NAME="BRK31"); wire(33, 82, 33, 83)
    move("1849060553", 37, 83)
    # bus 30 (6113 MVA): unit (24,16) T (27,16), wire (27,16)-(27,17) to Bus30 bar y=17 -> unit up 3
    drop("1580457468"); move("993049547", 24, 13); place("brk", 27, 15, NAME="BRK30"); move("1599896956", 25, 17)
    # France: T (23,49); MM shifted up 1 -> ports (23,49)/(23,51); tie breaker (23,51)-(23,55)=Bus39
    drop("1448384586", "1985803688"); move("1917341412", 23, 50); place("brk", 23, 53, NAME="BRKFR")
    mm = P(byid["1917341412"]); mm["S"].set("value", "1.0"); mm["P"].set("value", "PTIE"); mm["Q"].set("value", "QTIE")
    # Ph31/32/37 recorders (sources removed)
    drop("526101669", "439138242", "288677605", "890664589", "387209170", "1493628208",
         "1820306055", "103513855", "1536964255")
    # trip-command logic, rows y = 400..408 (free area below the LFDD ladder)
    for k, (name) in enumerate(("BRK30", "BRK31", "BRK32", "BRK37")):
        y = 400 + 2 * k
        place("time-sig", 6, y)
        place("compare", 10, y, X="1.0e6", OL="0", OH="1")      # IN (8,y) = time-sig O; X = trip time
        place("datalabel", 12, y, Name=name)

    # ---- 2. out-of-step relay -------------------------------------------------------------------
    y = 412
    place("datalabel", 8, y, Name="Ph39"); place("sum", 10, y); place("datalabel", 10, y + 2, Name="Ph9")
    place("trig", 14, y)                                        # IN (12,y) = sum OUT; Type COS, degrees
    place("compare", 18, y, X=f"{math.cos(math.radians(a.oos_deg)):.4f}", OL="1", OH="0")
    place("datalabel", 20, y, Name="OOS1")
    place("time-sig", 6, y + 6); place("compare", 10, y + 6, X=f"{a.t_arm}", OL="0", OH="1")
    place("datalabel", 12, y + 6, Name="OOSARM")
    y2 = y + 12
    s = place("sum", 10, y2); P(s)["F"].set("value", "1")        # OOS1 + OOSARM
    place("datalabel", 8, y2, Name="OOS1"); place("datalabel", 10, y2 + 2, Name="OOSARM")
    place("compare", 14, y2, X="1.5", OL="0", OH="1")           # both true
    place("pi_ctlr", 18, y2, GP="0.0", TI="0.001", YHI="10", YLO="0", YINIT="0.0")   # latch
    place("compare", 22, y2, X="0.5", OL="0", OH="1")
    place("datalabel", 24, y2, Name="BRKFR")

    # ---- 3. tie strength ----------------------------------------------------------------------
    for i in TIE_PI:
        pp = P(byid[i])
        for k in ("Rp1", "Lp1", "XLp1", "RPUP1", "XLPUP1", "Rz1", "Lz1", "XLz1", "RPUZ1", "XLPUZ1"):
            if k in pp:
                pp[k].set("value", repr(f(pp[k].get("value")) * a.k_tie))
        print(f"tie {i}: L {f(pp['Lp1'].get('value')):.4f} H = {f(pp['Lp1'].get('value'))*2*math.pi*50:.1f} ohm")

    # ---- 4/5. loads -------------------------------------------------------------------------------
    loads = [c for c in sch if c.get("defn") == "master:fixed_load" and f(P(c)["PO"].get("value")) > 0]
    fr = byid[FR_LOAD_ID]
    move(FR_LOAD_ID, 17, 57)                                    # IA at (17,56)
    place("nodelabel", 17, 56, Name="HE39_2")
    ib = [c for c in loads if c is not fr]
    ph = sum(f(P(c)["PO"].get("value")) for c in ib)
    kl = IBERIA_LOAD_MW / 3.0 / ph
    for c in ib:
        P(c)["PO"].set("value", repr(f(P(c)["PO"].get("value")) * kl))
    fr_mw = 3 * f(P(fr)["PO"].get("value"))
    print(f"loads: Iberia {3*ph:.1f} -> {3*ph*kl:.1f} MW (x{kl:.5f}); French local load {fr_mw:.1f} MW")

    # ---- 6. generation ----------------------------------------------------------------------------
    sus = [c for c in sch if (c.get("defn") or "").endswith(":SyncUnit")]
    ibs = [c for c in sus if c.get("id") != FR_ID]
    p0 = sum(f(P(c)["P0"].get("value")) for c in ibs); ks = SYNC_TARGET_MW / p0
    for c in ibs:
        pp = P(c); new = f(pp["P0"].get("value")) * ks; sb = f(pp["Sbase"].get("value"))
        pp["P0"].set("value", f"{new:.1f}"); pp["Pmec"].set("value", f"{new/sb:.5f}")
    print(f"sync: {p0:.1f} -> {SYNC_TARGET_MW:.1f} MW (x{ks:.4f})")
    plants = [c for c in sch if (c.get("defn") or "").endswith(":RES_Plant")]
    for c in plants:
        pp = P(c); k = a.k_plant
        for n, op in (("Sbase", k), ("Cf", k), ("Ki", 1 / k), ("Lf", 1 / k)):
            pp[n].set("value", repr(f(pp[n].get("value")) * op))
    ups = [c for c in sch if c.get("defn") == "master:upramp" and abs(f(P(c)["Y2"].get("value")) + 1.7) > 1e-6]
    if len(ups) != 18:
        raise SystemExit(f"expected 18 plant upramps, found {len(ups)}")
    for c in ups:
        P(c)["Y2"].set("value", f"{f(P(c)['Y2'].get('value')) + LEVER3_PU:.6f}")
    sb_tot = sum(f(P(c)["Sbase"].get("value")) for c in plants)
    print(f"plants: Sbase total {sb_tot:.0f} MVA (x{a.k_plant}); Pref restored (+{LEVER3_PU:.4f} pu)")

    # ---- 7. France ----------------------------------------------------------------------------------
    pf_ = P(byid[FR_ID]); pfr = fr_mw - AC_EXPORT_MW - HVDC_MW
    pf_["P0"].set("value", f"{pfr:.1f}"); pf_["Pmec"].set("value", f"{pfr/200000.0:.6f}")
    print(f"France: P0 {pfr:.1f} MW (French load {fr_mw:.0f} - AC export {AC_EXPORT_MW:.0f} - HVDC {HVDC_MW:.0f})")

    if not a.dry:
        tree.write(a.dst, encoding="utf-8"); print("written", a.dst)


if __name__ == "__main__":
    main()
