#!/usr/bin/env python3
"""
Omarchy-Hue Theme Synchronization TUI
Syncs Omarchy theme colors with Philips Hue lights
"""

import os
import sys
import json
import random

from omarchy_hue import (
    HueBridge,
    HUE_CREDENTIALS,
    ROOM_CONFIG,
    BRIGHTNESS_CONFIG,
    DEFAULT_BRIGHTNESS_PERCENT,
    BRIGHTNESS_VARIATION_PERCENT,
    get_current_theme,
    get_weighted_palette,
    pick_weighted_color,
    hex_to_xy,
    clamp_to_gamut,
    add_color_variation,
    percent_to_hue,
    save_brightness,
    load_selected_room,
    save_selected_room,
    get_randomized_brightness,
)

# Global brightness setting
current_brightness = DEFAULT_BRIGHTNESS_PERCENT


def init_brightness():
    """Initialize brightness from config"""
    global current_brightness
    from omarchy_hue import load_brightness
    current_brightness = load_brightness()


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """Print application header"""
    print("=" * 60)
    print("       Omarchy-Hue Theme Synchronization")
    print("=" * 60)
    print()


def print_status(bridge: HueBridge):
    """Print current status"""
    print("Current Status:")
    print("-" * 60)

    if bridge.bridge_ip:
        print(f"  Bridge: {bridge.bridge_ip}")
        print(f"  Connected: {'Yes' if bridge.username else 'No'}")
    else:
        print(f"  Bridge: Not connected")

    try:
        theme = get_current_theme()
        print(f"  Theme: {theme}")
    except:
        print(f"  Theme: Unknown")

    if selected_room["name"]:
        print(f"  Room: {selected_room['name']}")
    else:
        print(f"  Room: Not selected")

    print(f"  Brightness: {current_brightness}% (±{BRIGHTNESS_VARIATION_PERCENT}%)")

    print("-" * 60)
    print()


def show_menu():
    """Show main menu and return choice"""
    print("Options:")
    print("  1. Discover Hue Bridge")
    print("  2. Connect to Bridge")
    print("  3. Select Room")
    print("  4. Sync Current Theme")
    print(f"  5. Set Brightness (current: {current_brightness}%)")
    print("  6. Exit")
    print()

    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        print("Invalid choice. Please enter 1-6.")


def discover_bridge(bridge: HueBridge):
    """Handle bridge discovery"""
    print("\n🔍 Searching for Hue bridge on your network...")
    print("   This may take a few seconds...")
    print()

    bridge_ip = bridge.discover()

    if bridge_ip:
        if bridge.test_connection(bridge_ip):
            bridge.bridge_ip = bridge_ip
            print(f"✓ Bridge found at: {bridge_ip}")
            print("  Connection test: OK")
        else:
            print(f"⚠ Found bridge at {bridge_ip} but cannot connect")
            print("  Please check your network connection")
    else:
        print("✗ No bridge found on your network")
        print()
        print("Troubleshooting:")
        print("  • Make sure the bridge is powered on")
        print("  • Check that it's connected to your network")
        print("  • Ensure you're on the same network as the bridge")


def connect_bridge(bridge: HueBridge):
    """Handle bridge connection and authentication"""
    if not bridge.bridge_ip:
        print("\n⚠ Please discover the bridge first or enter IP manually:")
        manual_ip = input("   Bridge IP (or press Enter to cancel): ").strip()
        if not manual_ip:
            return

        if not bridge.test_connection(manual_ip):
            print(f"\n✗ Cannot connect to bridge at {manual_ip}")
            return

        bridge.bridge_ip = manual_ip

    print("\n🔗 Connecting to bridge...")
    print(f"   Bridge IP: {bridge.bridge_ip}")
    print()
    print("⚠ IMPORTANT: Press the link button on your Hue bridge")
    print("   (the round button on top of the bridge)")
    print()
    input("   Press Enter when ready...")
    print()

    try:
        username = bridge.register(bridge.bridge_ip)
        if username:
            print("✓ Successfully connected!")
            print(f"   Username: {username[:20]}...")
            print("   Credentials saved for future use")
        else:
            print("✗ Registration failed")
    except Exception as e:
        print(f"✗ Error: {e}")
        if "Link button" in str(e):
            print("\n   Please make sure you pressed the link button")
            print("   You have 30 seconds after pressing it to complete")


def select_room(bridge: HueBridge):
    """Handle room selection"""
    if not bridge.username:
        print("\n⚠ Please connect to the bridge first")
        return

    print("\n📍 Fetching rooms from bridge...")

    try:
        rooms = bridge.get_rooms()

        if not rooms:
            print("✗ No rooms found on your bridge")
            return

        print(f"\nFound {len(rooms)} room(s):\n")

        for i, room in enumerate(rooms, 1):
            light_count = len(room["lights"])
            print(f"  {i}. {room['name']} ({light_count} light{'s' if light_count != 1 else ''})")

        print("  0. Cancel")
        print()

        while True:
            choice = input("Select room: ").strip()

            if choice == "0":
                return

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(rooms):
                    selected_room["id"] = rooms[idx]["id"]
                    selected_room["name"] = rooms[idx]["name"]
                    save_selected_room(selected_room["id"], selected_room["name"])
                    print(f"\n✓ Selected: {selected_room['name']}")
                    return
                else:
                    print("Invalid choice")
            except ValueError:
                print("Please enter a number")

    except Exception as e:
        print(f"\n✗ Error fetching rooms: {e}")


