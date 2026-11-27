# List logical CPUs with their core index and efficiency class (S30 sec 23, run-strategy optimisation).
# Higher EfficiencyClass = faster core (Zen 5 vs Zen 5c on the Ryzen AI 9 HX 370). Read-only.
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public static class CpuSets {
  [DllImport("kernel32.dll", SetLastError=true)]
  public static extern bool GetSystemCpuSetInformation(IntPtr info, uint len, out uint ret, IntPtr proc, uint flags);
}
"@
$len = 0
[void][CpuSets]::GetSystemCpuSetInformation([IntPtr]::Zero, 0, [ref]$len, [IntPtr]::Zero, 0)
$buf = [Runtime.InteropServices.Marshal]::AllocHGlobal([int]$len)
[void][CpuSets]::GetSystemCpuSetInformation($buf, $len, [ref]$len, [IntPtr]::Zero, 0)
$off = 0
while ($off -lt $len) {
  $size = [Runtime.InteropServices.Marshal]::ReadInt32($buf, $off)
  $lp   = [Runtime.InteropServices.Marshal]::ReadByte($buf, $off + 14)   # LogicalProcessorIndex
  $core = [Runtime.InteropServices.Marshal]::ReadByte($buf, $off + 15)   # CoreIndex
  $cls  = [Runtime.InteropServices.Marshal]::ReadByte($buf, $off + 18)   # EfficiencyClass
  "{0},{1},{2}" -f $lp, $core, $cls
  $off += $size
}
[Runtime.InteropServices.Marshal]::FreeHGlobal($buf)
