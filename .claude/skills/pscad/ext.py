"""
Extra tools for the PSCAD MCP server (pscad_mcp).

The base server (C:\\GitHub\\PSCAD-MCP, commit f864c9f) cannot read port
positions, create buses or node labels, resize a canvas, copy components or
definitions between projects, or report node counts. Building a large model
without those forces guessing, which is what broke the previous attempt.

INSTALL (two steps, then restart the MCP server):
  1. Copy this file to   C:\\GitHub\\PSCAD-MCP\\pscad_mcp\\ext.py
  2. Add this line just above ``def main()`` in pscad_mcp\\server.py:
         from . import ext  # noqa: E402,F401  (registers extra tools)

STATUS (installed 2026-11-15, registers with the server; 68 tools total): every mhi.pscad call below was checked against the signatures and
docstrings of the installed library (mhi-pscad 3.1.3). The tools have NOT yet
been run against a live PSCAD. First use = test: see "Self-test" in SKILL.md.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Optional

import mhi.psout

from .server import _get_canvas, _safe, mcp
from .session import session

# ---------------------------------------------------------------------------
# Inspecting components: ports, bounds, legal parameter values
# ---------------------------------------------------------------------------


def _port_dict(p) -> dict[str, Any]:
    return {
        "name": p.name,
        "x": p.x,
        "y": p.y,
        "dim": p.dim,
        "type": str(p.type),
        "electrical": str(p.electrical),
        "signal": str(p.signal),
    }


@mcp.tool()
def pscad_get_ports(project: str, iid: int, canvas: str = "Main") -> dict[str, Any]:
    """Return every active port of a component: name, absolute x/y (grid units), dimension, type.

    ALWAYS call this after placing or moving a component and before wiring it.
    Wire to the x/y reported here; never to coordinates you calculated.
    `dim` is the electrical dimension (1 = single conductor, 3 = three-phase).
    `type` tells input / output / electrical. Only components have ports;
    wires and buses raise an error.
    """

    def _ports() -> dict[str, Any]:
        comp = _get_canvas(project, canvas).component(iid)
        return {
            "iid": iid,
            "defn_name": comp.defn_name,
            "location": tuple(comp.location),
            "ports": [_port_dict(p) for p in comp.ports().values()],
        }

    return _safe(_ports)


@mcp.tool()
def pscad_get_bounds(project: str, iids: list[int], canvas: str = "Main") -> dict[str, Any]:
    """Return the bounding box (left, top, right, bottom, grid units) of components.

    Use to check that a new component's box does not overlap any other
    component, wire or bus before building.
    """

    def _bounds() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        comps = [cv.component(i) for i in iids]
        rects = cv.bounds(comps)
        return {
            "bounds": [
                {"iid": i, "left": r.left, "top": r.top, "right": r.right, "bottom": r.bottom}
                for i, r in zip(iids, rects)
            ]
        }

    return _safe(_bounds)


@mcp.tool()
def pscad_get_parameter_range(project: str, iid: int, parameter: str, canvas: str = "Main") -> dict[str, Any]:
    """Return the legal values (or min/max) of one component parameter.

    Call this before setting any choice-type parameter. It tells you the
    exact accepted values so you do not guess between a label and an index.
    """

    def _range() -> dict[str, Any]:
        comp = _get_canvas(project, canvas).component(iid)
        rng = comp.range(parameter)
        if isinstance(rng, range):
            return {"parameter": parameter, "kind": "int_range", "start": rng.start, "stop": rng.stop}
        return {"parameter": parameter, "kind": type(rng).__name__, "values": [str(v) for v in rng]}

    return _safe(_range)


@mcp.tool()
def pscad_list_canvas_objects(project: str, canvas: str = "Main", defn: Optional[str] = None) -> dict[str, Any]:
    """Fast listing of everything on a canvas: iid, definition, location, bounds.

    Unlike pscad_list_components this does not read each component's
    parameters, so it stays fast on canvases with hundreds of components.
    `defn` filters by definition, e.g. "master:source3", "Bus", "TLine".
    """

    def _list() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        comps = cv.find_all(defn) if defn else cv.components()
        rects = cv.bounds(comps) if comps else []
        out = []
        for c, r in zip(comps, rects):
            out.append(
                {
                    "iid": c.iid,
                    "defn_name": c.defn_name,
                    "bounds": [r.left, r.top, r.right, r.bottom],
                }
            )
        return {"count": len(out), "objects": out}

    return _safe(_list)


# ---------------------------------------------------------------------------
# Canvas: size, free space, buses, node labels
# ---------------------------------------------------------------------------


@mcp.tool()
def pscad_get_canvas_settings(project: str, canvas: str = "Main") -> dict[str, Any]:
    """Return a canvas's settings (paper `size`, `orient`, ...) and its size in grid units."""

    def _get() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        size = cv.size
        return {"settings": dict(cv.parameters()), "grid_size": [size[0], size[1]]}

    return _safe(_get)


