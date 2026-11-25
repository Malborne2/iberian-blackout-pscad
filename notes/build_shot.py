"""Build, and screenshot every modal dialog that appears before dismissing it."""
import sys, os, time, threading
import ctypes
from ctypes import wintypes as wt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptools
from shot_hwnd import shot

user32 = ctypes.WinDLL('user32', use_last_error=True)
PID = 9876
HERE = os.path.dirname(os.path.abspath(__file__))


def text(h):
    n = user32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 2)
    user32.GetWindowTextW(h, b, n + 2)
    return b.value


died = threading.Event()


def watch():
    n = 0
    while not died.is_set():
        hwnd = 0
        while True:
            hwnd = user32.FindWindowExW(0, hwnd, '#32770', None)
            if not hwnd:
                break
            p = wt.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            if p.value != PID or not user32.IsWindowVisible(hwnd):
                continue
            n += 1
            name = 'dlg_%d' % n
            try:
                w, h = shot(hwnd, os.path.join(HERE, name + '.bmp'))
                print('dialog %r -> %s.bmp (%dx%d)' % (text(hwnd), name, w, h), flush=True)
            except Exception as e:
                print('shot err', e, flush=True)
            for cid in (4200, 4202, 4203, 4201, 1):
                b = user32.GetDlgItem(hwnd, cid)
                if b and user32.IsWindowVisible(b):
                    user32.PostMessageW(b, 0x00F5, 0, 0)
                    break
            time.sleep(1.0)
        time.sleep(0.4)


app, pr = ptools.ensure_loaded()
t = threading.Thread(target=watch, daemon=True)
t.start()
t0 = time.time()
pr.build()
ptools.log('build finished in', round(time.time() - t0, 1), 's')
time.sleep(1.5)
died.set()
