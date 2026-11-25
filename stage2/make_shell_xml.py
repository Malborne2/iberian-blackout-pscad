"""Build module-shell definitions from XML, using PSCAD's own `Gen1` symbol as the template.

Used for the shells PLAN F3 lists. The four rules found by F1-T4 (see PLAN F3c) are applied here:

  1. every parameter is `content_type="Constant"` (so it can be substituted into a field);
  2. a `master:import` with the parameter's name is placed inside the canvas (publishes it);
  3. the definition gets a **unique id** (never the template's);
  4. the form is `<form><category>…</category></form>` — no `<categories>` wrapper.

Usage:
    python make_shell_xml.py TestShell 1200000005           # the T4 bench shell
    python make_shell_xml.py --spec syncunit.json           # a spec from a JSON file

Spec JSON:
    {"name": "SyncUnit", "id": "1200000101", "port": "T", "desc": "...",
     "params": [{"name": "Sbase", "desc": "...", "unit": "MVA", "value": 300}, ...]}
"""
from __future__ import annotations

import copy
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

EXAMPLE = Path(r"C:\Users\Public\Documents\PSCAD\5.1.0\Examples\sync_machines\sync_multiplemachines.pscx")
SHELLS = Path(__file__).with_name("shells")


def parameter_xml(p: dict) -> str:
    return (
        f'    <parameter desc="{p["desc"]}" name="{p["name"]}" group="{p.get("group", "")}"'
        f' unit="{p.get("unit", "")}" min="{p.get("min", "-1e+308")}" max="{p.get("max", "+1e+308")}"'
        f' content_type="Constant" type="{p.get("type", "Real")}" helpmode="Append"'
        f' intent="Input" dim="1" animate="false">\n'
        f'      <value><![CDATA[{p["value"]}]]></value>\n'
        "      <cond />\n      <help />\n      <vis />\n    </parameter>\n"
    )


def build(name: str, def_id: str, params: list[dict], port: str = "T", desc: str = "") -> Path:
    tree = ET.parse(EXAMPLE)
    gen1 = next(d for d in tree.getroot().iter("Definition") if d.get("name") == "Gen1")
    d = copy.deepcopy(gen1)

    d.set("name", name)
    d.set("instances", "0")
    d.set("id", def_id)
    d.set("crc", "0")
    d.set("date", "0")
    for tag in ("script", "graphics"):
        for el in d.findall(tag):
            d.remove(el)

    pl = d.find("paramlist")
    if pl is None:
        pl = ET.SubElement(d, "paramlist")
    pl.clear()
    ET.SubElement(pl, "param", {"name": "Description", "value": desc or name})

    old_form = d.find("form")
    idx = list(d).index(old_form) if old_form is not None else 0
    if old_form is not None:
        d.remove(old_form)
    body = "".join(parameter_xml(p) for p in params)
    form = ET.fromstring(
        f'<form name="{name}" w="320" h="400" splitter="60">'
        f'<category name="Configuration" visible="true">\n{body}  </category>\n</form>'
    )
    d.insert(idx, form)

    svg = d.find("svg")
    svg.find("port").set("name", port)
    for text in svg.iter("text"):
        if (text.text or "").strip() in ("S", "T"):
            text.text = port

    sch = d.find("schematic")
    for child in list(sch):
        if child.tag != "paramlist":
            sch.remove(child)
    ET.SubElement(
        sch, "User",
        {"classid": "UserCmp", "name": "", "defn": "master:xnode", "id": "15604105",
         "x": "450", "y": "378", "w": "20", "h": "33", "z": "1", "orient": "0",
         "link": "-1", "q": "4", "disable": "false"},
    )
    pl2 = ET.SubElement(sch[-1], "paramlist", {"link": "-1", "name": "", "crc": "37312176"})
    ET.SubElement(pl2, "param", {"name": "Name", "value": port})

    refs = d.find("references")
    if refs is None:
        refs = ET.SubElement(d, "references")
    refs.clear()
    ET.SubElement(refs, "using", {"namespace": "master"})

    SHELLS.mkdir(parents=True, exist_ok=True)
    out = SHELLS / f"{name}.xml"
    out.write_text(ET.tostring(d, encoding="unicode"), encoding="utf-8")
    print("written:", out)
    print("  port      :", port)
    print("  parameters:", [p["name"] for p in params])
    return out


T4_PARAMS = [
    {"name": "Sbase", "desc": "Power per phase", "unit": "MW", "value": 10.0, "min": "0.0", "max": "10000.0"},
    {"name": "H", "desc": "Second parameter (unused inside)", "unit": "s", "value": 3.0, "min": "0.0", "max": "100.0"},
]

SYNCUNIT_PARAMS = [
    {"name": "Sbase", "desc": "Rated MVA", "unit": "MVA", "value": 300.0, "min": "1.0"},
    {"name": "Vbase", "desc": "Rated line-to-line kV", "unit": "kV", "value": 18.0, "min": "0.1"},
    {"name": "H", "desc": "Inertia constant", "unit": "s", "value": 3.117, "min": "0.1"},
    {"name": "P0", "desc": "Initial active power", "unit": "MW", "value": 60.0},
    {"name": "Q0", "desc": "Initial reactive power", "unit": "Mvar", "value": 2.4},
    {"name": "V0", "desc": "Initial terminal voltage", "unit": "pu", "value": 1.0, "min": "0.1"},
    {"name": "Ph0", "desc": "Initial rotor angle", "unit": "rad", "value": 0.0},
    {"name": "Vctl", "desc": "0 = slow Q regulator, 1 = fast AVR", "unit": "", "value": 0, "type": "Integer", "min": "0", "max": "1"},
    {"name": "Tstart", "desc": "Exciter release time", "unit": "s", "value": 0.5, "min": "0.0"},
]


def main() -> None:
    if "--spec" in sys.argv:
        spec = json.loads((SHELLS / sys.argv[sys.argv.index("--spec") + 1]).read_text())
        build(spec["name"], spec["id"], spec["params"], spec.get("port", "T"), spec.get("desc", ""))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "SyncUnit":
        build("SyncUnit", sys.argv[2] if len(sys.argv) > 2 else "1200000101",
              SYNCUNIT_PARAMS, desc="Synchronous unit (machine + AVR)")
        return
    name = sys.argv[1] if len(sys.argv) > 1 else "TestShell"
    def_id = sys.argv[2] if len(sys.argv) > 2 else "1200000001"
    build(name, def_id, T4_PARAMS, desc="T4 shell test")


if __name__ == "__main__":
    main()