@mcp.tool()
def pscad_set_canvas_settings(project: str, parameters: dict[str, Any], canvas: str = "Main") -> dict[str, Any]:
    """Change canvas settings. Main use: enlarge the drawing area.

    `size` is one of '85X11', '11X17', '17X22', '22X34', '34X44', '100X100';
    `orient` is 'PORTRAIT' or 'LANDSCAPE'. Everything placed outside the
    canvas is moved onto its corner when PSCAD saves, so enlarge FIRST.
    """

    def _set() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        cv.parameters(**parameters)
        size = cv.size
        return {"settings": dict(cv.parameters()), "grid_size": [size[0], size[1]]}

    return _safe(_set)


@mcp.tool()
def pscad_find_empty_rect(
    project: str, width: int, height: int, near: list[int], canvas: str = "Main"
) -> dict[str, Any]:
    """Find the empty rectangle of the given size (grid units) closest to point `near` = [x, y]."""

    def _find() -> dict[str, Any]:
        r = _get_canvas(project, canvas).closest_empty_rect(width, height, tuple(near))
        return {"left": r.left, "top": r.top, "right": r.right, "bottom": r.bottom}

    return _safe(_find)


@mcp.tool()
def pscad_create_bus(project: str, vertices: list[list[int]], canvas: str = "Main") -> dict[str, Any]:
    """Draw a bus through the given [x, y] points (grid units). Returns its iid.

    Give the bus a name afterwards with pscad_set_component_parameters; read
    the parameter names first with pscad_get_component_parameters. Every bus
    in a project needs a unique name.
    """

    def _bus() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        bus = cv.create_bus(*[tuple(v) for v in vertices])
        return {"iid": bus.iid, "vertices": [list(p) for p in bus.vertices()]}

    return _safe(_bus)


@mcp.tool()
def pscad_create_node_label_pair(
    project: str,
    from_point: list[int],
    to_point: list[int],
    label: str,
    electrical: bool,
    canvas: str = "Main",
) -> dict[str, Any]:
    """Connect two points by a pair of named node labels instead of a wire.

    Use where a wire would have to cross other components (a wire that
    crosses a bus or a port connects to it). `electrical=True` for power
    nodes, False for control/data signals. PSCAD may append "_2", "_3" to
    make the name unique: use the returned `label`, not the one you passed.
    Both ends must have the same dimension (3-phase to 3-phase).
    """

    def _label() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        name = cv.create_connection(tuple(from_point), tuple(to_point), label=label, electrical=electrical)
        return {"label": name}

    return _safe(_label)


# ---------------------------------------------------------------------------
# Copying: components within a project, groups and definitions across projects
# ---------------------------------------------------------------------------


@mcp.tool()
def pscad_clone_component(project: str, iid: int, x: int, y: int, canvas: str = "Main") -> dict[str, Any]:
    """Copy one component (with all its parameters) to a new location on the same canvas."""

    def _clone() -> dict[str, Any]:
        comp = _get_canvas(project, canvas).component(iid)
        new = comp.clone(x, y)
        return {"iid": new.iid, "defn_name": new.defn_name, "location": tuple(new.location)}

    return _safe(_clone)


@mcp.tool()
def pscad_copy_region(project: str, x1: int, y1: int, x2: int, y2: int, canvas: str = "Main") -> dict[str, Any]:
    """Select everything inside a rectangle (grid units) and copy it to PSCAD's clipboard.

    This is how a working, already-wired group (e.g. machine + exciter +
    governor in a PSCAD example) is lifted with its wiring intact. Follow
    with pscad_paste on the destination canvas.
    """

    def _copy() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        cv.clear_selection()
        cv.select_components(x1, y1, x2, y2)
        ok = cv.copy()
        return {"copied": bool(ok)}

    return _safe(_copy)


