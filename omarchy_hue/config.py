"""Omarchy-Hue Configuration

Shared configuration constants and paths.
"""

from pathlib import Path

# Config in repo root (no subfolder)
CONFIG_DIR = Path(__file__).parent.parent.resolve() / ".config"
OMARCHY_NEW = Path.home() / ".local" / "share" / "omarchy-new"
THEMES_DIR = OMARCHY_NEW / "themes"
HUE_CREDENTIALS = CONFIG_DIR / "hue-credentials.json"
BRIGHTNESS_CONFIG = CONFIG_DIR / "brightness.json"
ROOM_CONFIG = CONFIG_DIR / "selected_room.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Default brightness settings
DEFAULT_BRIGHTNESS_PERCENT = 20
BRIGHTNESS_VARIATION_PERCENT = 10
