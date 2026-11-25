import ctypes, ctypes.wintypes as wt
user32 = ctypes.WinDLL('user32', use_last_error=True)


def text(h):
    n = user32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 2)
    user32.GetWindowTextW(h, b, n + 2)
    return b.value


def cls(h):
    b = ctypes.create_unicode_buffer(128)
    user32.GetClassNameW(h, b, 128)
    return b.value


PARENT = 200048

@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb(h, _):
    r = wt.RECT()
    user32.GetWindowRect(h, ctypes.byref(r))
    print(h, cls(h), repr(text(h))[:80], user32.IsWindowVisible(h),
          r.left, r.top, r.right - r.left, r.bottom - r.top)
    return True


user32.EnumChildWindows(PARENT, cb, 0)
