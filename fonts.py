import pygame
import os

# Font management
FONT_PATHS = [
    "fonts/Roboto-Regular.ttf",
]

_cached_fonts = {}

def get_font(size, bold=False, italic=False):
    """Return a Pygame font, using custom TTF if available."""
    key = (size, bold, italic)
    if key in _cached_fonts:
        return _cached_fonts[key]

    font = None
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                print(f"Loaded custom font: {path}")
                break
            except Exception as e:
                print(f"Failed to load {path}: {e}")
    if font is None:
        print("Custom font not found, using system font.")
        font = pygame.font.SysFont(None, size, bold, italic)

    _cached_fonts[key] = font
    return font