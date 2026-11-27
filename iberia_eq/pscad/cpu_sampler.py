r"""Sample CPU use of PSCAD and solver processes every few seconds (S30 sec 23, run-strategy optimisation).

usage: python iberia_eq\pscad\cpu_sampler.py --names v2a v2b --until-gone --dt 10
Prints, per sample, each Pscad.exe (with the script that launched it) and each solver process whose name is in --names,
as % of one core. With --until-gone it stops once the named solvers have appeared and all exited.
"""
import argparse, subprocess, sys, time

ap = argparse.ArgumentParser(); ap.add_argument("--names", nargs="+", required=True); ap.add_argument("--dt", type=float, default=10)
ap.add_argument("--until-gone", action="store_true"); ap.add_argument("--max", type=float, default=1800); a = ap.parse_args()
PS = r"""
$p=Get-CimInstance Win32_Process
$sel=Get-Process -EA SilentlyContinue | ? { $_.ProcessName -eq 'Pscad' -or @(%s) -contains $_.ProcessName }
$a=$sel | Select Id,ProcessName,CPU; Start-Sleep %g
foreach($x in $a){ $g=Get-Process -Id $x.Id -EA SilentlyContinue; if($g){
  $par=($p|?{$_.ProcessId -eq $x.Id}).ParentProcessId; $cmd=(($p|?{$_.ProcessId -eq $par}).CommandLine+'')
  $i=$cmd.IndexOf('pscad\'); if($i -ge 0){$cmd=$cmd.Substring($i+6,[Math]::Min(28,$cmd.Length-$i-6))} else {$cmd=''}
  '{0}|{1}|{2:N0}|{3}' -f $x.ProcessName,$x.Id,(($g.CPU-$x.CPU)/%g*100),$cmd } }
"""
names = ",".join(f"'{n}'" for n in a.names); seen = False; t0 = time.time()
while time.time() - t0 < a.max:
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS % (names, a.dt, a.dt)], capture_output=True, text=True).stdout
    rows = [r.split("|") for r in out.strip().splitlines() if r.count("|") == 3]
    sol = [r for r in rows if r[0] in a.names]; seen = seen or bool(sol)
    print(f"[{time.time() - t0:5.0f} s] " + "  ".join(f"{r[0]}({r[1]}) {r[2]}% {r[3]}".strip() for r in rows), flush=True)
    if a.until_gone and seen and not sol: break
