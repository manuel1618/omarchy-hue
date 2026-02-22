# Omarchy-Hue

Sync Omarchy theme colors with Philips Hue lights.

## Quick Start

```bash
git clone ~/omarchy-hue ~/omarchy-hue
cd ~/omarchy-hue
./bin/omarchy-hue-setup
./bin/omarchy-hue-install
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