def sync_theme(bridge: HueBridge):
    """Handle theme synchronization"""
    if not bridge.username:
        print("\n⚠ Please connect to the bridge first")
        return

    if not selected_room["id"]:
        print("\n⚠ Please select a room first")
        return

    try:
        current_theme = get_current_theme()
        print(f"\n🎨 Current theme: {current_theme}")
        print()

        # Get weighted palette (accent/foreground/background/selection = high, color0-15 = mid, cursor = none)
        palette = get_weighted_palette()

        if not palette:
            print("✗ No colors found for current theme")
            return

        # Show palette info
        high_count = sum(1 for _, _, w in palette if w == 3)
        mid_count = sum(1 for _, _, w in palette if w == 1)
        low_count = sum(1 for _, _, w in palette if 0 < w < 1)
        print(f"Weighted palette: {len(palette)} colors")
        print(f"  High priority: {high_count} (foreground, background)")
        print(f"  Mid priority: {mid_count} (accent, terminal colors)")
        print(f"  Low priority: {low_count} (selection colors)")
        print(f"  Excluded: cursor")
        print()

        # Get room lights
        print(f"📍 Fetching lights in {selected_room['name']}...")
        room_lights = bridge.get_room_lights(selected_room["id"])

        if not room_lights:
            print("✗ No lights found in selected room")
            return

        color_lights = [l for l in room_lights if bridge.light_supports_color(l["id"])]

        print(f"Found {len(room_lights)} light(s), {len(color_lights)} support color")
        print()

        if not color_lights:
            print("⚠ No color-capable lights in this room")
            print("   Only color bulbs can be synced")
            return

        # Apply colors - each lamp gets a weighted random color from the palette with slight variations
        print("💡 Syncing colors to lights...")
        print(f"   Assigning weighted random colors from {len(palette)}-color palette to {len(color_lights)} lights")
        min_bri = max(0, current_brightness - BRIGHTNESS_VARIATION_PERCENT)
        max_bri = min(100, current_brightness + BRIGHTNESS_VARIATION_PERCENT)
        print(f"   Brightness: {current_brightness}% (range: {min_bri}%-{max_bri}%)")
        print(f"   Colors will have ±5% variation for variety")
        print(f"   (foreground/background have 3x higher chance, selection colors are rare)")
        print()

        success_count = 0

        for light in color_lights:
            # Pick color based on weights (accent/foreground/background/selection = high, color0-15 = mid, cursor = none)
            color_name, hex_color = pick_weighted_color(palette)

            # Add slight variation to the color
            hex_color = add_color_variation(hex_color, variation_percent=5.0)

            # Convert to XY
            xy_x, xy_y = hex_to_xy(hex_color)
            xy_x, xy_y = clamp_to_gamut(xy_x, xy_y)

            # Get randomized brightness for this light
            light_brightness = get_randomized_brightness(current_brightness)

            # Set state
            state = {
                "on": True,
                "bri": light_brightness,
                "xy": [round(xy_x, 4), round(xy_y, 4)]
            }

            if bridge.set_light_state(light["id"], state):
                bri_percent = int((light_brightness / 254) * 100)
                print(f"  ✓ {light['name']} → {color_name} ({hex_color}) @ {bri_percent}%")
                success_count += 1
            else:
                print(f"  ✗ {light['name']} → Failed")

        print()
        print(f"✓ Synced {success_count}/{len(color_lights)} lights")
        print(f"  with {current_theme} weighted palette colors!")

    except FileNotFoundError as e:
        print(f"\n✗ Theme error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def set_brightness():
    """Handle brightness setting"""
    global current_brightness

    print("\n💡 Brightness Settings")
    print("-" * 60)
    print(f"Current brightness: {current_brightness}%")
    print(f"Variation: ±{BRIGHTNESS_VARIATION_PERCENT}%")
    print()
    print("Each light will get a random brightness between")
    print(f"{max(0, current_brightness - BRIGHTNESS_VARIATION_PERCENT)}% and {min(100, current_brightness + BRIGHTNESS_VARIATION_PERCENT)}%")
    print()

    while True:
        try:
            new_brightness = input(f"Enter new brightness (1-100, or press Enter to keep {current_brightness}%): ").strip()

            if not new_brightness:
                print("Brightness unchanged.")
                return

            new_brightness = int(new_brightness)

            if 1 <= new_brightness <= 100:
                current_brightness = new_brightness
                save_brightness(current_brightness)
                print(f"✓ Brightness set to {current_brightness}%")
                print(f"  Lights will vary between {max(0, current_brightness - BRIGHTNESS_VARIATION_PERCENT)}% and {min(100, current_brightness + BRIGHTNESS_VARIATION_PERCENT)}%")
                return
            else:
                print("Please enter a value between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")


# Initialize globals
init_brightness()
selected_room = load_selected_room()


def main():
    """Main application loop"""
    bridge = HueBridge()

    while True:
        clear_screen()
        print_header()
        print_status(bridge)

        choice = show_menu()

        if choice == '1':
            clear_screen()
            print_header()
            discover_bridge(bridge)
            input("\nPress Enter to continue...")

        elif choice == '2':
            clear_screen()
            print_header()
            connect_bridge(bridge)
            input("\nPress Enter to continue...")

        elif choice == '3':
            clear_screen()
            print_header()
            select_room(bridge)
            input("\nPress Enter to continue...")

        elif choice == '4':
            clear_screen()
            print_header()
            sync_theme(bridge)
            input("\nPress Enter to continue...")

        elif choice == '5':
            clear_screen()
            print_header()
            set_brightness()
            input("\nPress Enter to continue...")

        elif choice == '6':
            clear_screen()
            print("\n👋 Goodbye!\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
