"""Omarchy-Hue Utilities

Shared utility functions for config management and brightness handling.
"""

import json
import random
from pathlib import Path
from .config import (
    BRIGHTNESS_CONFIG,
    ROOM_CONFIG,
    DEFAULT_BRIGHTNESS_PERCENT,
    BRIGHTNESS_VARIATION_PERCENT,
)
from .colors import percent_to_hue


def load_brightness() -> int:
    """Load brightness setting from config"""
    if BRIGHTNESS_CONFIG.exists():
        try:
            with open(BRIGHTNESS_CONFIG, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("brightness", DEFAULT_BRIGHTNESS_PERCENT)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: could not load brightness from {BRIGHTNESS_CONFIG}: {e}")
    return DEFAULT_BRIGHTNESS_PERCENT


def save_brightness(brightness: int) -> None:
    """Save brightness setting to config"""
    with open(BRIGHTNESS_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"brightness": brightness}, f)


def load_selected_room() -> dict:
    """Load selected room from config"""
    if ROOM_CONFIG.exists():
        try:
            with open(ROOM_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: could not load room config from {ROOM_CONFIG}: {e}")
    return {"id": None, "name": None}


def save_selected_room(room_id: str, room_name: str) -> None:
    """Save selected room to config"""
    with open(ROOM_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"id": room_id, "name": room_name}, f)


def get_randomized_brightness(base_brightness: int) -> int:
    """Get brightness with ±BRIGHTNESS_VARIATION_PERCENT variation"""
    min_percent = max(0, base_brightness - BRIGHTNESS_VARIATION_PERCENT)
    max_percent = min(100, base_brightness + BRIGHTNESS_VARIATION_PERCENT)
    random_percent = random.randint(min_percent, max_percent)
    return percent_to_hue(random_percent)
