"""Apply the Q(V) droop at the report's own target, with the zero-delay relays parked (S22, Stage 7).

Measured starting points (`run 100`, steady 5-6 s, no forcing):

    collector group        channels        steady VDF
    A (Granada + bulk)     1, 18           0.9789
    B                      2, 3, 4         0.9908
    C                      5 ... 11        0.9788
    D                      12, 13, 14      1.0073
    E                      15, 16, 17      1.0322

The report has Granada at **1.061 pu** at 12:32:56, so the target is `Vset = 1.06`, not run 101's 1.10.
Because each group starts at a different point, the droop injects a different amount per collector even
with one set-point - that IS the per-collector action, and the achieved voltage is measured.

Run 101 also showed that the three channels assigned **Tt1 = 0** (ch1, ch7, ch13) fire on the start-up
overshoot. They are **parked at 0.05 s** for this approach run and the deviation is recorded; the gate run
must restore 0 s.

usage: python stage7/apply_droop_target.py --pscx X [--vset 1.06] [--park 0.05]
"""
import argparse
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--vset", default="1.06")
    ap.add_argument("--park", default="0.05")
    a = ap.parse_args()

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]

    def walk(el):
        for c in el:
            yield c
            if c.tag != "User":
                yield from walk(c)

    plants = [c for c in walk(main_def.find("schematic"))
              if c.tag == "User" and (c.get("defn") or "").endswith(":RES_Plant")]
    plants.sort(key=lambda c: int(c.get("id")))          # psout channel order

    parked = []
    for k, c in enumerate(plants, 1):
        pl = c.find("paramlist")
        for q in pl.findall("param"):
            if q.get("name") == "Qmode":
                q.set("value", "1")
            elif q.get("name") == "Vset":
                q.set("value", a.vset)
            elif q.get("name") == "Tt1" and float(q.get("value")) == 0.0:
                q.set("value", a.park)
                parked.append(k)

    print(f"written: {a.pscx}")
    print(f"  Qmode 1, Vset {a.vset} pu on {len(plants)} plants")
    print(f"  Tt1 parked {a.park} s on channels {parked} (deviation - restore 0 s for the gate run)")


if __name__ == "__main__":
    main()
