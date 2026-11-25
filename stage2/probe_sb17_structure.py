"""Read sb17.pscx structure and dump the machine-group `User`/`Wire` XML verbatim.

Purpose: build the SyncUnit definition XML from PSCAD's own stored components instead of
re-creating them by hand (PLAN F3b/F3c route). Read-only.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(r"C:\PSCAD_work\sb17.pscx")


def main() -> None:
    tree = ET.parse(SRC)
    root = tree.getroot()
    defs = {d.get("name"): d for d in root.iter("Definition")}
    print("definitions:", list(defs))
    main_def = defs["Main"]
    sch = main_def.find("schematic")
    users = sch.findall("User")
    wires = sch.findall("Wire")
    print(f"Main canvas: {len(users)} users, {len(wires)} wires")

    rows = []
    for u in users:
        pl = u.find("paramlist")
        params = {}
        if pl is not None:
            for p in pl.findall("param"):
                params[p.get("name")] = p.get("value")
        rows.append({
            "id": u.get("id"),
            "defn": u.get("defn"),
            "x": int(u.get("x")), "y": int(u.get("y")),
            "w": int(u.get("w")), "h": int(u.get("h")),
            "orient": u.get("orient"),
            "nparams": len(params),
            "name": params.get("Name", ""),
        })
    for r in sorted(rows, key=lambda r: (r["y"], r["x"])):
        print(f'{r["defn"]:<28} id={r["id"]:<12} x={r["x"]//18:>3} y={r["y"]//18:>3} '
              f'{r["w"]//18}x{r["h"]//18} or={r["orient"]} npar={r["nparams"]:>3} Name={r["name"]!r}')

    Path("sb17_structure.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("\nwires:")
    for w in wires:
        vs = [(int(v.get("x")) // 18, int(v.get("y")) // 18) for v in w.findall("vertex")]
        print(f'  id={w.get("id"):<12} verts={vs}')


if __name__ == "__main__":
    main()
