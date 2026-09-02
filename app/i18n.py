"""Minimal i18n for Subtitle Blocker (zh / en).

The default UI language is Chinese; English is selectable from the tray menu.
"""
from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "zh": {
        "app_name": "字幕遮挡器",
        "show": "显示",
        "hide": "隐藏",
        "toggle": "显示 / 隐藏",
        "enter_edit": "进入编辑模式",
        "exit_edit": "锁定(退出编辑)",
        "position": "位置",
        "reset_position": "恢复默认位置",
        "appearance": "外观",
        "color": "颜色",
        "opacity": "透明度",
        "opacity_100": "全额 100%",
        "opacity_90": "较实 90%",
        "opacity_75": "雾面 75%",
        "opacity_50": "半透 50%",
        "opacity_25": "微透 25%",
        "custom_color": "自定义…",
        "color_black": "黑色",
        "color_charcoal": "深灰",
        "color_white": "白色",
        "color_green": "墨绿",
        "color_orange": "橙色",
        "language": "语言",
        "quit": "退出",
    },
    "en": {
        "app_name": "Subtitle Blocker",
        "show": "Show",
        "hide": "Hide",
        "toggle": "Show / Hide",
        "enter_edit": "Enter edit mode",
        "exit_edit": "Lock (exit edit)",
        "position": "Position",
        "reset_position": "Reset position",
        "appearance": "Appearance",
        "color": "Color",
        "opacity": "Opacity",
        "opacity_100": "Solid 100%",
        "opacity_90": "Opaque 90%",
        "opacity_75": "Frosted 75%",
        "opacity_50": "Translucent 50%",
        "opacity_25": "Slight 25%",
        "custom_color": "Custom…",
        "color_black": "Black",
        "color_charcoal": "Charcoal",
        "color_white": "White",
        "color_green": "Green",
        "color_orange": "Orange",
        "language": "Language",
        "quit": "Quit",
    },
}

_current_lang = "zh"


def set_language(lang: str) -> None:
    global _current_lang
    if lang in STRINGS:
        _current_lang = lang


def get_language() -> str:
    return _current_lang


def tr(key: str, **kwargs) -> str:
    text = STRINGS.get(_current_lang, STRINGS["zh"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text
