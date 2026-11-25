"""List every wire of sb17's Main canvas with absolute (grid) endpoints, so the core
machine-group wires can be selected by id with evidence rather than by guesswork."""
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(r"C:\PSCAD_work\sb17.pscx")

# Absolute port coordinates measured with pscad_get_ports (grid units) for the components
# that matter. Port name -> (x, y).
PORTS = {
    # sync_machine 1280433174
    "telect": (16, 30), "speed": (18, 34), "tmeco": (16, 32), "efo": (16, 26),
    "mvit": (22, 26), "cfldn": (20, 26), "efldn": (18, 26), "tmech": (20, 34),
    "NS": (22, 30), "N": (19, 30),
    # excac_2016_2 974437483
    "IFD": (20, 26), "EFD0": (16, 24), "EFD": (18, 26), "VREF": (20, 20),
    "VREFO": (18, 20), "VIT": (22, 24),
    # consts
    "c_vref": (20, 20), "c_torque": (20, 34), "c_one": (30, 28), "c_enab": (42, 14),
    # labels
    "l_efd0": (10, 24), "l_vrefo": (14, 20), "l_vit": (28, 25), "l_exinit": (24, 50),
    "l_pout": (44, 40), "l_qout": (44, 44), "l_vt": (44, 48), "l_v400": (44, 52),
    "l_vinf": (44, 56), "l_pgrid": (44, 58), "l_qgrid": (44, 62), "l_wspd": (18, 38),
    # sources / meters
    "vmet18": (30, 30), "gsu_n1": (36, 30), "source_n3": (57, 30),
    "upramp_i": (14, 50), "upramp_o": (18, 50), "timesig_o": (14, 50),
}


def name_of(pt):
    hits = [k for k, v in PORTS.items() if v == pt]
    return "/".join(hits) if hits else ""


def main() -> None:
    root = ET.parse(SRC).getroot()
    main_def = [d for d in root.iter("Definition") if d.get("name") == "Main"][0]
    sch = main_def.find("schematic")
    users = {u.get("id"): u for u in sch.findall("User")}

    for w in sch.findall("Wire"):
        wx, wy = int(w.get("x")) // 18, int(w.get("y")) // 18
        pts = [(wx + int(v.get("x")) // 18, wy + int(v.get("y")) // 18) for v in w.findall("vertex")]
        print(f'id={w.get("id"):<12} {pts}  start={name_of(pts[0])!r} end={name_of(pts[-1])!r}')


if __name__ == "__main__":
    main()
