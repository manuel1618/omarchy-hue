#!/usr/bin/env python3
"""
Omarchy-Hue Quick Sync
One-liner to sync current theme to selected room
"""

import sys
import random

from omarchy_hue import (
    HueBridge,
    HUE_CREDENTIALS,
    ROOM_CONFIG,
    get_current_theme,
    get_weighted_palette,
    pick_weighted_color,
    hex_to_xy,
    clamp_to_gamut,
    add_color_variation,
    load_brightness,
    get_randomized_brightness,
)


def main():
    """Quick sync - no interactive UI"""
    import json

    # Load config
    if not HUE_CREDENTIALS.exists():
        print("Error: Not authenticated. Run omarchy-hue-setup first.")
        sys.exit(1)

    if not ROOM_CONFIG.exists():
        print("Error: No room selected. Run omarchy-hue-setup first.")
        sys.exit(1)

    with open(ROOM_CONFIG, 'r') as f:
        room_data = json.load(f)
        room_id = room_data.get("id")

    if not room_id:
        print("Error: No room selected. Run omarchy-hue-setup first.")
        sys.exit(1)

    # Initialize
    bridge = HueBridge()

    if not bridge.username:
        print("Error: Not authenticated. Run omarchy-hue-setup first.")
        sys.exit(1)

    try:
        # Get theme
        current_theme = get_current_theme()

        # Get lights
        room_lights = bridge.get_room_lights(room_id)

        if not room_lights:
            print("Error: No lights found in selected room")
            sys.exit(1)

        color_lights = [l for l in room_lights if bridge.light_supports_color(l["id"])]

        if not color_lights:
            print("Error: No color-capable lights in room")
            sys.exit(1)

        # Get brightness
        base_brightness = load_brightness()

        # Get weighted palette
        palette = get_weighted_palette()

        if not palette:
            print("Error: No colors found for theme")
            sys.exit(1)

        # Sync - each lamp gets a weighted random color from the palette
        success_count = 0
        for light in color_lights:
            # Pick color based on weights (accent/foreground/background/selection = high, color0-15 = mid, cursor = none)
            color_name, hex_color = pick_weighted_color(palette)

            # Add slight variation to the color
            hex_color = add_color_variation(hex_color, variation_percent=5.0)

            xy_x, xy_y = hex_to_xy(hex_color)
            xy_x, xy_y = clamp_to_gamut(xy_x, xy_y)

            light_brightness = get_randomized_brightness(base_brightness)

            state = {
                "on": True,
                "bri": light_brightness,
                "xy": [round(xy_x, 4), round(xy_y, 4)]
            }

            if bridge.set_light_state(light["id"], state):
                success_count += 1

        print(f"✓ Synced {success_count}/{len(color_lights)} lights with {current_theme} theme @ {base_brightness}% (weighted palette)")
        sys.exit(0)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
