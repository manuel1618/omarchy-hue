# Omarchy-Hue

Sync Omarchy theme colors with Philips Hue lights.

## Installation

**Prerequisite:** Omarchy must be installed first.

```bash
# Clone this repository
git clone https://github.com/manuel1618/omarchy-hue.git ~/omarchy-hue

# Run the installer (requires Omarchy to be installed)
~/omarchy-hue/bin/omarchy-hue-install
```

After installation, run the setup to configure your Hue bridge:

```bash
omarchy-hue-setup
```

Lights sync automatically when you change themes via `omarchy-theme-set`.

## Usage

```bash
omarchy-hue-sync          # Manual sync
omarchy-hue-setup         # Reconfigure (includes sync mode)
omarchy-hue-reset         # Reset lights to white
omarchy-hue-uninstall     # Remove from system
```

### Sync Modes

In setup (option 7), choose between:
- **Group** (default) - All lights same color, fast (1 API request)
- **Individual** - Random color per light, slower (N requests)

## Requirements

- Philips Hue bridge on local network
- `jq`, `curl`, `notify-send` (already in Omarchy)
