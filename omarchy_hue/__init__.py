"""Omarchy-Hue Package

Shared utilities for syncing Omarchy themes with Philips Hue lights.
"""

import random
import time

# Seed random number generator with current time for true randomness per execution
random.seed(time.time_ns())

__version__ = "1.0.0"

from .config import (
    CONFIG_DIR,
    HUE_CREDENTIALS,
    BRIGHTNESS_CONFIG,
    ROOM_CONFIG,
    DEFAULT_BRIGHTNESS_PERCENT,
    BRIGHTNESS_VARIATION_PERCENT,
)

from .colors import (
    parse_toml_colors,
    get_current_theme,
    get_dominant_colors,
    get_weighted_palette,
    pick_weighted_color,
    hex_to_rgb,
    hex_to_xy,
    clamp_to_gamut,
    add_color_variation,
    percent_to_hue,
)

from .bridge import HueBridge
from .utils import (
    load_brightness,
    save_brightness,
    load_selected_room,
    save_selected_room,
    get_randomized_brightness,
)

__all__ = [
    # Config
    "CONFIG_DIR",
    "HUE_CREDENTIALS",
    "BRIGHTNESS_CONFIG",
    "ROOM_CONFIG",
    "DEFAULT_BRIGHTNESS_PERCENT",
    "BRIGHTNESS_VARIATION_PERCENT",
    # Colors
    "parse_toml_colors",
    "get_current_theme",
    "get_dominant_colors",
    "get_weighted_palette",
    "pick_weighted_color",
    "hex_to_rgb",
    "hex_to_xy",
    "clamp_to_gamut",
    "add_color_variation",
    "percent_to_hue",
    # Bridge
    "HueBridge",
    # Utils
    "load_brightness",
    "save_brightness",
    "load_selected_room",
    "save_selected_room",
    "get_randomized_brightness",
]
