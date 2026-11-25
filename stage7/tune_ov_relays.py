"""Stage 7 - Case B: assign the fleet's observed OV settings to the plants (S22).

Source: data/parameters.md p.160-172 (report pages), the six settings actually observed in the Spanish /
Portuguese fleet:

    1.089 pu / 1.5 s      1.10 pu / 0 s       1.10 pu / 0.5 s
    1.111 pu / (delay not printed)             1.139 pu / 0.2 s     1.15 pu / 0.6 s

The 1.111 pu entry carries no delay in the report; **0.1 s is assumed** (between the 0 s and 0.2 s
entries) and the assumption is recorded rather than hidden.

Assignment is deterministic: plant k (document order, 1..18) gets settings[(k-1) % 6], so every setting
appears three times and the mapping can be reproduced. Only block 1 is used (Nsub = 1, Share1 = 1.0,
unchanged).

usage: python stage7/tune_ov_relays.py --pscx X [--dry-run]
"""
import argparse
import xml.etree.ElementTree as ET

SETTINGS = [
    ("1.089", "1.5"),
    ("1.10", "0"),
    ("1.10", "0.5"),
    ("1.111", "0.1"),      # delay not printed in the report; 0.1 s assumed
    ("1.139", "0.2"),
    ("1.15", "0.6"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--dry-run", action="store_true")
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
    print(f"{len(plants)} plants; mapping (plant -> Vt1 / Tt1):")
    for k, c in enumerate(plants, 1):
        vt, tt = SETTINGS[(k - 1) % len(SETTINGS)]
        if not a.dry_run:
            pl = c.find("paramlist")
            for q in pl.findall("param"):
                if q.get("name") == "Vt1":
                    q.set("value", vt)
                elif q.get("name") == "Tt1":
                    q.set("value", tt)
        print(f"   plant {k:2d}: {vt:>6s} pu / {tt:>4s} s")

    if a.dry_run:
        print("dry run - nothing written")
        return
    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - block-1 OV relays tuned across 18 plants")


if __name__ == "__main__":
    main()
