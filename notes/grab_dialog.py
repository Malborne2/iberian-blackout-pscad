"""Wait for a #32770 dialog owned by PSCAD, screenshot it, dump texts, then dismiss."""
import ctypes, ctypes.wintypes as wt, time, os, sys

user32 = ctypes.WinDLL('user32', use_last_error=True)
gdi32 = ctypes.WinDLL('gdi32')

HERE = os.path.dirname(os.path.abspath(__file__))
PID = 9876


def _pid_of(hwnd):
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _text(hwnd):
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 2)
    user32.GetWindowTextW(hwnd, buf, n + 2)
    return buf.value


def children(parent):
    out = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        cls = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(hwnd, cls, 64)
        r = wt.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        out.append((hwnd, cls.value, _text(hwnd), r.left, r.top, r.right - r.left, r.bottom - r.top))
        return True

    user32.EnumChildWindows(parent, cb, 0)
    return out


def shot(hwnd, path):
    r = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    hdc = user32.GetWindowDC(hwnd)
    mdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(hwnd, mdc, 2)  # PW_RENDERFULLCONTENT
    # write BMP
    import struct
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [('biSize', wt.DWORD), ('biWidth', wt.LONG), ('biHeight', wt.LONG),
                    ('biPlanes', wt.WORD), ('biBitCount', wt.WORD), ('biCompression', wt.DWORD),
                    ('biSizeImage', wt.DWORD), ('biXPelsPerMeter', wt.LONG), ('biYPelsPerMeter', wt.LONG),
                    ('biClrUsed', wt.DWORD), ('biClrImportant', wt.DWORD)]
    bi = BITMAPINFOHEADER()
    bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bi.biWidth, bi.biHeight = w, -h
    bi.biPlanes, bi.biBitCount = 1, 24
    bi.biCompression = 0
    stride = ((w * 3 + 3) // 4) * 4
    buf = ctypes.create_string_buffer(stride * h)
    gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bi), 0)
    with open(path, 'wb') as f:
        f.write(b'BM')
        f.write(struct.pack('<IHHI', 14 + 40 + len(buf), 0, 0, 14 + 40))
        f.write(bytes(bi))
        f.write(buf.raw)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mdc)
    user32.ReleaseDC(hwnd, hdc)


def main():
    click = '--click' in sys.argv
    t0 = time.time()
    while time.time() - t0 < float(os.environ.get('GRAB_TIMEOUT', '120')):
        hwnd = 0
        while True:
            hwnd = user32.FindWindowExW(0, hwnd, '#32770', None)
            if not hwnd:
                break
            if _pid_of(hwnd) == PID and user32.IsWindowVisible(hwnd):
                title = _text(hwnd)
                print('DIALOG:', repr(title), flush=True)
                for c in children(hwnd):
                    print('   ', c[1], repr(c[2])[:200], c[3:], flush=True)
                p = os.path.join(HERE, 'dialog.png')
                shot(hwnd, p)
                print('saved', p, flush=True)
                if click:
                    for cid in (4200, 4202, 4203, 4201, 1):
                        b = user32.GetDlgItem(hwnd, cid)
                        if b and user32.IsWindowVisible(b):
                            user32.PostMessageW(b, 0x00F5, 0, 0)
                            print('clicked', cid, flush=True)
                            break
                return
        time.sleep(0.3)
    print('no dialog found', flush=True)


main()
