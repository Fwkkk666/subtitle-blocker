"""Coordinates the bar window, in-bar buttons, tray menu and message host."""

from __future__ import annotations

from PySide6.QtCore import QObject, QRect, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QColorDialog, QMenu, QSystemTrayIcon

from . import config as cfg_mod
from . import i18n
from .bar_buttons import BarButton
from .bar_window import BarWindow
from .defaults import default_geometry
from .host import MessageHost

COLOR_PRESETS = [
    ("#000000", "color_black"),
    ("#1f1f1f", "color_charcoal"),
    ("#ffffff", "color_white"),
    ("#0f4c2a", "color_green"),
    ("#ff7f00", "color_orange"),
]

OPACITY_PRESETS = [
    ("opacity_100", 1.0),
    ("opacity_90", 0.9),
    ("opacity_75", 0.75),
    ("opacity_50", 0.5),
    ("opacity_25", 0.25),
]

BTN_GAP = 4
BTN_MARGIN = 6


class Controller(QObject):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.cfg = cfg_mod.load_config()
        i18n.set_language(self.cfg["language"])

        self.bar = BarWindow()
        self.btn_edit = BarButton("edit")
        self.btn_close = BarButton("close")

        self._apply_initial_geometry()
        self.bar.set_color(self.cfg["color"])
        self.bar.set_opacity(self.cfg["opacity"])

        self.bar.geometryChanged.connect(self._on_geometry_changed)
        self.bar.commit.connect(self._on_commit)
        self.bar.lockRequested.connect(self._on_lock_requested)
        self.btn_edit.clicked.connect(self._on_edit_clicked)
        self.btn_close.clicked.connect(self._on_close_clicked)
        self._update_button_tooltips()

        self.host = MessageHost()
        # A second exe launch asks us to SHOW the bar (never hide).
        self.host.showRequested.connect(self._show)

        self.tray = QSystemTrayIcon(self._make_icon(), self)
        self.tray.activated.connect(self._on_tray_activated)
        self._rebuild_menu()

        # Starting the app always shows the bar, so first-time users can see
        # that it launched; hiding is an explicit action ([✕] or tray).
        self._show()

    # ----- visibility ------------------------------------------------------

    def _show(self) -> None:
        self.bar.show()
        self.bar.raise_()
        self._sync_buttons()

    def _hide(self) -> None:
        if self.bar.is_edit():
            self.bar.exit_edit()
            self.btn_edit.set_active(False)
            self._update_button_tooltips()
        self.bar.hide()
        self.btn_edit.hide()
        self.btn_close.hide()

    def toggle_visible(self) -> None:
        if self.bar.isVisible():
            self._hide()
        else:
            self._show()

    def _ensure_visible(self) -> None:
        """Tray actions that affect the bar show it first (live preview)."""
        if not self.bar.isVisible():
            self._show()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visible()

    # ----- in-bar buttons --------------------------------------------------

    def _on_edit_clicked(self) -> None:
        if self.bar.is_edit():
            self._exit_edit()
        else:
            self._enter_edit()

    def _on_close_clicked(self) -> None:
        self._hide()

    def _enter_edit(self) -> None:
        self._ensure_visible()
        self.bar.enter_edit()
        self.btn_edit.set_active(True)
        self._update_button_tooltips()
        self._sync_buttons()

    def _exit_edit(self) -> None:
        self.bar.exit_edit()
        self.btn_edit.set_active(False)
        self._update_button_tooltips()
        self._sync_buttons()

    def _on_lock_requested(self) -> None:
        self.btn_edit.set_active(False)
        self._update_button_tooltips()
        self._sync_buttons()

    def _update_button_tooltips(self) -> None:
        self.btn_edit.setToolTip(
            i18n.tr("exit_edit") if self.bar.is_edit() else i18n.tr("enter_edit")
        )
        self.btn_close.setToolTip(i18n.tr("hide"))

    def _on_geometry_changed(self, rect: QRect) -> None:
        self._sync_buttons()

    def _on_commit(self, rect: QRect) -> None:
        self.cfg["geometry"] = [rect.x(), rect.y(), rect.width(), rect.height()]
        cfg_mod.save_config(self.cfg)
        self._sync_buttons()

    def _sync_buttons(self) -> None:
        if not self.bar.isVisible():
            self.btn_edit.hide()
            self.btn_close.hide()
            return
        g = self.bar.frameGeometry()
        size = self.btn_close.width()
        y = g.center().y() - size // 2
        x_close = g.right() - BTN_MARGIN - size
        x_edit = x_close - BTN_GAP - size
        self.btn_close.move(x_close, y)
        self.btn_edit.move(x_edit, y)
        for b in (self.btn_edit, self.btn_close):
            b.show()
            b.raise_()

    # ----- geometry --------------------------------------------------------

    def _apply_initial_geometry(self) -> None:
        saved = self.cfg.get("geometry")
        if saved:
            self.bar.set_bar_geometry(*saved)
        else:
            screen = self.app.primaryScreen()
            self.bar.set_bar_geometry(
                *default_geometry(screen.size().width(), screen.size().height())
            )

    def _reset_position(self) -> None:
        self._ensure_visible()
        screen = self.app.primaryScreen()
        self.bar.set_bar_geometry(
            *default_geometry(screen.size().width(), screen.size().height())
        )
        rect = self.bar.geometry()
        self.cfg["geometry"] = [rect.x(), rect.y(), rect.width(), rect.height()]
        cfg_mod.save_config(self.cfg)
        self._sync_buttons()

    # ----- appearance ------------------------------------------------------

    def _set_color(self, hex_color: str) -> None:
        self._ensure_visible()
        self.bar.set_color(hex_color)
        self.cfg["color"] = hex_color
        cfg_mod.save_config(self.cfg)

    def _pick_color(self) -> None:
        self._ensure_visible()
        current = QColor(self.cfg["color"])
        chosen = QColorDialog.getColor(current, None, i18n.tr("custom_color"))
        if chosen.isValid():
            self._set_color(chosen.name())

    def _set_opacity(self, value: float) -> None:
        self._ensure_visible()
        self.bar.set_opacity(value)
        self.cfg["opacity"] = value
        cfg_mod.save_config(self.cfg)

    # ----- language --------------------------------------------------------

    def _set_language(self, lang: str) -> None:
        i18n.set_language(lang)
        self.cfg["language"] = lang
        cfg_mod.save_config(self.cfg)
        self._rebuild_menu()
        self._update_button_tooltips()

    # ----- tray / menu -----------------------------------------------------

    def _rebuild_menu(self) -> None:
        self.menu = self._build_menu()
        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip(i18n.tr("app_name"))
        self.tray.show()

    def _build_menu(self) -> QMenu:
        menu = QMenu()

        toggle = QAction(i18n.tr("toggle"), menu)
        toggle.triggered.connect(self.toggle_visible)
        menu.addAction(toggle)

        pos_menu = menu.addMenu(i18n.tr("position"))
        reset = pos_menu.addAction(i18n.tr("reset_position"))
        reset.triggered.connect(self._reset_position)

        edit = menu.addAction(i18n.tr("enter_edit"))
        edit.triggered.connect(self._on_edit_clicked)

        appearance = menu.addMenu(i18n.tr("appearance"))
        color_menu = appearance.addMenu(i18n.tr("color"))
        for hex_color, key in COLOR_PRESETS:
            act = color_menu.addAction(i18n.tr(key))
            act.triggered.connect(lambda _ch=False, h=hex_color: self._set_color(h))
        custom = color_menu.addAction(i18n.tr("custom_color"))
        custom.triggered.connect(self._pick_color)
        op_menu = appearance.addMenu(i18n.tr("opacity"))
        for key, val in OPACITY_PRESETS:
            act = op_menu.addAction(i18n.tr(key))
            act.triggered.connect(lambda _ch=False, v=val: self._set_opacity(v))

        lang_menu = menu.addMenu(i18n.tr("language"))
        zh = lang_menu.addAction("中文")
        zh.triggered.connect(lambda: self._set_language("zh"))
        en = lang_menu.addAction("English")
        en.triggered.connect(lambda: self._set_language("en"))

        menu.addSeparator()
        quit_act = menu.addAction(i18n.tr("quit"))
        quit_act.triggered.connect(self.app.quit)

        return menu

    # ----- icon ------------------------------------------------------------

    @staticmethod
    def _make_icon() -> QIcon:
        pm = QPixmap(64, 64)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#000000"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(6, 24, 52, 16, 5, 5)
        p.end()
        return QIcon(pm)
