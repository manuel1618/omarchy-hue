# Omarchy-Hue

Sync your Omarchy theme colors with Philips Hue lights. Pure bash implementation - works out of the box with no Python dependencies!

## Features

- 🎨 **Automatic Theme Sync** - Lights automatically update when you change themes
- 🚀 **Minimal Dependencies*** - Just bash and standard Linux tools (jq, curl)

\* Dependencies: `jq curl notify-send` (already present in Omarchy)

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url> ~/omarchy-hue
cd ~/omarchy-hue

# 2. Run interactive setup
./bin/omarchy-hue-setup

# 3. Install to omarchy (adds to PATH and enables automatic sync)
./bin/omarchy-hue-install
```

That's it! Now when you run `omarchy-theme-set <theme>`, your lights will automatically sync.

## Usage

### Initial Setup

Run the interactive setup to configure your Hue bridge:

```bash
./bin/omarchy-hue-setup
```

This will guide you through:
1. **Discover Hue Bridge** - Finds your bridge on the local network
2. **Connect to Bridge** - Authenticate (requires pressing the bridge button)
3. **Select Room** - Choose which room's lights to control
4. **Set Brightness** - Configure base brightness (default: 20% ± 10% variation)
5. **Sync Theme** - Test the sync with your current theme

### Daily Use

After installation, lights sync automatically when you change themes:

```bash
omarchy-theme-set catppuccin   # Lights sync in background
omarchy-theme-set gruvbox       # Lights sync again
```

You can also manually sync anytime:

```bash
omarchy-hue-sync
```

To reconfigure (change room, brightness, etc.):

```bash
omarchy-hue-setup
```

### Installation

Install to your omarchy bin directory:

```bash
./bin/omarchy-hue-install
```

This will:
- Copy `omarchy-hue-sync` and `omarchy-hue-setup` to `~/.local/share/omarchy/bin/`
- Patch `omarchy-theme-set` to automatically call sync on theme changes
- Create a backup of your original `omarchy-theme-set`

### Uninstallation

```bash
./bin/omarchy-hue-uninstall
```

This will:
- Remove scripts from omarchy bin directory
- Restore original `omarchy-theme-set` from backup
- Optionally remove configuration (keeps credentials by default)

## How It Works

### Theme Color Detection

The sync script automatically finds your theme colors in this order:

1. `~/.local/share/omarchy/themes/<theme>/colors.toml` (standard location)
2. `~/.local/share/omarchy-new/themes/<theme>/colors.toml` (if omarchy-new exists)
3. `~/.config/omarchy/themes/<theme>/alacritty.toml` (old format, fallback)

### Weighted Color Palette

Not all colors are treated equally! The palette uses weights to prioritize:

- **High Priority (3x)**: `foreground`, `background` - Your theme's main colors
- **Medium Priority (1x)**: `accent`, `color0-15` - Terminal colors
- **Low Priority (0.3x)**: `selection_foreground`, `selection_background` - Rare accents
- **Excluded**: `cursor` - Too bright/distracting for ambient lighting

This means your lights will mostly show your theme's primary colors, with occasional pops of terminal colors.

### Color Variations

Each light gets:
- A weighted-random color from the palette
- ±5% color variation (so identical colors look slightly different)
- Random brightness in range: `base_brightness ± 10%` (configurable)

This creates a dynamic, ambient lighting effect that feels natural and varied.

### Performance

- **Sync Time**: <1 second for typical setups (3-5 lights)
- **Non-Blocking**: Runs in background, doesn't delay theme changes
- **Silent**: No output unless there's an error (then you get a notification)

## Configuration

All configuration is stored in `./.config/` (in the repo directory):

- `hue-credentials.json` - Bridge IP and authentication username
- `selected_room.json` - Selected room ID and name
- `brightness.json` - Base brightness percentage

**Important**: Don't commit the `.config/` directory - it contains your Hue bridge credentials!

## Requirements

### System Dependencies

- `jq` - JSON parsing
- `curl` - HTTP requests to Hue bridge  
- `notify-send` - Desktop notifications for errors

**All dependencies are already present in Omarchy** - no additional packages needed!

If for some reason you need to install them:
```bash
# Arch Linux
sudo pacman -S jq curl libnotify

# Ubuntu/Debian
sudo apt install jq curl libnotify-bin
```

### Hardware

- Philips Hue bridge on the same local network
- At least one Hue color bulb

### Omarchy

- Omarchy Linux with themes in `~/.local/share/omarchy/themes/`
- `omarchy-theme-set` and `omarchy-theme-current` commands available

## Troubleshooting

### Bridge Not Found

```
✗ No bridge found on your network
```

**Solutions:**
- Make sure your Hue bridge is powered on and connected to the network
- Ensure you're on the same network as the bridge
- Try entering the bridge IP manually in the setup menu

### Authentication Failed

```
✗ Registration failed
Error: Link button not pressed on bridge
```

**Solutions:**
- Press the round button on top of your Hue bridge
- You have 30 seconds after pressing to complete authentication
- Try the "Connect to Bridge" step again

### No Colors Found

```
Error: No colors found for theme: <theme>
```

**Solutions:**
- Make sure the theme exists in `~/.local/share/omarchy/themes/<theme>/`
- Verify the theme has a `colors.toml` or `alacritty.toml` file
- Try running `omarchy-theme-current` to see the actual theme name

### Lights Not Syncing

Check the logs:
```bash
journalctl -t omarchy-hue -f
```

Common issues:
- Bridge network connection lost
- Room has no color-capable lights
- Credentials expired (re-run setup)

## Development

### Project Structure

```
omarchy-hue/
├── bin/
│   ├── omarchy-hue-setup       # Interactive setup TUI
│   ├── omarchy-hue-sync        # Quick sync script
│   ├── omarchy-hue-install     # Installation script
│   └── omarchy-hue-uninstall   # Uninstallation script
├── lib/
│   ├── config.sh              # Config management (jq)
│   ├── hue-api.sh             # Hue Bridge API client (curl)
│   └── colors.sh              # Color parsing & conversion (bc)
└── .config/                    # Config storage (git-ignored)
    ├── hue-credentials.json
    ├── selected_room.json
    └── brightness.json
```

### Contributing

This is a pure bash implementation with **zero external dependencies** beyond what Omarchy already has. When contributing:

- Keep scripts POSIX-compatible where possible
- Use `jq` for JSON parsing (already in Omarchy)
- Use **pure bash integer math** for color conversion (no bc, no awk, no python)
- Test on both new (`colors.toml`) and old (`alacritty.toml`) theme formats
- Color conversion uses fixed-point arithmetic (scaled by 10000) for accuracy
- All math is done with bash's built-in `$(( ))` arithmetic

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Original Python implementation by the Omarchy-Hue team
- Philips Hue API documentation
- Omarchy Linux project for the amazing theme system
