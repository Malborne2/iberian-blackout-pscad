import ctypes, ctypes.wintypes as wt
user32 = ctypes.WinDLL('user32', use_last_error=True)
PID = 9876

def pid_of(h):
    p = wt.DWORD(); user32.GetWindowThreadProcessId(h, ctypes.byref(p)); return p.value

def text(h):
    n = user32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 2); user32.GetWindowTextW(h, b, n + 2); return b.value

def cls(h):
    b = ctypes.create_unicode_buffer(128); user32.GetClassNameW(h, b, 128); return b.value

rows = []
@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb(h, _):
    if pid_of(h) == PID:
        r = wt.RECT(); user32.GetWindowRect(h, ctypes.byref(r))
        rows.append((h, cls(h), text(h), user32.IsWindowVisible(h), r.left, r.top, r.right - r.left, r.bottom - r.top))
    return True

user32.EnumWindows(cb, 0)
for r in rows:
    print(r)
print('---- children of main')
main = user32.FindWindowW(None, 'PSCAD 5.1.0 (64-bit) Educational')
@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb2(h, _):
    r = wt.RECT(); user32.GetWindowRect(h, ctypes.byref(r))
    t = text(h)
    if t or 'Edit' in cls(h):
        print(h, cls(h), repr(t)[:120], user32.IsWindowVisible(h), r.right - r.left, r.bottom - r.top)
    return True
user32.EnumChildWindows(main, cb2, 0)
