"""Omarchy-Hue Color Utilities

Color parsing, conversion, and palette management.
"""

import re
import random
import math
from pathlib import Path
from .config import THEMES_DIR

# Theme names must be alphanumeric or hyphen only (no path traversal)
_THEME_SAFE_PATTERN = re.compile(r"^[a-z0-9\-]+$")


def _resolve_theme_colors_path(current_theme: str) -> Path:
    """Return path to colors.toml for current_theme, only if under THEMES_DIR.

    Prevents path traversal via malicious or misconfigured theme names.
    Raises FileNotFoundError if theme name is invalid or path would escape THEMES_DIR.
    """
    if not _THEME_SAFE_PATTERN.match(current_theme):
        raise FileNotFoundError(f"Invalid theme name: {current_theme!r}")

    themes_base = THEMES_DIR.resolve()
    for candidate in (
        THEMES_DIR / current_theme / "colors.toml",
        THEMES_DIR / current_theme.replace("-", "") / "colors.toml",
    ):
        try:
            resolved = candidate.resolve()
            if resolved.is_relative_to(themes_base) and candidate.exists():
                return candidate
        except (ValueError, OSError):
            continue
    raise FileNotFoundError(f"colors.toml not found for theme: {current_theme}")


def parse_toml_colors(filepath: Path) -> dict:
    """Parse simple colors.toml format"""
    colors = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                colors[key] = value
    return colors


