"""Small floating control buttons attached inside the bar's right edge.

The bar itself is input-transparent (click-through), so each button is its
own tiny always-on-top window. They are the only spots on the bar that eat
mouse clicks; the rest of the bar still passes clicks through.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

SIZE = 30      # window / hit area
VISUAL = 26    # visible rounded square

BG = QColor(20, 20, 20, 150)
BG_HOVER = QColor(60, 60, 60, 200)
BG_PRESS = QColor(0, 0, 0, 220)
GLYPH = QColor("#f8fafc")


def _lerp_color(a: QColor, b: QColor, t: float) -> QColor:
    c = QColor()
    c.setRed(int(a.red() + (b.red() - a.red()) * t))
    c.setGreen(int(a.green() + (b.green() - a.green()) * t))
    c.setBlue(int(a.blue() + (b.blue() - a.blue()) * t))
    c.setAlpha(int(a.alpha() + (b.alpha() - a.alpha()) * t))
    return c


class BarButton(QWidget):
    clicked = Signal()

    def __init__(self, kind: str) -> None:
        super().__init__()
        assert kind in ("edit", "close")
        self._kind = kind
        self._active = False  # edit button shows the check glyph when active
        self._t = 0.0
        self._pressed = False
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFixedSize(SIZE, SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(150)
        self._anim.valueChanged.connect(self._on_anim)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.update()

    def _on_anim(self, value) -> None:
        self._t = value / 100.0
        self.update()

    def _animate_to(self, target: int) -> None:
        self._anim.stop()
        self._anim.setStartValue(int(self._t * 100))
        self._anim.setEndValue(target)
        self._anim.start()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg = _lerp_color(BG, BG_HOVER, self._t)
        if self._pressed:
            bg = BG_PRESS
        half = (SIZE - VISUAL) / 2.0
        rect = QRectF(self.rect()).adjusted(half, half, -half, -half)
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 6, 6)

        pen = QPen(GLYPH, 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        cx, cy = rect.center().x(), rect.center().y()

        path = QPainterPath()
        if self._kind == "close":
            d = rect.width() * 0.18
            path.moveTo(cx - d, cy - d)
            path.lineTo(cx + d, cy + d)
            path.moveTo(cx + d, cy - d)
            path.lineTo(cx - d, cy + d)
        elif self._active:
            # check mark
            d = rect.width() * 0.20
            path.moveTo(cx - d, cy)
            path.lineTo(cx - d * 0.25, cy + d * 0.7)
            path.lineTo(cx + d, cy - d * 0.7)
        elif self._kind == "edit":
            # filled pencil silhouette, drawn in a 26-unit box scaled to rect
            u = rect.width() / 26.0
            ox, oy = rect.left(), rect.top()

            def pt(x, y):
                return QPointF(ox + x * u, oy + y * u)

            body = QPainterPath()
            body.moveTo(pt(7, 15))
            body.lineTo(pt(16, 6))
            body.lineTo(pt(20, 10))
            body.lineTo(pt(11, 19))
            body.closeSubpath()
            tip = QPainterPath()
            tip.moveTo(pt(7, 15))
            tip.lineTo(pt(11, 19))
            tip.lineTo(pt(5, 21))
            tip.closeSubpath()
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(GLYPH)
            p.drawPath(body)
            p.drawPath(tip)
            p.end()
            return
        p.drawPath(path)
        p.end()

    def enterEvent(self, event) -> None:  # noqa: N802
        self._animate_to(100)

    def leaveEvent(self, event) -> None:  # noqa: N802
        if not self._pressed:
            self._animate_to(0)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
            event.accept()
