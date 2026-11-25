"""Dismiss PSCAD modal dialogs (#32770) while a long API call runs.

All dialog text is dumped to a log file so build/run errors are not lost.
"""
import ctypes, ctypes.wintypes as wt, threading, time, os

user32 = ctypes.WinDLL('user32', use_last_error=True)

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dialogs.log')


def _pid_of(hwnd):
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _text(hwnd):
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 2)
    user32.GetWindowTextW(hwnd, buf, n + 2)
    return buf.value


def _child_texts(parent):
    out = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        cls = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(hwnd, cls, 64)
        t = _text(hwnd)
        if t and cls.value not in ('Button',):
            out.append(f'  <{cls.value}> {t}')
        return True

    user32.EnumChildWindows(parent, cb, 0)
    return out


class Watcher(threading.Thread):
    def __init__(self, pid, verbose=True):
        super().__init__(daemon=True)
        self.pid = pid
        self.stop_flag = False
        self.seen = []
        self.verbose = verbose

    def run(self):
        open(LOG, 'w', encoding='utf-8').close()
        while not self.stop_flag:
            hwnd = 0
            while True:
                hwnd = user32.FindWindowExW(0, hwnd, '#32770', None)
                if not hwnd:
                    break
                if _pid_of(hwnd) == self.pid and user32.IsWindowVisible(hwnd):
                    title = _text(hwnd)
                    hit = None
                    for cid in (4200, 4202, 4203, 4201, 1):
                        b = user32.GetDlgItem(hwnd, cid)
                        if b and user32.IsWindowVisible(b):
                            hit = (cid, b)
                            break
                    if hit:
                        self.seen.append((title, hit[0]))
                        txt = [f'=== DIALOG "{title}" cid={hit[0]}'] + _child_texts(hwnd)
                        with open(LOG, 'a', encoding='utf-8') as fh:
                            fh.write('\n'.join(txt) + '\n')
                        if self.verbose:
                            print(f'[dialog] "{title}" -> click {hit[0]}', flush=True)
                        user32.PostMessageW(hit[1], 0x00F5, 0, 0)  # BM_CLICK
                        time.sleep(1.5)
            time.sleep(0.4)

    def stop(self):
        self.stop_flag = True
