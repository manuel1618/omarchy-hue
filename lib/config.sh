#!/bin/bash
# Omarchy-Hue Configuration Management
# Handles reading/writing JSON config files using jq

# Get the repo root directory (parent of lib/)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$REPO_ROOT/.config"

# Config file paths
HUE_CREDENTIALS="$CONFIG_DIR/hue-credentials.json"
ROOM_CONFIG="$CONFIG_DIR/selected_room.json"
BRIGHTNESS_CONFIG="$CONFIG_DIR/brightness.json"

# Defaults
DEFAULT_BRIGHTNESS=20
BRIGHTNESS_VARIATION=10

# Ensure config directory exists
mkdir -p "$CONFIG_DIR"

# ============================================================================
# Credentials Functions
# ============================================================================

config_get_bridge_ip() {
    if [[ -f "$HUE_CREDENTIALS" ]]; then
        jq -r '.bridge_ip // empty' "$HUE_CREDENTIALS" 2>/dev/null
    fi
}

config_get_username() {
    if [[ -f "$HUE_CREDENTIALS" ]]; then
        jq -r '.username // empty' "$HUE_CREDENTIALS" 2>/dev/null
    fi
}

config_save_credentials() {
    local bridge_ip="$1"
    local username="$2"
    
    jq -n \
        --arg ip "$bridge_ip" \
        --arg user "$username" \
        '{bridge_ip: $ip, username: $user}' > "$HUE_CREDENTIALS"
}

config_has_credentials() {
    [[ -f "$HUE_CREDENTIALS" ]] && [[ -n "$(config_get_username)" ]]
}

# ============================================================================
# Room Functions
# ============================================================================

config_get_room_id() {
    if [[ -f "$ROOM_CONFIG" ]]; then
        jq -r '.id // empty' "$ROOM_CONFIG" 2>/dev/null
    fi
}

config_get_room_name() {
    if [[ -f "$ROOM_CONFIG" ]]; then
        jq -r '.name // empty' "$ROOM_CONFIG" 2>/dev/null
    fi
}

config_save_room() {
    local room_id="$1"
    local room_name="$2"
    
    jq -n \
        --arg id "$room_id" \
        --arg name "$room_name" \
        '{id: $id, name: $name}' > "$ROOM_CONFIG"
}

config_has_room() {
    [[ -f "$ROOM_CONFIG" ]] && [[ -n "$(config_get_room_id)" ]]
}

# ============================================================================
# Brightness Functions
# ============================================================================

config_get_brightness() {
    if [[ -f "$BRIGHTNESS_CONFIG" ]]; then
        local brightness
        brightness=$(jq -r '.brightness // empty' "$BRIGHTNESS_CONFIG" 2>/dev/null)
        if [[ -n "$brightness" ]]; then
            echo "$brightness"
            return
        fi
    fi
    echo "$DEFAULT_BRIGHTNESS"
}

config_save_brightness() {
    local brightness="$1"
    jq -n --arg bri "$brightness" '{brightness: ($bri | tonumber)}' > "$BRIGHTNESS_CONFIG"
}

# ============================================================================
# Utility Functions
# ============================================================================

config_check_dependencies() {
    local missing=()
    command -v jq &>/dev/null || missing+=("jq")
    command -v curl &>/dev/null || missing+=("curl")
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Error: Missing required dependencies: ${missing[*]}" >&2
        echo "Install with: sudo pacman -S ${missing[*]}" >&2
        return 1
    fi
    return 0
}

config_get_variation() {
    echo "$BRIGHTNESS_VARIATION"
}
