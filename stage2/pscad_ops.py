"""Direct-API replacement for the pscad MCP tools (the MCP server dropped out of
the agent session at 23:20). Every function calls the *same* mhi.pscad layer the
MCP tools wrap, so behaviour is identical; this module only removes the MCP
transport.

Usage from another script:  import pscad_ops as P ; P.connect()
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Optional

import mhi.pscad

_APP = None


class PscadError(RuntimeError):
    pass


def connect(silence: bool = True):
    global _APP
    if _APP is not None:
        return _APP
    _APP = mhi.pscad.connect(timeout=10)
    try:
        _APP.flags({"silence": silence, "load-meta-files": False})
    except Exception:
        pass
    return _APP


def app():
    if _APP is None:
        connect()
    return _APP


def project(name: str):
    return app().projects()[name] if isinstance(app().projects(), dict) else app().project(name)


# --------------------------------------------------------------- inspection
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


def get_ports(project: str, iid: int, canvas: str = "Main") -> dict[str, Any]:
    comp = app().project(project).canvas(canvas).component(iid)
    return {
        "iid": iid,
        "defn_name": comp.defn_name,
        "location": tuple(comp.location),
        "ports": [_port_dict(p) for p in comp.ports().values()],
    }


def get_bounds(project: str, iids: list[int], canvas: str = "Main") -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    comps = [cv.component(i) for i in iids]
    rects = cv.bounds(comps)
    return {
        "bounds": [
            {"iid": i, "left": r.left, "top": r.top, "right": r.right, "bottom": r.bottom}
            for i, r in zip(iids, rects)
        ]
    }


def get_component_parameters(project: str, iid: int, canvas: str = "Main") -> dict[str, Any]:
    comp = app().project(project).canvas(canvas).component(iid)
    return {"iid": iid, "parameters": dict(comp.parameters())}


def set_component_parameters(project: str, iid: int, parameters: dict, canvas: str = "Main") -> dict[str, Any]:
    comp = app().project(project).canvas(canvas).component(iid)
    comp.parameters(**parameters)
    return {"iid": iid, "parameters": dict(comp.parameters())}


def get_parameter_range(project: str, iid: int, parameter: str, canvas: str = "Main") -> dict[str, Any]:
    comp = app().project(project).canvas(canvas).component(iid)
    rng = comp.range(parameter)
    if isinstance(rng, range):
        return {"parameter": parameter, "kind": "int_range", "start": rng.start, "stop": rng.stop}
    return {"parameter": parameter, "kind": type(rng).__name__, "values": [str(v) for v in rng]}


def list_canvas_objects(project: str, canvas: str = "Main", defn: Optional[str] = None) -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    comps = cv.find_all(defn) if defn else cv.components()
    rects = cv.bounds(comps) if comps else []
    out = [
        {"iid": c.iid, "defn_name": c.defn_name, "bounds": [r.left, r.top, r.right, r.bottom]}
        for c, r in zip(comps, rects)
    ]
    return {"count": len(out), "objects": out}


# --------------------------------------------------------------- placement
def add_component(project: str, library: str, name: str, canvas: str = "Main", x: int = 36, y: int = 36,
                  orient: int = 0, parameters: Optional[dict] = None) -> dict[str, Any]:
    prj = app().project(project)
    comp = prj.canvas(canvas).add_component(library, name, x, y, orient, **(parameters or {}))
    return {"iid": comp.iid, "defn_name": comp.defn_name, "location": tuple(comp.location)}


def create_wire(project: str, vertices: list, canvas: str = "Main") -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    wire = cv.create_wire(*[tuple(v) for v in vertices])
    return {"ok": True, "wire": str(wire)}


def create_connection(project: str, from_point: list, to_point: list, label: str,
                      canvas: str = "Main") -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    return {"label": cv.create_connection(tuple(from_point), tuple(to_point), label=label)}


def create_bus(project: str, vertices: list, canvas: str = "Main") -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    bus = cv.create_bus(*[tuple(v) for v in vertices])
    return {"iid": bus.iid, "vertices": [list(p) for p in bus.vertices()]}


def move_component(project: str, iid: int, x: int, y: int, canvas: str = "Main") -> dict[str, Any]:
    comp = app().project(project).canvas(canvas).component(iid)
    comp.set_location(x, y)
    return {"iid": iid, "location": tuple(comp.location)}


def delete_component(project: str, iid: int, canvas: str = "Main") -> dict[str, Any]:
    app().project(project).canvas(canvas).component(iid).delete()
    return {"deleted": iid}


def find_empty_rect(project: str, width: int, height: int, near: list, canvas: str = "Main") -> dict[str, Any]:
    r = app().project(project).canvas(canvas).closest_empty_rect(width, height, tuple(near))
    return {"left": r.left, "top": r.top, "right": r.right, "bottom": r.bottom}


def get_canvas_settings(project: str, canvas: str = "Main") -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    size = cv.size
    return {"settings": dict(cv.parameters()), "grid_size": [size[0], size[1]]}


def create_project(name: str, folder: str, project_type: int = 1):
    p = app().create_project(project_type, name, folder)
    return {"created": str(p)}


def copy_region(project: str, x1: int, y1: int, x2: int, y2: int, canvas: str = "Main") -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    cv.clear_selection()
    cv.select_components(x1, y1, x2, y2)
    return {"copied": bool(cv.copy())}


def paste(project: str, x: int, y: int, canvas: str = "Main", mode: str = "paste") -> dict[str, Any]:
    cv = app().project(project).canvas(canvas)
    fn = {"paste": cv.paste, "rename": cv.paste_rename, "transfer": cv.paste_transfer}[mode]
    return {"pasted": bool(fn(x, y)), "mode": mode}


# --------------------------------------------------------------- build
def messages(project: str, status: Optional[str] = None, skip: int = 0) -> dict[str, Any]:
    msgs = app().project(project).messages()
    out = []
    for m in msgs[skip:]:
        st = str(m.status)
        if status and not st.lower().startswith(status.lower()):
            continue
        out.append({"text": m.text, "label": m.label, "status": st, "name": m.name, "link": m.link})
    return {"total": len(msgs), "returned": len(out), "messages": out}


def build(project: str) -> dict[str, Any]:
    n0 = len(app().project(project).messages())
    t = time.time()
    ok = app().project(project).build()
    dur = time.time() - t
    errs = messages(project, "error", n0)
    warns = messages(project, "warning", n0)
    return {
        "build_returned": bool(ok),
        "seconds": round(dur, 1),
        "errors": errs["messages"],
        "warnings": warns["messages"],
    }


def build_dimensions(project: str) -> dict[str, Any]:
    prj = app().project(project)
    folder = Path(str(prj.temp_folder))
    maps = sorted(folder.glob("*.map"))
    if not maps:
        return {"found": False, "temp_folder": str(folder)}
    text = maps[-1].read_text(errors="replace")
    dims = {k: int(v) for k, v in re.findall(r"^\s*([A-Z_]+)\s*=\s*(\d+)\s*/", text, flags=re.M)}
    return {"found": True, "map_file": str(maps[-1]), "dimensions": dims}


def project_parameters(project: str) -> dict[str, Any]:
    return dict(app().project(project).parameters())


def set_project_parameters(project: str, parameters: dict) -> dict[str, Any]:
    app().project(project).parameters(**parameters)
    return dict(app().project(project).parameters())


def save(project: str) -> dict[str, Any]:
    p = app().project(project)
    p.save()
    return {"saved": project, "filename": str(p.filename)}


def save_as(project: str, new_filename: str, folder: Optional[str] = None) -> dict[str, Any]:
    p = app().project(project)
    new = p.save_as(new_filename, folder=folder) if folder else p.save_as(new_filename)
    return {"new_name": new.name, "new_filename": str(new.filename)}


def run(project: str, wait: bool = True, poll: float = 1.0, timeout: float = 3600) -> dict[str, Any]:
    p = app().project(project)
    p.run()
    if not wait:
        return {"started": True}
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = str(p.run_status())
        if "Run" not in st and "Build" not in st:
            return {"seconds": round(time.time() - t0, 1), "status": st}
        time.sleep(poll)
    return {"timeout": True}


def run_status(project: str) -> dict[str, Any]:
    return {"status": str(app().project(project).run_status())}


def output(project: str, tail: int = 4000) -> str:
    text = app().project(project).output() or ""
    return text[-tail:]


def find_output_file(project: str) -> str:
    folder = Path(str(app().project(project).temp_folder))
    cands = sorted(folder.glob("*.psout"))
    return str(cands[-1]) if cands else ""


# --------------------------------------------------------------- results
def list_output_channels(psout_path: str, run_index: int = 0):
    """Return [(description, path)] for every trace in the run."""
    import mhi.psout

    with mhi.psout.File(str(psout_path)) as f:
        run = f.run(run_index)
        out = []
        for p in run.trace_paths():
            trace, path = p
            out.append((str(trace), str(path)))
        return out


def trace_window(psout_path: str, channel_path: str, t_start: float, t_end: float,
                 run_index: int = 0, max_points: int = 500):
    import mhi.psout

    with mhi.psout.File(str(psout_path)) as f:
        run = f.run(run_index)
        trace = run.call(channel_path, sep="/")
        data = trace.data
        domain = trace.domain
        times = domain.data if domain is not None else range(len(data))
        sel = [(t, v) for t, v in zip(times, data) if t_start <= t <= t_end]
    if not sel:
        return {"num_samples": 0}
    vals = [v for _, v in sel]
    step = max(1, len(sel) // max_points)
    return {
        "num_samples": len(sel),
        "min": min(vals), "max": max(vals),
        "mean": sum(vals) / len(vals),
        "first": vals[0], "last": vals[-1],
        "points": [[t, v] for t, v in sel[::step]],
    }


def trace_series(psout_path: str, channel_path: str, run_index: int = 0):
    import mhi.psout

    with mhi.psout.File(str(psout_path)) as f:
        run = f.run(run_index)
        trace = run.call(channel_path, sep="/")
        data = trace.data
        domain = trace.domain
        times = domain.data if domain is not None else range(len(data))
        return [(t, v) for t, v in zip(times, data)]


def definitions(project: str) -> list[str]:
    return list(app().project(project).definitions())


if __name__ == "__main__":
    connect()
    print("connected, projects:", list(app().projects()))