@mcp.tool()
def pscad_paste(project: str, x: int, y: int, canvas: str = "Main", mode: str = "paste") -> dict[str, Any]:
    """Paste PSCAD's clipboard onto a canvas at (x, y) grid units.

    mode: "paste" (plain), "rename" (give pasted components unique names and
    fix references between them -- use when pasting a second copy of a
    group), or "transfer" (also bring a copied user-component's definition
    into this project). Afterwards call pscad_list_canvas_objects to get the
    new iids; paste does not return them.
    """

    def _paste() -> dict[str, Any]:
        cv = _get_canvas(project, canvas)
        fn = {"paste": cv.paste, "rename": cv.paste_rename, "transfer": cv.paste_transfer}[mode]
        return {"pasted": bool(fn(x, y)), "mode": mode}

    return _safe(_paste)


@mcp.tool()
def pscad_list_definitions(project: str) -> dict[str, Any]:
    """List the definitions stored in a project, with instance count and whether each is a module."""

    def _defs() -> dict[str, Any]:
        prj = session.project(project)
        out = []
        for name in prj.definitions():
            d = prj.definition(name)
            entry: dict[str, Any] = {"name": name}
            try:
                entry["is_module"] = d.is_module()
                entry["instances"] = d.instances
            except Exception as e:  # noqa: BLE001
                entry["error"] = str(e)
            out.append(entry)
        return {"definitions": out}

    return _safe(_defs)


@mcp.tool()
def pscad_copy_definition(
    from_project: str, definition: str, to_project: str, with_dependents: bool = True
) -> dict[str, Any]:
    """Copy a definition (e.g. a finished module) from one loaded project into another.

    This is how a module proven in a small test-bench project is moved into
    the main project. Place instances afterwards with
    pscad_add_component(project=to_project, library=to_project, name=definition, ...).
    """

    def _copy() -> dict[str, Any]:
        src = session.project(from_project).definition(definition)
        session.app.copy_definitions(src)
        dst = session.project(to_project)
        if with_dependents:
            dst.paste_definitions_with_dependents()
        else:
            dst.paste_definitions()
        return {"definitions_now": dst.definitions()}

    return _safe(_copy)


@mcp.tool()
def pscad_export_definition_xml(project: str, definition: str, xml_path: str) -> dict[str, Any]:
    """Write a definition's XML to a file (to keep as a template, or to inspect)."""

    def _exp() -> dict[str, Any]:
        xml = session.project(project).definition(definition).xml
        Path(xml_path).write_text(str(xml), encoding="utf-8")
        return {"path": xml_path, "chars": len(str(xml))}

    return _safe(_exp)


@mcp.tool()
def pscad_create_definition_from_xml(project: str, xml_path: str) -> dict[str, Any]:
    """Add a new definition to a project from an XML file (see pscad_export_definition_xml)."""

    def _create() -> dict[str, Any]:
        xml = Path(xml_path).read_text(encoding="utf-8")
        d = session.project(project).create_definition(xml)
        return {"name": d.name, "is_module": d.is_module()}

    return _safe(_create)


@mcp.tool()
def pscad_rename_definition(project: str, definition: str, new_name: str) -> dict[str, Any]:
    """Rename a definition (unique, alphanumeric, at most 30 characters)."""

    def _ren() -> dict[str, Any]:
        d = session.project(project).definition(definition)
        d.parameters(name=new_name)
        return {"definitions_now": session.project(project).definitions()}

    return _safe(_ren)


# ---------------------------------------------------------------------------
# Build diagnostics
# ---------------------------------------------------------------------------


@mcp.tool()
def pscad_get_messages_structured(
    project: str, status: Optional[str] = None, skip: int = 0
) -> dict[str, Any]:
    """Build/load messages as records: text, label, status, name, link (component id).

    `status` filters by prefix: "error" or "warning". `link` is the iid of
    the component that caused the message -- look it up with
    pscad_get_component_parameters. The list can contain messages of earlier
    builds: note `total` before a build and pass it as `skip` afterwards to
    see only the new ones. An EMPTY list after a failed build means a hard
    error that only PSCAD's own Build Messages pane shows: ask the user.
    """

    def _msgs() -> dict[str, Any]:
        msgs = session.project(project).messages()
        total = len(msgs)
        out = []
        for m in msgs[skip:]:
            st = str(m.status)
            if status and not st.lower().startswith(status.lower()):
                continue
            out.append({"text": m.text, "label": m.label, "status": st, "name": m.name, "link": m.link})
        return {"total": total, "returned": len(out), "messages": out}

    return _safe(_msgs)


