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
omarchy-hue-setup         # Reconfigure
omarchy-hue-reset         # Reset Hue credentials
omarchy-hue-uninstall     # Remove from system
```

## Requirements

- Philips Hue bridge on local network
- `jq`, `curl`, `notify-send` (already in Omarchy)
