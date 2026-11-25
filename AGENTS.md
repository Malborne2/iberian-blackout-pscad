# AGENTS.md — how agents (and people) work together on this project

This project replicates the 28 April 2025 Iberian blackout in PSCAD 5.1 (Educational licence). Several AI agents and
the project owner work on it in parallel, each in their own clone. This file is the shared rulebook. Read it before
your first change; follow it on every change.

## 1. What is where

| File / folder | Role | Who edits |
|---|---|---|
| `PLAN.md` | the plan: work packages, gates, decisions | anyone, with the owner's agreement for scope changes |
| `RUNLOG.md` | chronological log of everything done and measured | everyone, append-only (see §3) |
| `STATUS.md` | short current-state banner | the agent who changes the state |
| `iberia_eq/SOURCES.md` | data dossier: every number used, with its source and page | anyone; add the source **before** using a value |
| `iberia_eq/V2_BUS_UNIT_LIST.md` | the v2 Iberian-equivalent design | anyone; design changes are logged in RUNLOG |
| `iberia_eq/pp_v2.py` | pandapower model and calibration of the v2 pre-event state | anyone (see §4) |
| `stage*/` | scripts and results of earlier stages (IEEE-39-based ib4…ib6 cases) | append new scripts; do not rewrite history |
| `EXECUTOR_PROMPT.md` | **frozen**, do not edit | nobody |
| `Resources/` | reference documents | owner |
| `notes/` | text extracts of the references | anyone |

**Authority of sources:** the ENTSO-E *Final Report* (`Resources/Final Report …pdf`, code [FR]) is the reference. The
Spanish committee report [CA] and the papers are supplementary (SOURCES.md §12). Never put a number in a model
without an entry in SOURCES.md.

## 2. Ground rules (they protect the work and the machine)

1. **No scratch work.** All code you run goes in the repository, committed (a new script under the stage or
   `iberia_eq/` folder it belongs to), so others can rerun it. Results that come from code must be reproducible from
   committed code plus the command line recorded in RUNLOG.
2. **PSCAD builds and runs only in `C:\PSCAD_work\…`** (a path without non-ASCII characters; the `Ø` in the OneDrive
   path breaks the build). Use your own subfolder per batch (e.g. `C:\PSCAD_work\<agent>\<batch>`), never another
   agent's folder. At most 8 PSCAD runs in parallel on one machine.
3. **Do not edit** `C:\GitHub\PSCAD-MCP` (the MCP server) or the archived iberia4 case.
4. **Keep the switching converter models** (no averaged-model substitution) unless the owner decides otherwise.
5. **Fidelity before prevention:** no prevention measure (P1–P7) is studied until the event replay passes its gate
   (PLAN.md).
6. **Never change Windows security settings.** Ask the owner.
7. No secrets in the repo (tokens, passwords, personal e-mail addresses).
8. Licensed PDFs: `Resources/` holds IEEE papers licensed to a university library. The repository is **private**
   for that reason. Remove them (and their `notes/` text extracts) before the repository is ever made public.

## 3. Collaboration protocol

**Identify yourself.** Every agent picks a short, stable name, e.g. `claude-main` (the owner's main Claude Code
session) or `<tool>-<owner/machine>`. Use it in branch names and RUNLOG headings (not in commit messages).

**Branches.**
- `main` is the shared, working state. Do not force-push it.
- Work on `agent/<name>/<topic>` (e.g. `agent/claude-main/pp-v2-calibration`). Merge into `main` via a pull request
  or a fast-forward after `git pull --rebase`. Keep commits small and focused.
- Before starting: `git pull --rebase origin main`. Before pushing: pull again and rerun anything your change touches.

**Claim before you start.** Add one line to the claims table at the top of `STATUS.md` (§5 below): who, what, files,
since when. Remove it when done. Do not edit files another agent has claimed. Ask in a PR comment, or ask the owner.

**RUNLOG entries (append-only, signed).**
- Start a new block per working session:
  `## Session <n> — <date> — agent: <name>` and number your sections inside it.
- Every section heading carries the agent name if it is not obvious from the session heading:
  `### 35. <title> (2026-11-25, agent: claude-main)`.
- Never rewrite another agent's entries. Corrections go in a new entry that cites the old one
  ("correction to S27 §21 by …").
- Record for every result: the command line, the script and its commit, input files, and where outputs are.

**Merge conflicts in RUNLOG/STATUS** are resolved by keeping both sides (entries are independent blocks).

**Commits are made under the owner's GitHub identity (Malborne2) only.** No agent names, no AI co-author or
attribution lines in commit messages or PRs. Message format: `<area>: <what>`, e.g. `pp_v2: France ties hub-to-hub`.
Who did what is recorded only in the signed RUNLOG entries.

## 4. Shared-code rules

- `iberia_eq/pp_v2.py` is the reference pre-event model. Change behaviour through command-line options or
  environment switches with the old behaviour available. Note the new default in RUNLOG.
- Saved states (`iberia_eq/pp_v2_state*.pkl`) are inputs to `RESUME=1`. If you produce a new reference state,
  commit it under a new name and say in RUNLOG which run made it.
- Long runs: run in the background, write the log next to the script (`iberia_eq/cal_*.txt`), commit the log.

## 5. Where the PSCAD cases are

The working PSCAD cases (`C:\PSCAD_work\s25 … s28`, snapshots `.snp`, outputs `.psout`) are **outside** this
repository on the owner's machine. Copies of the reference cases live under `stage*/`. When you build a new case
from a committed script, commit the script and the resulting `.pscx` (not the build folder) and record the path.
