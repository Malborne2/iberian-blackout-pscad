---
name: pscad
description: Build, wire, run and read results from PSCAD 5.x models through the pscad MCP server (pscad_* tools). Use for any work in PSCAD or EMTDC - creating or editing a project, placing and wiring components, modules, synchronous machines, converters, building, running, snapshots, reading .psout results. Contains exact step-by-step procedures and the known failure modes on this machine.
---

# PSCAD through the `pscad` MCP server

*Version 2026-11-17 (rewritten after Sessions 17–18; the 2026-11-15 version is superseded).*

Every `pscad_*` tool drives the real PSCAD 5.1.0 (Educational) on this machine. There is no dry run.
Coordinates in every tool are **grid units** (the `.pscx` file stores grid × 18).

**The one rule: never assume, always read back.** PSCAD accepts wrong coordinates, wrong parameter
values and wires that touch nothing, and reports success. After every action, read the result with
the tool named in the procedure. If a read-back differs from what you expected, fix that before
doing anything else.

**The second rule: every sign and every per-unit base is checked against an independent meter in
the same run** (a source's own `P`/`Q` outputs, a multimeter, a breaker's `BP`, a DC source's `Ia`).
Sign and base errors cost Sessions 6–7 and 13–16 and passed gates that were wrong.

Each fact below is tagged:

- **[API]** — checked against the installed `mhi.pscad` 3.1.3 documentation;
- **[seen]** — observed on this machine (session number in RUNLOG where useful);
- **[untested]** — not yet tried. Test it on a throw-away project first and record the outcome in `RUNLOG.md`.

In the Iberian-blackout project, `PLAN.md` §2/§5 hold the project rules. Where this skill and
`PLAN.md` differ, `PLAN.md` wins.

## 0. Setup and tool health

1. **Server:** the server lives in `C:\GitHub\PSCAD-MCP`, started as `python -m pscad_mcp.server`. It
   lists **72 tools**, including the ⊕ tools from `ext.py`. A `.pth` file in
   `…\Python313\Lib\site-packages\pscad_mcp_path.pth` makes `pscad_mcp` importable from any working
   directory, so the client's `cwd` setting no longer matters [seen S17].
2. **Registrations** (do not edit unless broken):
   - opencode: `~\.config\opencode\opencode.json` (`mcp.pscad`, `PYTHONPATH`) and the project's `.opencode\opencode.json`;
   - Claude Code: the project's `.mcp.json` (full python path + `env.PYTHONPATH`; Claude Code **ignores** `cwd` [seen S17]).
3. **If the `pscad_*` tools are missing in a session:**
   - Read the client's MCP log:
     - opencode: `C:\Users\Ibrahim\.local\share\opencode\log\opencode.log`, search `server=pscad`;
     - Claude Code: `%LOCALAPPDATA%\claude-cli-nodejs\Cache\<project-slug>\mcp-logs-pscad\*.jsonl`.
   - Check the server outside the client: `python stage0\check_server_tools.py` (project folder) must report 72 tools.
   - If the server is healthy, the client fetched its tool list at start-up and must be restarted. Tell the user, quoting the log line.
   - Fallback driver: `stage2\pscad_ops.py` (direct `mhi.pscad`). Use it only if the user cannot restart, and say so in the RUNLOG.
4. **Dialogs:** PSCAD draws its error/confirmation dialogs *inside* the main frame, so
   `pscad_list_dialogs` cannot see them. Sending `{ENTER}` to the main window dismisses them and
   unblocks the tools [seen S4].
5. **Paths:** PSCAD cannot build in a path containing non-ASCII characters (the `Ø` of the OneDrive
   folder) [seen S2]. Build and run only under `C:\PSCAD_work`; copy snapshots back to the project
   folder.

## 1. Which tool for which job

| Job | Tool |
| --- | --- |
| Start | `pscad_connect(prefer_launch=False)` (attach to the running PSCAD) → `pscad_status` |
| Open / list / close projects | `pscad_load(paths)`, `pscad_list_projects`, `pscad_unload_project` |
| New project | **copy an existing `.pscx`** and rename its prefix (P13). `pscad_create_project` once crashed the server [seen S1] |
| Run settings | `pscad_get_project_parameters(name=…)`, `pscad_set_project_parameters` |
| What is on a canvas | `pscad_list_canvas_objects` ⊕ (fast; `defn=` filter), `pscad_find_component`, `pscad_list_components` (slow) |
| Place a component | `pscad_add_component(project, library, name, canvas, x, y, orient, parameters)` |
| **Where are its ports** | `pscad_get_ports` ⊕ |
| Its box | `pscad_get_bounds(iids=[…])` ⊕ |
| Parameters | `pscad_get_component_parameters`, `pscad_set_component_parameters`, legal values: `pscad_get_parameter_range` ⊕ |
| Wire | `pscad_create_wire(project, vertices, canvas)` |
| Bus | `pscad_create_bus` ⊕ |
| Connect far-apart points | `pscad_create_node_label_pair` ⊕ (or place `master:nodelabel` / `master:datalabel` yourself, P4) |
| Canvas size, free space | `pscad_get_canvas_settings` ⊕, `pscad_set_canvas_settings` ⊕, `pscad_find_empty_rect` ⊕ |
| Copy | `pscad_clone_component` ⊕, `pscad_copy_region` ⊕ + `pscad_paste` ⊕ |
| Definitions / modules | `pscad_list_definitions` ⊕, `pscad_create_definition_from_xml`, `pscad_copy_definition` ⊕, `pscad_export_definition_xml` ⊕, `pscad_rename_definition` ⊕ — and the generator scripts of P8 |
| Delete | `pscad_delete_component(iid=<one int>)` — a list is rejected [seen S16] |
| Build | `pscad_build_project` → `pscad_get_messages_structured` ⊕ → `pscad_get_build_dimensions` ⊕ |
| Run | `pscad_run_project(name, wait=False)` → completion check (P7); log: `pscad_get_run_output` ⊕ |
| Results | `pscad_find_output_file(project=…)` → `pscad_list_output_channels(psout_path=…)` → `mhi.psout` in a Python script (P7) |
| Save | `pscad_save_project` (after every successful step) |

Inside a module: pass the module's **definition name** as `canvas` (e.g. `canvas="RES_Plant"`)
[API].

## 2. Procedures

### P1. Start of every session
1. `pscad_connect(prefer_launch=False)`. If PSCAD is not running, use `prefer_launch=True`. If
   `needs_login: true`, the user must log in; never type passwords.
2. `pscad_list_projects`. **Do not `pscad_load` a project that is already listed** — it raises a modal dialog and every later call hangs [seen].
3. `pscad_get_project_parameters`: confirm `PlotType` is `"PSOUT"`; if not, set it and read it back. A wrong value gives a successful run with no output file [seen].

### P2. Place and wire one component (the core loop)
Use this for **fewer than ~10 components**. For more, generate XML (P8/P12).
1. **Find room.** `pscad_find_empty_rect(width, height, near)`, with 2 grid units of margin on each side. Coordinates above 100 can work on a 100X100 canvas, but stay inside it when possible [seen S4, S17].
2. **Place.** `pscad_add_component(...)`. Keep the returned `iid`.
3. **Read ports.** `pscad_get_ports(iid)`. Write down each port's `x`, `y`, `dim`, `type`.
4. **Check the box.** `pscad_get_bounds`; compare with `pscad_list_canvas_objects`. No other component, wire or bus may lie inside or touch the box, except where you intend a connection. Overlaps connect silently [seen].
5. **Wire.** `pscad_create_wire` from the exact port coordinate to the exact target coordinate. Rules:
   - A wire must **end on** a port, never pass through a component [seen].
   - A wire that **crosses a bus, a port or another wire's endpoint connects to it** [seen]. Route around, or use labels (P4).
   - Two ports at the same coordinate are already connected. A label placed exactly on a port connects to it with no wire [seen S17].
   - Only connect ports of the same `dim` (`dimension mismatch -> 1 != 3`) [seen].
   - Data and electrical wires look the same: check `type` of both ends.
6. **Build and read messages** (P6). Then `pscad_save_project`.

To change orientation: delete and re-add with another `orient`, then read the ports again. Do not
calculate rotated port positions yourself.

### P3. Parameters
1. `pscad_get_component_parameters(iid)` first; use the **exact** key names it returns. Parameter names are internal symbols, not dialog captions.
2. Choice parameters: on this machine, many accept only the **index** (`"4"`, `"1"`), not the label. A wrong label is silently ignored by `set_component_parameters` [seen S4]. Read back: it comes back as the label (e.g. `Type: "RR_L"`).
3. Values with units are strings: `"50.0 [ohm]"`, `"400 [kV]"`.
4. Set, then read back. `set_parameters` performs no validity check [API]; out-of-range values are silently ignored or clamped (a negative `PO` on `fixed_load` draws zero power [seen]).
5. Facts [seen]:
   - `fixed_load`: `PO`, `QO` are **per phase**; `VBO` is line-to-neutral; constant power = `NP = NQ = 0`, `KPF = 0`.
   - `source3`: frequency is in `F` and `F0` (lower-case `f` is ignored).
   - `source3`/`source1` **`Type` defaults to "1 = R", a purely resistive source impedance** even with `Imp = IMPEDANCE`. For a grid, use `Type = 4` (R-R//L), `Imp = IMPEDANCE`, `Z1`/`Phi1`, and `ZSeq = YES` with `Z0`/`Phi0` [seen S17].
   - `source1` `R1p`/`L1p` are the *shunt* R‖L of the RRL format, not the Thevenin impedance [seen S16].
   - `breaker3`: control signal named by `NAME`; signal **1 = open, 0 = closed** [seen S18].
   - `signalgen` PULSE starts at Max; `P = 180` starts it at Min. `master:sig_gen` is a **sine**; the triangle is `master:signalgen` `Type = TRIANGLE` [seen S16–S17].
   - `realpole` initialises its state from its t = 0 input [seen S16].
6. **Which fields can hold a module parameter name:** look up the field's `content_type` in
   `C:\Program Files (x86)\PSCAD\5.1.0\master.pslx` [seen S17].
   - `Constant` fields take a published parameter (`rtcbranch` R/L/C, `fixed_load`, `multimeter.S`, `source_3.Vm`, `sync_machine` data, `excac_2016_2` gains, `upramp`).
   - `Variable` fields take a signal, and a published parameter also works (`gain.G`, `realpole` T/Max/Min, `pi_ctlr` GP/TI, `var_impedance`, `varrlc`).
   - **`Literal` fields cannot** (`inductor.L`, `capacitor.C`, `resistor.R`, `const.Value`). Error: `Conversion of '<name>' to a finite number was not resolved`.

### P4. Buses and labels
- `pscad_create_bus(vertices)`, then name it (P3). Two buses with the same name fail the build [seen].
- Electrical labels are **`master:nodelabel`**; signal labels are **`master:datalabel`** [seen S17]. Same `Name` = connected.
- `pscad_create_node_label_pair` places two labels. Re-using a name makes it rename the new pair `<name>_2`, which is then **not** connected. To connect a third point to an existing label, place a `nodelabel`/`datalabel` component with the exact `Name` [seen S17].
- A `datalabel` name must be a plain identifier (`MM1:CurI` is invalid) [seen S4].

### P5. Record a signal
1. Give the measuring component a signal name in its own parameters (e.g. source `P = "PG"`, `Ia = "IDC"`, breaker `BP`, `rtcbranch` `I`).
2. `master:datalabel` with that name → wire → `master:pgb` (read both ports). Wiring a pgb straight to a component output produced no channel [seen].
3. A pgb on a wire that carries a module **parameter** fails (`source contention` / `constant signal … cannot be utilized before it is generated`) [seen S10].
4. Channel paths: `Root/Main/<pgb>/0/1` on Main. Inside module instances: `Root/Main/<Defn>/<pgb>/0/1` (one instance) or `Root/Main/<Defn>[n]/<pgb>/0/1` (several). **`[n]` is PSCAD's order and changes between builds**, so identify instances by a measured quantity (P, Sbase-scaled values) [seen S10, S18].

### P6. Build and verify
1. `pscad_build_project(name)`. Its return value says nothing about success [seen].
2. `pscad_get_messages_structured(project, status="error")`, then `status="warning"`. `total` counts all messages; the filter only narrows the returned list [seen S16]. For each error, `link` is the component iid.
3. Treat these warnings as errors: `short circuit`, `Open circuit`, `floating`, `Unresolved`, `source contention`, `below range`, `above range`. Integer→real `type conversion may lose accuracy` warnings are harmless.
4. `pscad_get_build_dimensions` → record `NODES`, `NPAGES`, `SUBSYS`. Educational limits: 200 nodes, 64 module pages, 1 subsystem.
   - **Ammeters and multimeters split a node:** +3 nodes each on a 3-phase line [seen S17].
   - `source3` has 3 hidden nodes; `sync_machine` costs 0.
   - Every module *instance* is a page.
5. A failed build with no messages means the error is only in PSCAD's Build Messages pane: ask the user.

### P7. Run and read results
1. Set `time_duration` (s), `time_step` (µs), `sample_step` (µs); read back. Switching converters need ≈ 5 µs.
2. Runs under 1 min wall-clock: `wait=True`. **Longer: `wait=False`.** `pscad_get_run_status` returns nothing useful on this machine [seen S17]. Completion = `pscad_get_run_output` contains `Simulation has ended` (status code 0). The `NdStartup failed with c00000bb` line after it is harmless.
3. **Copy the `.psout`** (`<project>.gf81_x86\<project>.psout`) to a session folder before the next run overwrites it. Check its timestamp is after the run started (a stale file looks like a result [seen]).
4. Read results with a Python script: `mhi.psout.File(path).run(0).call("Root/Main/…/0/1", sep="/")` → `.domain.data`, `.data` [seen]. Instantaneous P/Q carry 100 Hz ripple: use a 20 ms moving mean, padded with edge values, not `np.convolve(mode="same")` [seen S10].
5. Every result used for a decision ends as a figure made by the same script that prints the numbers.

### P8. Modules (one definition, many instances) — generated from XML
Module shells **are** created by tool: `pscad_create_definition_from_xml`, or a script that writes the
definition into a `.pscx` (P12) [seen S9–S18]. Working generators: `stage2\build_syncunit_xml.py`,
`stage2\add_governor.py`, `stage3\build_resplant.py` (`--update <pscx>` replaces the definition in an
existing project). Copy their pattern. The rules, every one of which broke a build:

| # | Rule |
| --- | --- |
| 1 | Parameters: `content_type="Constant"`, `type="Real"` (an `Integer` needs integer `min`/`max` — a float bound breaks `mhi`'s codec) |
| 2 | Publish every parameter inside the canvas with a `master:import` whose `Name` is the parameter (its output port is 2 grid units right of the placement point) |
| 3 | A unique definition `id` (do not inherit the template's) |
| 4 | `<form><category>…</category></form>`, no `<categories>` wrapper |
| 5 | Electrical port = a `master:xnode` with `Name` = port name, sitting on the internal node |
| 6 | Data ports = `master:import` (input) / `master:export` (output) with `Name` = port name — **not** `xnode` |
| 7 | **The instance's ports come from the `<graphics>` `Port` elements**, not from `<svg>`: `mode` 1 = input, 2 = output, 3 = electrical; `datatype` 3 = Real, 0 = electrical; `dim` |
| 8 | Bind a component field to a parameter only if the field is `Constant`/`Variable` (P3.6); replace `inductor`/`capacitor` by `master:rtcbranch` (ports at ±1 grid unit; ER/EL/EC select R/L/C; its `I` field is a free branch-current output) |

Then:

1. Prove the module on a small bench project (< 20 nodes).
2. An instance must show the right ports (`pscad_get_ports`) and build with 0 errors.
3. One run must reproduce the bench the module was copied from, **to the digit**.

Only then put it into the main project. Keep modules flat (no module inside a module).

### P9. Reuse a working group from a PSCAD example
Shipped examples: `C:\Users\Public\Documents\PSCAD\5.1.0\Examples\`. Library definitions:
`C:\Program Files (x86)\PSCAD\5.1.0\master.pslx` (port offsets: `<port x y>` ÷ 18).
1. `pscad_load` the example. Record the wiring and parameters of the group (`pscad_list_canvas_objects`, `pscad_get_ports`, `pscad_get_component_parameters`). The record is the specification.
2. Prefer copying the group's XML with a script (the components keep their parameters exactly) over `pscad_copy_region`/`pscad_paste`.
3. Build the copied group alone before changing anything. Unload the example **without saving**.

### P10. Snapshots
`SnapType`/`StartType` take the **index** (`SnapType: 1` = ONLY_ONCE, `StartType: 1` = FROM_SNAP_FILE)
[seen S4]. A reloaded project copy reproduces its run to the digit [seen S16]. Snapshot-start of a
switching model is still [untested]: prove it on the bench before relying on it.

### P11. Canvas too small
`pscad_get_canvas_settings` → `pscad_set_canvas_settings(parameters={"size": "100X100"})` → read
back. Do this **before** placing anything [seen].

### P12. Editing the `.pscx` file directly
For bulk edits and for generated modules. Sequence:

1. `pscad_save_project` → `pscad_unload_project`.
2. Script edit with `xml.etree.ElementTree`.
3. `pscad_load` → build.

Never edit while loaded: PSCAD overwrites the file from memory [seen]. When writing strings that
contain Windows paths from Python, use raw strings: `\r`, `\f`, `\a` inside normal strings silently
corrupt text [seen S17].

### P13. New project from an existing one
Copy `X.pscx` to `C:\PSCAD_work\Y.pscx`. In the copy, replace every `X:` prefix with `Y:` and set
`<project name="Y">`. Keep the station definition `DS` and the `<hierarchy>` calls, renamed.
Removing `DS` breaks the project [seen S17].

## 3. Symptom → cause → what to do

| Symptom | Likely cause | Do |
| --- | --- | --- |
| Every tool call hangs | Modal dialog in PSCAD (login, "already loaded", save prompt) | Send `{ENTER}` (§0.4); if that fails, ask the user |
| `pscad_*` tools missing | MCP server not started by the client | §0.3 |
| Build fails, no messages | Hard error shown only in the GUI | Ask the user for the Build Messages text |
| `dimension mismatch -> 1 != 3` | 1-conductor port on a 3-phase node, or overlap | `pscad_get_ports` on `link`; check bounds |
| `source contention` | Two outputs on one signal; or a pgb on a parameter wire | `pscad_list_canvas_objects`; move the pgb |
| `Input port '...' is floating` | Unwired input; or the signal died with a deleted component (e.g. a recorder of a removed source) | Wire it, or delete the dead label + pgb |
| `Conversion of 'X' to a finite number was not resolved` | Parameter name in a `Literal` field | P3.6 |
| `Port 'T' has no matching '<Defn>' tag component` | Missing `xnode` | P8 rule 5 |
| Instance shows the wrong ports | `<graphics>` not updated, or an inherited definition id | P8 rules 3, 7 |
| Run fine, no `.psout` | `PlotType` not `PSOUT` | P1 step 3 |
| Results unchanged after an edit | Stale output file, or the edit did not apply | Check file time; read the parameter back |
| A weak-grid bench has V rising with P but not with Q | Source `Type` = R | P3.5 |
| A dq current loop gets *worse* at lower gain | Wrong structure or sign (rotation not decoupled, feedback sign) — not a tuning issue | Write the plant equation in your frame; check the current sign against an independent meter |
| Machine terminal voltage sags / drifts | Machine not initialised, AVR on the wrong base | Never change machine reactances to fix it |
| Governor/AVR "test" shows no response | Tested against an ideal source that fixes f/V | Test where the controller can move its quantity (island, weak bus) |
| Node / module limit | Educational limits | Record the exact error text; follow the project plan's cut order |

## 4. When to involve the user

Only for:

1. tools missing and §0.3 cannot fix it (the client needs a restart);
2. a GUI-only action (a dialog `{ENTER}` does not clear, a login or licence prompt, a build that fails with no messages);
3. a change to a decision the user has documented (the project plan names them).

Everything else — a tool that errors, a gate that fails, something that behaves differently from
this file — is handled autonomously:

- measure and record it in `RUNLOG.md`;
- choose the next step yourself, recording the alternatives;
- correct the [untested]/[seen] tags in this file **only if the user has allowed skill edits**; otherwise list the correction in the RUNLOG.
