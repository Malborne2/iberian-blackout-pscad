r"""Live PSCAD run dashboard (S30): a local web page with one progress bar per run. Reads files only, changes nothing.

usage: python iberia_eq\pscad\run_dashboard.py [--port 8765] [--hours 12] [--done-min 30] [--host 100.106.88.76]
       python iberia_eq\pscad\run_dashboard.py --clear
then open http://localhost:8765 (the page refreshes itself every 5 s).
Shown (owner request): live runs always; a finished run for --done-min minutes; a failed run until a newer run starts in
the same work folder (a restart) or until cleared. --clear (or the page's 'Clear finished' button; × hides one run) hides every run that is not live now (list in
C:\PSCAD_work\v2_runs\_dashboard_hidden.json) and exits; running servers pick it up on their next refresh.

Sources per run tag (C:\PSCAD_work\v2_runs\<tag>\run.log, written by run_v2.py):
  - duration and snapshot time from the "run parameters" line; work folder from the "work:" line (older runs: the
    folder C:\PSCAD_work\<tag> if it exists, else v2sld for sld_* tags, else v2);
  - state: failed (BUILD ERRORS / RUN FAILED), done (run done), stopped (no live run_v2.py process for the tag: killed;
    shown like a finished run), running (the .out file grows), building/starting;
  - simulated time = first column of the last line of <work>\v2.gf81_x86\v2_01.out, its age flags a stall;
  - speed and ETA from the run.log creation time.
Case generation in progress (build_v2.py) shows from <work>\build_v2.log written in the last 10 min.
"""
import argparse, glob, json, os, re, shutil, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765); ap.add_argument("--hours", type=float, default=12)
ap.add_argument("--done-min", type=float, default=30.0); ap.add_argument("--clear", action="store_true")
ap.add_argument("--host", default="127.0.0.1")   # e.g. the Tailscale IP to view it from the phone (tailnet only)
a = ap.parse_args([] if __name__ != "__main__" else None)
RUNS, WORK = r"C:\PSCAD_work\v2_runs", r"C:\PSCAD_work"

def last_t(out):
    try:
        with open(out, "rb") as f:
            f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 600)); tail = f.read().decode(errors="replace").strip().split("\n")
        return float(tail[-1].split()[0])
    except Exception:
        return None

_LIVE = [0.0, set()]                                 # (time, tags of live run_v2.py processes), refreshed every 20 s
def live_tags():
    """tags of the run_v2.py processes alive now (S30: a run killed from outside left no end line and showed 'stalled?')."""
    if time.time() - _LIVE[0] > 20:
        import subprocess
        ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | % { $_.CommandLine }")
        try:
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=30).stdout
            _LIVE[1] = {m.group(1) for m in re.finditer(r"run_v2\.py\"?\s+(\S+)", out)}; _LIVE[0] = time.time()
        except Exception:
            return None
    return _LIVE[1]

HIDDEN = os.path.join(RUNS, "_dashboard_hidden.json")
def hidden():
    try: return json.load(open(HIDDEN))
    except Exception: return {}

