"""Print and dismiss every modal dialog owned by PSCAD (one-shot, synchronous)."""
import ctypes
from ctypes import wintypes as wt
import os, time

user32 = ctypes.WinDLL('user32', use_last_error=True)
PID = 9876
HERE = os.path.dirname(os.path.abspath(__file__))


def text(h):
    n = user32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 2)
    user32.GetWindowTextW(h, b, n + 2)
    return b.value


def pid_of(h):
    p = wt.DWORD()
    user32.GetWindowThreadProcessId(h, ctypes.byref(p))
    return p.value


def children(h):
    out = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(w, _):
        cls = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(w, cls, 64)
        t = text(w)
        if t and cls.value != 'Button':
            out.append(t)
        return True

    user32.EnumChildWindows(h, cb, 0)
    return out


hwnd = 0
found = 0
while True:
    hwnd = user32.FindWindowExW(0, hwnd, '#32770', None)
    if not hwnd:
        break
    if pid_of(hwnd) != PID or not user32.IsWindowVisible(hwnd):
        continue
    found += 1
    print('=== DIALOG', hex(hwnd), repr(text(hwnd)))
    for t in children(hwnd):
        print('    ', t[:300])
    for cid in (4200, 4202, 4203, 4201, 1):
        b = user32.GetDlgItem(hwnd, cid)
        if b and user32.IsWindowVisible(b):
            user32.PostMessageW(b, 0x00F5, 0, 0)
            print('    clicked', cid)
            break
    time.sleep(0.6)
print('dialogs found', found)
