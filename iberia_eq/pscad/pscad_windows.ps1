# List the visible windows (title) of every PSCAD started by run_v2.py, per run tag (S30 sec 25: find hidden dialogs
# that block prj.run()). Read-only.  usage: powershell -File iberia_eq\pscad\pscad_windows.ps1
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public class PW { public delegate bool CB(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(CB cb, IntPtr l);
 [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 public static List<string> L(int p){ var r=new List<string>(); EnumWindows((h,l)=>{int q; GetWindowThreadProcessId(h,out q);
   if(q==p && IsWindowVisible(h)){var s=new StringBuilder(512); GetWindowText(h,s,512); r.Add("  '"+s+"'");} return true;},IntPtr.Zero); return r; } }
"@
$all = Get-CimInstance Win32_Process
foreach ($py in ($all | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*run_v2.py*' })) {
  $tag = ($py.CommandLine -split 'run_v2.py\s+')[1].Split(' ')[0]
  foreach ($ps in ($all | Where-Object { $_.ParentProcessId -eq $py.ProcessId -and $_.Name -eq 'Pscad.exe' })) {
    "$tag (PSCAD $($ps.ProcessId)):"; [PW]::L($ps.ProcessId)
  }
}
