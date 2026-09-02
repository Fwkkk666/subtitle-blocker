"""Calibrated default bar geometry.

The default position is derived from the reference screenshot the user
provided (a 2559x1599 frame): the Chinese subtitle line sits horizontally
centred, roughly 12% of the frame height up from the bottom. We express
every value as a fraction of the *screen* so that the same relative spot is
used on any display, then let the user fine-tune with the drag handles.
"""
from __future__ import annotations

# Horizontal width of the bar as a fraction of the screen width.
BAR_WIDTH_RATIO = 0.55

# Bar height as a fraction of screen height, with a hard minimum in px so the
# strip is still grab-able on very short monitors.
BAR_HEIGHT_RATIO = 0.03
BAR_HEIGHT_MIN_PX = 28

# Vertical position: the bar's centre sits at this fraction of screen height
# measured from the top (0.878 == about 12.2% from the bottom of the screen).
BAR_CENTER_Y_RATIO = 0.878


def default_geometry(screen_w: int, screen_h: int) -> tuple[int, int, int, int]:
    """Return (x, y, w, h) for a fresh bar on a screen of screen_w x screen_h."""
    w = int(screen_w * BAR_WIDTH_RATIO)
    h = max(int(screen_h * BAR_HEIGHT_RATIO), BAR_HEIGHT_MIN_PX)
    cx = screen_w // 2
    cy = int(screen_h * BAR_CENTER_Y_RATIO)
    x = cx - w // 2
    y = cy - h // 2
    return x, y, w, h