@mcp.tool()
def pscad_get_run_output(project: str, tail_chars: int = 6000) -> dict[str, Any]:
    """Return the tail of the EMTDC run log (runtime warnings/errors) for a project."""

    def _out() -> dict[str, Any]:
        text = session.project(project).output() or ""
        return {"chars": len(text), "tail": text[-tail_chars:]}

    return _safe(_out)


@mcp.tool()
def pscad_get_build_dimensions(project: str) -> dict[str, Any]:
    """Read node / module / branch counts of the last build from its .map file.

    Keys of interest on an Educational licence: NODES (limit 200),
    NPAGES (module pages, limit 64), SUBSYS (limit 1). Call after every
    successful build and record the numbers.
    """

    def _dims() -> dict[str, Any]:
        prj = session.project(project)
        folder = Path(str(prj.temp_folder))
        maps = sorted(folder.glob("*.map"))
        if not maps:
            return {"found": False, "temp_folder": str(folder)}
        text = maps[-1].read_text(errors="replace")
        dims = {k: int(v) for k, v in re.findall(r"^\s*([A-Z_]+)\s*=\s*(\d+)\s*/", text, flags=re.M)}
        return {"found": True, "map_file": str(maps[-1]), "dimensions": dims}

    return _safe(_dims)


@mcp.tool()
def pscad_clean_project(project: str) -> dict[str, Any]:
    """Delete a project's build products so the next build starts from nothing."""
    return _safe(session.project(project).clean)


# ---------------------------------------------------------------------------
# Results: windows and CSV export for long runs
# ---------------------------------------------------------------------------


def _trace_and_time(run, channel_path: str):
    trace = run.call(channel_path, sep="/")
    data = trace.data
    domain = trace.domain
    times = domain.data if domain is not None else range(len(data))
    return times, data


@mcp.tool()
def pscad_get_trace_window(
    psout_path: str,
    channel_path: str,
    t_start: float,
    t_end: float,
    run_index: int = 0,
    max_points: int = 500,
) -> dict[str, Any]:
    """Statistics and decimated points of one channel between two times (seconds).

    Use for gate checks ("mean voltage between 4.0 and 5.0 s") without
    pulling a whole long run into context.
    """

    def _win() -> dict[str, Any]:
        with mhi.psout.File(str(psout_path)) as f:
            times, data = _trace_and_time(f.run(run_index), channel_path)
            sel = [(t, v) for t, v in zip(times, data) if t_start <= t <= t_end]
            if not sel:
                return {"num_samples": 0, "points": []}
            vals = [v for _, v in sel]
            step = max(1, len(sel) // max_points)
            return {
                "num_samples": len(sel),
                "min": min(vals),
                "max": max(vals),
                "mean": sum(vals) / len(vals),
                "first": vals[0],
                "last": vals[-1],
                "decimation_step": step,
                "points": [[t, v] for t, v in sel[::step]],
            }

    return _safe(_win)


@mcp.tool()
def pscad_export_traces_csv(
    psout_path: str, channel_paths: list[str], csv_path: str, run_index: int = 0, every: int = 1
) -> dict[str, Any]:
    """Write several channels to one CSV (time + one column per channel) for plotting/analysis.

    `every` keeps one sample in N. All channels must share the same time base.
    """

    def _csv() -> dict[str, Any]:
        with mhi.psout.File(str(psout_path)) as f:
            run = f.run(run_index)
            cols = []
            times = None
            for p in channel_paths:
                t, d = _trace_and_time(run, p)
                if times is None:
                    times = list(t)[::every]
                cols.append(list(d)[::every])
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["time"] + channel_paths)
            for i, t in enumerate(times or []):
                w.writerow([t] + [c[i] for c in cols])
        return {"path": csv_path, "rows": len(times or []), "columns": len(cols)}

    return _safe(_csv)
