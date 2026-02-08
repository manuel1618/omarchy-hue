# Omarchy-Hue

Sync your Omarchy theme colors with Philips Hue lights.

## Files

- `omarchy-hue-setup` - Interactive TUI for initial setup (discover bridge, authenticate, select room, set brightness)
- `omarchy-hue-sync` - One-liner to quickly sync current theme to selected room
- `.config/` - Local config directory (created automatically). **Do not commit**—it contains credentials.

## Quick Start

```bash
# First time setup
./omarchy-hue-setup

# Then sync anytime
./omarchy-hue-sync
```

## Usage

### Setup (First Time)

Run the interactive setup:

```bash
./omarchy-hue-setup
```

This will:
1. Discover your Hue bridge on the network
2. Authenticate (press the link button on your bridge)
3. Select which room to control
4. Set brightness (default: 20% with ±10% variation)

### Quick Sync

After setup, just run:

```bash
./omarchy-hue-sync
```

This instantly syncs your current Omarchy theme colors to all lights in the selected room.

## How It Works

- Reads colors from `~/.local/share/omarchy-new/themes/<current-theme>/colors.toml`
- Assigns colors randomly to all lights in the room
- Each light gets a different brightness (default 20% ± 10% variation)
- Perfect for ambient lighting!

## Configuration

All config is stored locally in `./.config/` (in the repo directory). **Do not commit this directory**—it contains your Hue bridge credentials.

- `hue-credentials.json` - Bridge IP and authentication
- `selected_room.json` - Selected room ID and name
- `brightness.json` - Brightness setting

## Requirements

- Python 3.6+
- Philips Hue bridge on the same network
- Omarchy Linux with themes in `~/.local/share/omarchy-new/themes/`