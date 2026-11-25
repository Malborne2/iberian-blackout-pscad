"""Split the single global FRC Force net into per-plant Force nets (S22, Stage 6 prerequisite).

Measured facts this script relies on (run 85 and the XML, both recorded in RUNLOG):
  * all 18 plants' `Force` inputs sit on ONE net named FRC, driven by the const at (84,8);
  * the net only reaches 16 plants - plants 1 and 16 (channel numbering) have no FRC label on
    their Force pin, which is exactly why they survived the forced trip in run 85;
  * the `RES_Plant[k]` channel index follows **ascending component id**, verified against the
    survivors and against four plant MW values (1: 356 MW / 400 MVA, 16: 314 / 348,
    17: 2,817 / 3,132, 18: 2,271 / 2,550).

The split is signal-only (0 nodes): each Force pin keeps its (renamed) datalabel, and one driver is
placed in a free row, connected purely by net name.

usage: python stage6/split_force_net.py --pscx C:\\PSCAD_work\\ib4hv.pscx --force 2,4,11 --t 3.0
"""
import argparse
import copy
import xml.etree.ElementTree as ET

G = 18
ID = [1350006001]

# channel index -> component id (ascending id order), verified in RUNLOG S22
CHANNELS = [
    "740287642", "1700000002", "1700000011", "1700000020", "1700000030", "1700000039",
    "1700000048", "1700000057", "1700000066", "1700000075", "1700000084", "1700000094",
    "1700000103", "1700000112", "1700000122", "1700000131", "1700000140", "2127906943",
]
NO_LABEL = {1, 16}


def nid():
    ID[0] += 1
    return str(ID[0])


def grid(el):
    try:
        return (int(el.get("x")) // G, int(el.get("y")) // G)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pscx", required=True)
    ap.add_argument("--force", default="", help="comma separated channel indices to trip")
    ap.add_argument("--t", default="3.0")
    a = ap.parse_args()
    # --force accepts "2,4,11" (all at --t) or per-channel times "6:3.0,7:3.0,2:3.2"
    forced = {}
    for item in a.force.split(","):
        item = item.strip()
        if not item or not item.split(":")[0].isdigit():
            continue
        ch, _, tt = item.partition(":")
        forced[int(ch)] = float(tt) if tt else float(a.t)

    tree = ET.parse(a.pscx)
    root = tree.getroot()
    main_def = [d for d in root.find("definitions") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")

    def walk(el):
        for c in el:
            yield c
            if c.tag != "User":
                yield from walk(c)

    allc = list(walk(sch))
    plants = {}
    for c in allc:
        if c.tag == "User" and (c.get("defn") or "").endswith(":RES_Plant"):
            plants[c.get("id")] = c
    if len(plants) != 18:
        raise SystemExit(f"expected 18 plants, found {len(plants)}")

    labels = [c for c in allc if c.tag == "User" and (c.get("defn") or "").endswith(":datalabel")]
    by_grid = {}
    for c in labels:
        q = {p.get("name"): p.get("value") for p in c.find("paramlist").findall("param")}
        by_grid.setdefault(grid(c), []).append((c, q.get("Name")))

    renamed = []
    for ch, cid in enumerate(CHANNELS, 1):
        el = plants[cid]
        gx, gy = grid(el)
        pin = (gx - 3, gy)          # measured: Force sits 3 grid units left of the instance origin
        hit = [(c, nm) for c, nm in by_grid.get(pin, []) if nm == "FRC"]
        if ch in NO_LABEL:
            if hit:
                raise SystemExit(f"channel {ch}: expected no FRC label at {pin}, found {len(hit)}")
            continue
        if len(hit) != 1:
            raise SystemExit(f"channel {ch}: expected 1 FRC label at {pin}, found {len(hit)}")
        for p in hit[0][0].find("paramlist").findall("param"):
            if p.get("name") == "Name":
                p.set("value", f"FRC{ch}")
        renamed.append((ch, pin))

    print(f"renamed {len(renamed)} Force labels to FRC<channel>; "
          f"unlabelled (as measured): {sorted(NO_LABEL)}")

    # ---- drivers in a free row ----------------------------------------------------------
    proto_const = [c for c in allc if (c.get("defn") or "") == "master:const"][0]
    proto_cmp = [c for c in allc if (c.get("defn") or "") == "master:compare"][0]
    proto_lab = labels[0]
    proto_tsig = [c for c in allc if (c.get("defn") or "") == "master:time-sig"][0]

    def place(proto, x, y, **vals):
        el = copy.deepcopy(proto)
        el.set("id", nid())
        el.set("x", str(x * G))
        el.set("y", str(y * G))
        pl = el.find("paramlist")
        for q in pl.findall("param"):
            if q.get("name") in vals:
                q.set("value", str(vals.pop(q.get("name"))))
        for k, v in vals.items():
            ET.SubElement(pl, "param", {"name": k, "value": str(v)})
        sch.append(el)
        return el

    # measured geometry (this project): const OUT = (x, y+3); compare I = (x-2, y), O = (x+2, y);
    # time-sig OUT = (x+2, y); the const symbol spans 4 grid rows, so drivers are 8 rows apart.
    place(proto_tsig, 6, 404, Name="")                      # OUT at (8,404)
    place(proto_lab, 8, 404, Name="T6")

    n_forced = 0
    for i, (ch, _) in enumerate(sorted(renamed)):
        y = 412 + 8 * i
        if ch in forced:
            place(proto_cmp, 14, y, X=forced[ch], OL="0", OH="1")
            place(proto_lab, 12, y, Name="T6")              # compare I
            place(proto_lab, 16, y, Name=f"FRC{ch}")        # compare O
            n_forced += 1
        else:
            place(proto_const, 14, y, Name="", Value="0")
            place(proto_lab, 14, y + 2, Name=f"FRC{ch}")    # const OUT = (x, y+2)
    print(f"drivers built: {n_forced} time-triggered "
          f"({', '.join(f'{c}@{t:g}s' for c, t in sorted(forced.items()))}), "
          f"{len(renamed) - n_forced} held at 0")

    # the global FRC net is KEPT: HVDC_T's own `Force` input reads it (build error without it)
    glob = [c for c in allc if (c.get("defn") or "") == "master:const" and grid(c) == (84, 8)]
    for c in glob:
        for q in c.find("paramlist").findall("param"):
            if q.get("name") == "Value":
                q.set("value", "0")
    print(f"global FRC driver kept at Value 0 for HVDC_T ({len(glob)} const)")

    tree.write(a.pscx, encoding="utf-8", xml_declaration=True)
    print(f"written: {a.pscx} - per-plant Force nets (0 nodes)")


if __name__ == "__main__":
    main()
