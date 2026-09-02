"""Hidden message host used for single-instance toggling.

When the user launches the exe a second time, the new process finds this
window by title and posts WM_APP_SHOW, making the first instance show the
bar; the second process then exits. Double-clicking never hides the bar.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes  # noqa: F401
import sys

from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication, QObject, Qt, Signal
from PySide6.QtWidgets import QWidget

# Posted by a second launch to ask the first instance to SHOW the bar.
WM_APP_SHOW = 0x8001
HOST_WINDOW_TITLE = "SubtitleBlockerHostWindow"

_is_windows = sys.platform == "win32"


if _is_windows:
    class _ToggleFilter(QAbstractNativeEventFilter):
        def __init__(self, callback) -> None:
            super().__init__()
            self._cb = callback

        def nativeEventFilter(self, event_type, message):
            try:
                raw = bytes(event_type)
            except TypeError:
                raw = (
                    event_type.data()
                    if hasattr(event_type, "data")
                    else str(event_type).encode()
                )
            if raw == b"windows_generic_MSG":
                msg = ctypes.wintypes.MSG.from_address(int(message))
                if msg.message == WM_APP_SHOW:
                    self._cb()
                    return True, 0
            return False, 0


class MessageHost(QObject):
    """Owns the hidden window that receives WM_APP_SHOW."""

    showRequested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._host = QWidget()
        self._host.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self._host.setWindowTitle(HOST_WINDOW_TITLE)
        # Force HWND creation so FindWindowW can locate us.
        self._hwnd = int(self._host.winId())
        if _is_windows:
            self._filter = _ToggleFilter(self.showRequested.emit)
            QCoreApplication.instance().installNativeEventFilter(self._filter)
