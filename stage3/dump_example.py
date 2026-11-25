"""Record a PSCAD example project exactly as shipped: canvases, components, parameters, wiring.

Skill P9 / PLAN F2 Stage 3: "record how each port is wired and every parameter. This record is the
specification -- copy it, do not improve it."

Reads the .pscx directly (plain XML) so the shipped example is never modified, and writes Markdown.

Usage:
    python stage3/dump_example.py "<path to .pscx>" "<output .md>"
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

GRID = 18            # the .pscx stores grid * 18


def grid(v: str | None) -> int | None:
    try:
        return int(v) // GRID
    except (TypeError, ValueError):
        return None


def params_of(el: ET.Element) -> dict[str, str]:
    out: dict[str, str] = {}
    pl = el.find("paramlist")
    if pl is not None:
        for p in pl.findall("param"):
            out[p.get("name", "")] = p.get("value", "")
    return out


def wire_points(w: ET.Element) -> list[tuple[int, int]]:
    x0, y0 = grid(w.get("x")) or 0, grid(w.get("y")) or 0
    return [(x0 + (grid(v.get("x")) or 0), y0 + (grid(v.get("y")) or 0)) for v in w.findall("vertex")]


def main() -> None:
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    root = ET.parse(src).getroot()

    lines: list[str] = []
    lines.append(f"# Example record: `{src.name}`")
    lines.append("")
    lines.append("Source of every line below: the shipped `.pscx` itself (read-only, parsed offline).")
    lines.append("Coordinates are PSCAD grid units. This is the specification to copy, not to improve")
    lines.append("(PLAN F2 Stage 3, skill P9).")
    lines.append("")

    for d in root.iter("Definition"):
        name = d.get("name") or "?"
        sch = d.find("schematic")
        users = sch.findall("User") if sch is not None else []
        wires = sch.findall("Wire") if sch is not None else []
        if not users:
            continue
        header = d.find("paramlist")
        desc = ""
        if header is not None:
            for p in header.findall("param"):
                if p.get("name") == "Description":
                    desc = p.get("value") or ""
        ports = []
        svg = d.find("svg")
        if svg is not None:
            for port in svg.findall("port"):
                ports.append(f'{port.get("name")}(dim {port.get("dim")}, {port.get("mode")})')

        lines.append(f"## Canvas `{name}`" + (f" - {desc}" if desc else ""))
        lines.append("")
        if ports:
            lines.append(f"Module ports: {', '.join(ports)}")
            lines.append("")

        lines.append("| component | type | at | parameters |")
        lines.append("| --- | --- | --- | --- |")
        for u in users:
            pr = params_of(u)
            at = f'({grid(u.get("x"))},{grid(u.get("y"))})'
            name_field = pr.pop("Name", "")
            label = f'`{name_field}`' if name_field else ""
            pstr = ", ".join(f"`{k}`={v}" for k, v in pr.items() if v not in ("", "0", "-1"))
            if len(pstr) > 900:
                pstr = pstr[:900] + " ..."
            lines.append(f'| {u.get("defn")} {label} | | {at} | {pstr} |')
        lines.append("")

        if wires:
            lines.append("Wiring (absolute endpoints, intermediate vertices included):")
            lines.append("")
            for w in wires:
                pts = wire_points(w)
                lines.append(f"- {' -> '.join(f'({x},{y})' for x, y in pts)}")
            lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}  ({len(lines)} lines, {out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