def runs(filtered=True):
    now = time.time(); res = []; lv = live_tags()
    for log in glob.glob(os.path.join(RUNS, "*", "run.log")):
        try:                                                 # a run folder may be deleted while scanning
            w_ = re.search(r"^work: (.+)$", open(log, encoding="utf-8", errors="replace").read(), re.M)
            o_ = os.path.join(w_.group(1).strip(), "v2.gf81_x86", "v2_01.out") if w_ else ""
            last_ = max(os.path.getmtime(log), os.path.getmtime(o_) if o_ and os.path.exists(o_) else 0)
            if now - last_ > 3600 * a.hours: continue        # a long run writes its .out, not its run.log
            tag = os.path.basename(os.path.dirname(log)); txt = open(log, encoding="utf-8", errors="replace").read(); t0 = os.path.getctime(log)
        except OSError:
            continue
        dur = re.search(r"'time_duration': ([\d.]+)", txt); dur = float(dur.group(1)) if dur else None
        me = re.search(r"run ([\d.]+) -> ([\d.]+) s", txt)          # snapshot restart: end time, not added length
        if me: dur = float(me.group(2))
        snap = re.search(r"'SnapTime': '?([\d.]+)", txt)
        w = re.search(r"^work: (.+)$", txt, re.M)
        work = w.group(1).strip() if w else (os.path.join(WORK, tag) if os.path.isdir(os.path.join(WORK, tag))
                                             else os.path.join(WORK, "v2sld" if tag.startswith("sld") else "v2"))
        st = re.search(r"^start: (\d+)", txt, re.M)               # run_v2 start time (a rewritten run.log keeps its ctime)
        out = os.path.join(work, "v2.gf81_x86", "v2_01.out"); t0 = float(st.group(1)) if st else os.path.getctime(log)
        ts = last_t(out) if os.path.exists(out) and os.path.getmtime(out) > t0 else None
        age = now - os.path.getmtime(out) if ts is not None else None
        if "BUILD ERRORS" in txt or "RUN FAILED" in txt or "Traceback" in txt: state = "failed"
        elif "run done" in txt: state = "done"
        elif lv is not None and tag not in lv: state = "stopped"          # process gone without an end line (killed)
        elif ts is not None: state = "stalled?" if age > 300 else "running"
        else: state = "building"
        why = ""
        m = re.search(r"(RUN FAILED: .*|BUILD ERRORS:.*|\w+Error: .*)", txt)
        if m: why = m.group(1)[:160]
        wall = (os.path.getmtime(log) if state in ("done", "failed", "stopped") else now) - t0
        spd = wall / ts if ts else None
        eta = spd * (dur - ts) if (spd and dur and state == "running") else None
        res.append(dict(tag=tag, state=state, t=ts, dur=dur, snap=float(snap.group(1)) if snap else None, age=age, wall=wall,
                        spd=spd, eta=eta, why=why, start=time.strftime("%H:%M", time.localtime(t0)), work=work, t0=t0,
                        tend=os.path.getmtime(log)))
    if filtered:
        hid = hidden()
        def keep(r):
            if hid.get(r["tag"]) == r["t0"]: return False                   # cleared (same run instance)
            if r["state"] == "done": return now - r["tend"] < 60 * a.done_min
            if r["state"] == "stopped": return (now - r["tend"] < 60 * a.done_min
                                                and not any(o["work"] == r["work"] and o["t0"] > r["t0"] for o in res))
            if r["state"] == "failed": return not any(o["work"] == r["work"] and o["t0"] > r["t0"] for o in res)
            return True
        res = [r for r in res if keep(r)]
    started = [r["t0"] for r in res if "t0" in r]
    for bl in glob.glob(os.path.join(WORK, "*", "build_v2.log")):
        if now - os.path.getmtime(bl) < 600 and not any(s > os.path.getmtime(bl) for s in started):
            last = open(bl, encoding="utf-8", errors="replace").read().strip().split("\n")[-1][:120]
            res.append(dict(tag="generating " + os.path.basename(os.path.dirname(bl)), state="generating", t=None, dur=None,
                            snap=None, age=now - os.path.getmtime(bl), wall=None, spd=None, eta=None,
                            why=last, start="–"))
    order = {"running": 0, "stalled?": 0, "building": 1, "generating": 1, "failed": 2, "stopped": 3, "done": 3}
    return sorted(res, key=lambda r: (order.get(r["state"], 9), -(r["wall"] or 0)))

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>PSCAD runs</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--fg:#1d2330;--mut:#6b7280;--bar:#e5e7eb;--run:#2563eb;--ok:#16a34a;--bad:#dc2626;--warn:#d97706}
@media (prefers-color-scheme:dark){:root{--bg:#111318;--card:#1a1d24;--fg:#e5e7eb;--mut:#9ca3af;--bar:#2a2f3a}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:14px/1.4 system-ui,Segoe UI,sans-serif}
h1{font-size:18px;margin:0 0 4px}.sub{color:var(--mut);margin-bottom:14px}
.card{background:var(--card);border-radius:10px;padding:12px 14px;margin-bottom:10px;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}.tag{font-weight:600;font-family:Consolas,monospace}
.st{font-size:12px;font-weight:600;padding:1px 8px;border-radius:99px;color:#fff}
.bar{position:relative;height:12px;background:var(--bar);border-radius:6px;margin:8px 0 6px;overflow:hidden}
.fill{height:100%;border-radius:6px}.snap{position:absolute;top:0;width:2px;height:100%;background:var(--fg);opacity:.5}
button{font:12px system-ui;border:1px solid var(--bar);background:var(--card);color:var(--fg);border-radius:6px;padding:2px 9px;cursor:pointer}
.x{margin-left:6px;padding:0 7px}.hdr{display:flex;align-items:center;gap:10px}
.meta{color:var(--mut);font-size:12px;display:flex;gap:14px;flex-wrap:wrap}.why{color:var(--bad);font-size:12px;margin-top:4px}
</style></head><body><div class="hdr"><h1>PSCAD runs</h1><button onclick="post('/clear')" title="hide every done / failed / stopped run">Clear finished</button></div><div class="sub" id="sub">loading…</div><div id="list"></div>
<script>
const C={running:'var(--run)',done:'var(--ok)',failed:'var(--bad)','stalled?':'var(--warn)',stopped:'var(--mut)',building:'var(--mut)',generating:'var(--mut)'};
const f=(s)=>s==null?'–':s<90?s.toFixed(0)+' s':s<5400?(s/60).toFixed(0)+' min':(s/3600).toFixed(1)+' h';
const FIN=['done','failed','stopped'];
async function post(u){try{await fetch(u,{method:'POST'})}catch(e){}tick()}
async function tick(){try{const J=await (await fetch('/api')).json();const r=J.runs;
 const sub=document.getElementById('sub');sub.textContent=`${r.filter(x=>x.state=='running').length} running · disk C: ${J.free_gb} GB free · updated ${new Date().toLocaleTimeString()}`;sub.style.color=J.free_gb<15?'var(--bad)':'';
 document.getElementById('list').innerHTML=r.map(x=>{const p=(x.t!=null&&x.dur)?Math.min(100,100*x.t/x.dur):(x.state=='done'?100:0);
 return `<div class="card"><div class="top"><span class="tag">${x.tag}</span><span><span class="st" style="background:${C[x.state]||'gray'}">${x.state}</span>${FIN.includes(x.state)&&x.t0?`<button class="x" title="hide this run" onclick="post('/hide?tag=${encodeURIComponent(x.tag)}&t0=${x.t0}')">×</button>`:''}</span></div>
 <div class="bar"><div class="fill" style="width:${p}%;background:${C[x.state]||'gray'}"></div>${x.snap&&x.dur?`<div class="snap" style="left:${100*x.snap/x.dur}%" title="snapshot"></div>`:''}</div>
 <div class="meta"><span>${x.t!=null?x.t.toFixed(2):'–'} / ${x.dur??'–'} s simulated (${p.toFixed(0)} %)</span><span>started ${x.start}</span><span>wall ${f(x.wall)}</span>
 <span>${x.spd?x.spd.toFixed(0)+' s wall per sim s':''}</span><span>${x.eta!=null?'ETA '+f(x.eta):''}</span><span>${x.age!=null&&x.state!='done'?'last write '+f(x.age)+' ago':''}</span></div>
 ${x.why?`<div class="why" style="${x.state=='failed'?'':'color:var(--mut)'}">${x.why.replace(/</g,'&lt;')}</div>`:''}</div>`}).join('')||'<div class="sub">no runs in the last hours</div>';
}catch(e){document.getElementById('sub').textContent='dashboard server not reachable'}}
tick();setInterval(tick,5000);
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(dict(runs=runs(), free_gb=round(shutil.disk_usage(WORK).free / 1e9, 1))).encode() if self.path.startswith("/api") else PAGE.encode()
        self.send_response(200); self.send_header("Content-Type", "application/json" if self.path.startswith("/api") else "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)
    def do_POST(self):                                # Clear finished / hide one run (owner request): only edits HIDDEN
        from urllib.parse import urlparse, parse_qs
        u = urlparse(self.path); q = parse_qs(u.query); hid = hidden(); n = 0
        if u.path == "/clear":
            for r in runs(filtered=False):
                if r["state"] in ("done", "failed", "stopped") and r.get("t0"): hid[r["tag"]] = r["t0"]; n += 1
        elif u.path == "/hide" and "tag" in q and "t0" in q:
            hid[q["tag"][0]] = float(q["t0"][0]); n = 1
        json.dump(hid, open(HIDDEN, "w"))
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps(dict(hidden=n)).encode())
    def log_message(self, *x): pass

if a.clear:
    hid = hidden(); n = 0
    for r in runs(filtered=False):
        if r["state"] in ("done", "failed", "stopped") and r.get("t0"): hid[r["tag"]] = r["t0"]; n += 1
    json.dump(hid, open(HIDDEN, "w")); print(f"cleared {n} finished/failed/stopped runs"); raise SystemExit(0)
if __name__ == "__main__":                            # run_watch.py imports runs() without starting a server
    print(f"dashboard on http://{a.host}:{a.port}", flush=True)
    ThreadingHTTPServer((a.host, a.port), H).serve_forever()
