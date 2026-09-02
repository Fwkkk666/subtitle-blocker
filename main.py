"""Subtitle Blocker — cover the Chinese subtitle line, keep the target one.

Run:  python main.py
"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app import config as cfg_mod
from app.controller import Controller
from app.host import HOST_WINDOW_TITLE, WM_APP_SHOW

_mutex_handle = None  # keep alive for the process lifetime


def _single_instance_guard() -> bool:
    """Return True if another instance is already running.

    In that case, ask the first instance to show the bar and signal that
    this process should exit.
    """
    global _mutex_handle
    if not sys.platform.startswith("win"):
        return False
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    _mutex_handle = kernel32.CreateMutexW(None, False, "SubtitleBlockerSingleInstance")
    ERROR_ALREADY_EXISTS = 0x000000B7
    if kernel32.GetLastError() != ERROR_ALREADY_EXISTS:
        return False
    hwnd = ctypes.windll.user32.FindWindowW(None, HOST_WINDOW_TITLE)
    if hwnd:
        ctypes.windll.user32.PostMessageW(hwnd, WM_APP_SHOW, 0, 0)
    return True


def main() -> int:
    if _single_instance_guard():
        return 0
    app = QApplication(sys.argv)
    app.setApplicationName(cfg_mod.APP_NAME)
    app.setApplicationDisplayName(cfg_mod.APP_NAME)
    # Keep running from the tray even when the bar is hidden.
    app.setQuitOnLastWindowClosed(False)

    Controller(app)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
