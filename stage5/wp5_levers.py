"""WP5 levers as parameter edits on a network .pscx (Session 20). Project must NOT be loaded (skill P12).

Lever 1  --kc K      multiply every master:pi_section's shunt capacitance by K (Cp1, Cz1 x K; XCp1, XCz1 / K).
                     R and X untouched. Session 20 measured the model's charging at 4.2 Gvar (sum Cp1 = 84.45 uF,
                     400 kV); the Spanish 400 kV grid has roughly 11.5 Gvar (21,000 km x 0.55 Mvar/km).
Lever 2  --qscale S  multiply every master:fixed_load QO by S (0 = no reactive demand, <0 = capacitive DSO
                     injection). In ib4hv this is already 0 (ib4q0 lineage).
Lever 4  --tap T     set the tap const of the five collector-bus transformers (IEEE 19-33, 20-34, 22-35, 23-36,
                     29-38). Convention, read off the IEEE-39 power flow this model reproduces (G1): the tap is
                     network side / collector side at no load (tap 1.07 on 19-33 gives bus 19 1.050, bus 33 0.997).
                     So T = 1/1.04 = 0.962 puts the collector ~4 % above its 400 kV bus (report p.122, event 3).
--dry                print what would change.

usage: python stage5\\wp5_levers.py --pscx C:\\PSCAD_work\\ib4hv.pscx [--kc 2.5] [--qscale 0] [--tap 0.962] [--dry]
"""
import argparse
import xml.etree.ElementTree as ET

G = 18
# collector-bus transformers: iid -> (bus, IEEE branch, IEEE tap)  (identified in S20 by Xl and position)
COLLECTOR_XF = {
    "790392911": (33, "19-33", 1.070),
    "1726223889": (34, "20-34", 1.009),
    "807978177": (35, "22-35", 1.025),
    "1798631683": (36, "23-36", 1.000),
    "1618177572": (38, "29-38", 1.025),
}


def f(v):
    return float(str(v).split("[")[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--kc", type=float)
    ap.add_argument("--qscale", type=float)
    ap.add_argument("--tap", type=float)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    t = ET.parse(a.pscx)
    m = [d for d in t.getroot().iter("Definition") if d.get("name") == "Main"][0]
    users = m.find("schematic").findall("User")

    if a.kc:
        c0 = c1 = 0.0
        for u in users:
            if u.get("defn") != "master:pi_section":
                continue
            for p in u.find("paramlist").findall("param"):
                n = p.get("name")
                if n in ("Cp1", "Cz1"):
                    if n == "Cp1":
                        c0 += f(p.get("value"))
                    p.set("value", repr(f(p.get("value")) * a.kc))
                    if n == "Cp1":
                        c1 += f(p.get("value"))
                elif n in ("XCp1", "XCz1"):
                    p.set("value", repr(f(p.get("value")) / a.kc))
        q = lambda c: 400 ** 2 * 2 * 3.141592653589793 * 50 * c * 1e-6
        print(f"lever 1: sum Cp1 {c0:.2f} -> {c1:.2f} uF, charging {q(c0):.0f} -> {q(c1):.0f} Mvar at 400 kV")

    if a.qscale is not None:
        n = 0
        for u in users:
            if u.get("defn") == "master:fixed_load":
                for p in u.find("paramlist").findall("param"):
                    if p.get("name") == "QO":
                        p.set("value", repr(f(p.get("value")) * a.qscale)); n += 1
        print(f"lever 2: QO x {a.qscale} on {n} loads")

    if a.tap:
        consts = [u for u in users if u.get("defn") == "master:const"]
        for u in users:
            if u.get("id") not in COLLECTOR_XF:
                continue
            bus, br, tap0 = COLLECTOR_XF[u.get("id")]
            x, y = int(u.get("x")) // G, int(u.get("y")) // G
            # its tap const is the one whose value equals the IEEE tap, within 5 grid units
            cand = [c for c in consts if abs(int(c.get("x")) // G - x) <= 5 and abs(int(c.get("y")) // G - y) <= 5
                    and abs(f({p.get("name"): p.get("value") for p in c.find("paramlist")}["Value"]) - tap0) < 1e-6]
            if len(cand) != 1:
                raise SystemExit(f"bus {bus}: expected one tap const with value {tap0}, found {len(cand)}")
            for p in cand[0].find("paramlist").findall("param"):
                if p.get("name") == "Value":
                    print(f"lever 4: bus {bus} ({br}) tap const {cand[0].get('id')}: {p.get('value')} -> {a.tap}")
                    p.set("value", repr(a.tap))
    if not a.dry:
        t.write(a.pscx, encoding="utf-8")
        print("written", a.pscx)


if __name__ == "__main__":
    main()
