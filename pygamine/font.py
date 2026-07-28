"""Font loading helper used by panel factories.

Looks up `cfg[font_key]` in the asset manifest first; if no font is registered
under that name, treats it as a system font and falls back to SysFont.
"""

from __future__ import annotations

import pygame


def load_font(cfg: dict, assets, font_key: str = "font", size_key: str = "font_size", bold_key: str = "bold", italic_key: str = "italic") -> pygame.font.Font:
    name = cfg.get(font_key, "Arial")
    size = cfg.get(size_key, 32)
    bold = cfg.get(bold_key, False)
    italic = cfg.get(italic_key, False)

    try:
        return pygame.font.Font(str(assets.font_path(name)), size)
    except KeyError:
        return pygame.font.SysFont(name, size, bold, italic)
