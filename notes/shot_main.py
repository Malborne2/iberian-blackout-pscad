"""Screenshot the PSCAD main window (to read build messages)."""
import ctypes, ctypes.wintypes as wt, time, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grab_dialog import _pid_of, _text, shot, children

user32 = ctypes.WinDLL('user32', use_last_error=True)
PID = 9876

# dismiss any open dialog first
for _ in range(10):
    hwnd = 0
    found = False
    while True:
        hwnd = user32.FindWindowExW(0, hwnd, '#32770', None)
        if not hwnd:
            break
        if _pid_of(hwnd) == PID and user32.IsWindowVisible(hwnd):
            found = True
            for cid in (4200, 4202, 4203, 4201, 1):
                b = user32.GetDlgItem(hwnd, cid)
                if b and user32.IsWindowVisible(b):
                    user32.PostMessageW(b, 0x00F5, 0, 0)
                    print('dismissed', cid)
                    break
            break
    if not found:
        break
    time.sleep(1.0)

main = user32.FindWindowW(None, 'PSCAD 5.1.0 (64-bit) Educational')
print('main', main, repr(_text(main)))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pscad_main.png')
shot(main, out)
print('saved', out)