def get_current_theme() -> str:
    """Get current Omarchy theme name"""
    import subprocess

    try:
        result = subprocess.run(
            ["omarchy-theme-current"], capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip().lower().replace(" ", "-")
    except:
        return "gruvbox"


def get_weighted_palette() -> list:
    """Get full theme palette with weighted probabilities

    Returns list of (name, hex, weight) tuples with weights:
    - foreground: high (3)
    - background: high (3)
    - accent: mid (1)
    - color0-15: mid (1)
    - selection_foreground: low (0.3)
    - selection_background: low (0.3)
    - cursor: none (0) - excluded
    """
    current_theme = get_current_theme()
    colors_file = _resolve_theme_colors_path(current_theme)
    all_colors = parse_toml_colors(colors_file)

    # Define weights
    HIGH_WEIGHT = 3
    MID_WEIGHT = 1
    LOW_WEIGHT = 0.3
    EXCLUDED_WEIGHT = 0

    # Build weighted palette
    weighted_colors = []

    # High priority colors
    high_keys = ["foreground", "background"]
    for key in high_keys:
        if key in all_colors:
            hex_color = all_colors[key]
            if hex_color.startswith("#") and len(hex_color) == 7:
                weighted_colors.append((key, hex_color, HIGH_WEIGHT))

    # Mid priority colors
    mid_keys = ["accent"]
    for key in mid_keys:
        if key in all_colors:
            hex_color = all_colors[key]
            if hex_color.startswith("#") and len(hex_color) == 7:
                weighted_colors.append((key, hex_color, MID_WEIGHT))

    # Terminal colors (color0-15) - mid weight
    for i in range(16):
        key = f"color{i}"
        if key in all_colors:
            hex_color = all_colors[key]
            if hex_color.startswith("#") and len(hex_color) == 7:
                weighted_colors.append((key, hex_color, MID_WEIGHT))

    # Low priority colors (selection colors)
    low_keys = ["selection_foreground", "selection_background"]
    for key in low_keys:
        if key in all_colors:
            hex_color = all_colors[key]
            if hex_color.startswith("#") and len(hex_color) == 7:
                weighted_colors.append((key, hex_color, LOW_WEIGHT))

    # Cursor - excluded (weight 0, so we skip it)
    # Note: cursor is intentionally excluded per requirements

    return weighted_colors


def pick_weighted_color(weighted_palette: list) -> tuple:
    """Pick a random color from weighted palette

    Args:
        weighted_palette: List of (name, hex, weight) tuples

    Returns:
        (name, hex) tuple of selected color
    """
    if not weighted_palette:
        raise ValueError("Empty palette")

    # Separate names, colors, and weights
    names = [item[0] for item in weighted_palette]
    colors = [item[1] for item in weighted_palette]
    weights = [item[2] for item in weighted_palette]

    # Use random.choices for weighted selection
    selected_idx = random.choices(range(len(names)), weights=weights, k=1)[0]
    return (names[selected_idx], colors[selected_idx])


def get_dominant_colors() -> list:
    """Get dominant theme colors as a list of (name, hex) tuples

    Returns a curated palette of the most important colors:
    - accent (primary theme color)
    - foreground (text color)
    - background (base color)
    - cursor (often a contrasting color)
    """
    current_theme = get_current_theme()
    colors_file = _resolve_theme_colors_path(current_theme)
    all_colors = parse_toml_colors(colors_file)

    # Only use dominant colors for the palette
    dominant_keys = ["accent", "foreground", "background", "cursor"]

    color_values = []
    for key in dominant_keys:
        if key in all_colors:
            hex_color = all_colors[key]
            if hex_color.startswith("#") and len(hex_color) == 7:
                color_values.append((key, hex_color))

    return color_values


# Color conversion functions
def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex to RGB tuple"""
    hex_color = hex_color.lstrip("#")
    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def apply_gamma(value: float) -> float:
    """Apply gamma correction to RGB value"""
    if value > 0.04045:
        return pow((value + 0.055) / (1.0 + 0.055), 2.4)
    return value / 12.92


def rgb_to_xyz(r: int, g: int, b: int) -> tuple:
    """Convert RGB to XYZ color space"""
    r_norm = apply_gamma(r / 255.0)
    g_norm = apply_gamma(g / 255.0)
    b_norm = apply_gamma(b / 255.0)

    x = 0.4124 * r_norm + 0.3576 * g_norm + 0.1805 * b_norm
    y = 0.2126 * r_norm + 0.7152 * g_norm + 0.0722 * b_norm
    z = 0.0193 * r_norm + 0.1192 * g_norm + 0.9505 * b_norm

    return (x, y, z)


def xyz_to_xy(x: float, y: float, z: float) -> tuple:
    """Convert XYZ to xy chromaticity coordinates"""
    total = x + y + z
    if total == 0:
        return (0.0, 0.0)
    return (x / total, y / total)


def hex_to_xy(hex_color: str) -> tuple:
    """Convert hex color directly to xy coordinates for Hue"""
    r, g, b = hex_to_rgb(hex_color)
    x, y, z = rgb_to_xyz(r, g, b)
    return xyz_to_xy(x, y, z)


def clamp_to_gamut(xy_x: float, xy_y: float) -> tuple:
    """Clamp xy coordinates to Philips Hue gamut"""
    # Philips Hue Gamut C limits
    xy_x = max(0.1, min(0.8, xy_x))
    xy_y = max(0.1, min(0.9, xy_y))
    return (xy_x, xy_y)


def add_color_variation(hex_color: str, variation_percent: float = 5.0) -> str:
    """Add slight variation to a hex color

    Args:
        hex_color: Original hex color (e.g., "#ff5733")
        variation_percent: Maximum variation percentage (default 5%)

    Returns:
        Modified hex color with slight variation
    """
    r, g, b = hex_to_rgb(hex_color)

    # Calculate variation range
    max_variation = int(255 * (variation_percent / 100))

    # Add random variation to each channel
    r = max(0, min(255, r + random.randint(-max_variation, max_variation)))
    g = max(0, min(255, g + random.randint(-max_variation, max_variation)))
    b = max(0, min(255, b + random.randint(-max_variation, max_variation)))

    return f"#{r:02x}{g:02x}{b:02x}"


def percent_to_hue(percent: int) -> int:
    """Convert percentage (0-100) to Hue brightness value (0-254)"""
    return int((percent / 100.0) * 254)
