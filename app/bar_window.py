"""The always-on-top subtitle bar window."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal, QVariantAnimation
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

# Resize-handle anchor points: names map to direction strings used by _resize.
_HANDLE_POINTS = [
    ("nw", -1, -1),
    ("n", 0, -1),
    ("ne", 1, -1),
    ("e", 1, 0),
    ("se", 1, 1),
    ("s", 0, 1),
    ("sw", -1, 1),
    ("w", -1, 0),
]

ACCENT = QColor("#ff4d4f")
HANDLE_PX = 12
HIT_TOL = 16
MIN_W, MIN_H = 24, 16


class BarWindow(QWidget):
    """A frameless, always-on-top, click-through colored strip.

    Normal state: input-transparent (clicks pass through to the app below).
    Edit mode: the strip grabs the mouse so the user can move / resize it.
    """

    # Emitted whenever the user moves or resizes the bar (for live-following the
    # edit handle and for persisting geometry).
    geometryChanged = Signal(QRect)
    # Emitted once a move/resize gesture completes (used to save to disk).
    commit = Signal(QRect)
    # Emitted when the user presses Esc while in edit mode (request to lock).
    lockRequested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._visible_ = False
        self._edit = False
        self._color = QColor("#000000")
        self._opacity = 1.0
        self._drag_state: str | None = None  # "move" or "resize"
        self._resize_dir: str | None = None
        self._start_geom = QRect()
        self._start_global = QPoint()
        self._outline_t = 0.0  # edit-mode outline fade, 0..1
        self._outline_anim = QVariantAnimation(self)
        self._outline_anim.setDuration(180)
        self._outline_anim.valueChanged.connect(self._on_outline_anim)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)

    # ----- public API -----------------------------------------------------

    def is_edit(self) -> bool:
        return self._edit

    def set_bar_geometry(self, x, y, w, h) -> None:
        self.setGeometry(x, y, w, h)

    def set_color(self, hex_color: str) -> None:
        self._color = QColor(hex_color)
        self.update()

    def set_opacity(self, value: float) -> None:
        self._opacity = value
        self.update()

    def enter_edit(self) -> None:
        if self._edit:
            return
        self._edit = True
        self._set_click_through(False)
        self._fade_outline(100)

    def exit_edit(self) -> None:
        if not self._edit:
            return
        self._edit = False
        self._drag_state = None
        self._resize_dir = None
        self._set_click_through(True)
        self._fade_outline(0)

    def _on_outline_anim(self, value) -> None:
        self._outline_t = value / 100.0
        self.update()

    def _fade_outline(self, target: int) -> None:
        self._outline_anim.stop()
        self._outline_anim.setStartValue(int(self._outline_t * 100))
        self._outline_anim.setEndValue(target)
        self._outline_anim.start()

    def set_click_through(self, enabled: bool) -> None:
        """When not editing, the bar is click-through regardless."""
        self._set_click_through(enabled and not self._edit)

    # ----- internals ------------------------------------------------------

    def _set_click_through(self, enabled: bool) -> None:
        # setWindowFlag() hides the widget as a side effect, so remember the
        # real visibility *before* toggling and restore it afterwards.
        was_visible = self.isVisible()
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enabled)
        if was_visible:
            self.show()

    def showEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        super().showEvent(event)
        self._visible_ = True

    def hideEvent(self, event) -> None:  # noqa: N802
        super().hideEvent(event)
        self._visible_ = False

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        body = self.rect().adjusted(0, 0, -1, -1)
        fill = QColor(self._color)
        fill.setAlpha(int(self._opacity * 255))
        p.fillRect(body, fill)

        if self._outline_t > 0.01:
            a = int(255 * self._outline_t)
            outline = QColor(ACCENT.red(), ACCENT.green(), ACCENT.blue(), a)
            p.setPen(QPen(outline, 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(body)
            p.setPen(Qt.PenStyle.NoPen)
            for _name, dx, dy in _HANDLE_POINTS:
                cx = self.rect().center().x() + dx * (self.width() / 2 - 2)
                cy = self.rect().center().y() + dy * (self.height() / 2 - 2)
                p.fillRect(
                    QRect(int(cx) - HANDLE_PX // 2, int(cy) - HANDLE_PX // 2,
                          HANDLE_PX, HANDLE_PX),
                    outline,
                )
        p.end()

    # ----- mouse handling (only active in edit mode) ----------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._start_global = event.globalPosition().toPoint()
        self._start_geom = self.geometry()
        self._resize_dir = self._hit_handle(event.position().toPoint())
        self._drag_state = "resize" if self._resize_dir else "move"
        self.setCursor(
            self._cursor_for(self._resize_dir) if self._resize_dir
            else Qt.CursorShape.SizeAllCursor
        )
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if not self._drag_state:
            return
        delta = event.globalPosition().toPoint() - self._start_global
        if self._drag_state == "move":
            self.move(self._start_geom.topLeft() + delta)
        elif self._resize_dir:
            self.setGeometry(self._resize(self._start_geom, self._resize_dir, delta))
        self.geometryChanged.emit(self.geometry())
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_state:
            self._drag_state = None
            self._resize_dir = None
            self.unsetCursor()
            self.commit.emit(self.geometry())
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if self._edit and event.key() == Qt.Key.Key_Escape:
            self.exit_edit()
            self.lockRequested.emit()
        else:
            super().keyPressEvent(event)

    # ----- geometry helpers -----------------------------------------------

    def _hit_handle(self, pos: QPoint) -> str | None:
        for name, dx, dy in _HANDLE_POINTS:
            cx = self.rect().center().x() + dx * (self.width() / 2 - 2)
            cy = self.rect().center().y() + dy * (self.height() / 2 - 2)
            if abs(cx - pos.x()) <= HIT_TOL and abs(cy - pos.y()) <= HIT_TOL:
                return name
        return None

    def _cursor_for(self, direction: str | None):
        cursors = {
            "nw": Qt.CursorShape.SizeFDiagCursor,
            "se": Qt.CursorShape.SizeFDiagCursor,
            "ne": Qt.CursorShape.SizeBDiagCursor,
            "sw": Qt.CursorShape.SizeBDiagCursor,
            "n": Qt.CursorShape.SizeVerCursor,
            "s": Qt.CursorShape.SizeVerCursor,
            "e": Qt.CursorShape.SizeHorCursor,
            "w": Qt.CursorShape.SizeHorCursor,
        }
        return cursors.get(direction, Qt.CursorShape.SizeAllCursor)

    @staticmethod
    def _resize(rect: QRect, direction: str, delta: QPoint) -> QRect:
        left, top, right, bottom = (
            rect.left(),
            rect.top(),
            rect.right(),
            rect.bottom(),
        )
        dx, dy = delta.x(), delta.y()
        if "w" in direction:
            left = min(left + dx, right - MIN_W)
        if "e" in direction:
            right = max(right + dx, left + MIN_W)
        if "n" in direction:
            top = min(top + dy, bottom - MIN_H)
        if "s" in direction:
            bottom = max(bottom + dy, top + MIN_H)
        return QRect(left, top, right - left + 1, bottom - top + 1)
