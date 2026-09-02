"""Config loading / saving for Subtitle Blocker.

Stores a small JSON file in the platform's per-user config directory:
  - Windows: %APPDATA%/SubtitleBlocker/config.json
  - macOS / Linux: ~/.config/SubtitleBlocker/config.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

APP_NAME = "SubtitleBlocker"

# Default language of the UI before any user choice.
DEFAULT_LANGUAGE = "zh"

DEFAULTS: dict = {
    # Geometry is (x, y, w, h) in screen pixels. None means "use the
    # calibrated default for the current screen" (see defaults.py).
    "geometry": None,
    "color": "#000000",
    "opacity": 1.0,
    "language": DEFAULT_LANGUAGE,
}


def config_dir() -> Path:
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or str(Path.home())
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / APP_NAME


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config() -> dict:
    """Return the config dict (merged over DEFAULTS). Missing file -> defaults."""
    cfg = dict(DEFAULTS)
    path = config_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k in DEFAULTS:
                    if k in data:
                        cfg[k] = data[k]
        except (OSError, ValueError):
            pass
    return cfg


def save_config(cfg: dict) -> None:
    d = config_dir()
    try:
        d.mkdir(parents=True, exist_ok=True)
        tmp = config_path().with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        tmp.replace(config_path())
    except OSError:
        # Non-fatal: the app should keep working even if saving fails.
        pass
