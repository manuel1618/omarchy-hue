#!/bin/bash
# Shared functions for patching omarchy-theme-set

patch_set_theme() {
    if [[ ! -f "$THEME_SET_SCRIPT" ]]; then
        echo "Warning: omarchy-theme-set not found at: $THEME_SET_SCRIPT" >&2
        echo "You'll need to manually call omarchy-hue-sync after theme changes" >&2
        return 1
    fi

    if grep -q "# Omarchy-Hue Integration" "$THEME_SET_SCRIPT"; then
        echo "✓ omarchy-theme-set already patched (skipping)" >&2
        return 0
    fi

    if grep -q "^omarchy-hook theme-set" "$THEME_SET_SCRIPT"; then
        sed -i '1a\
# Omarchy-Hue Integration - Sync lights with theme (runs in parallel)\
if command -v omarchy-hue-sync &>/dev/null; then\
  (omarchy-hue-sync 2>&1 | logger -t omarchy-hue) &\
fi\
' "$THEME_SET_SCRIPT"
        echo "✓ Patched omarchy-theme-set for automatic sync" >&2
    else
        echo "Warning: Could not find 'omarchy-hook theme-set' line in script" >&2
        echo "Manual integration may be required" >&2
        return 1
    fi

    return 0
}

unpatch_set_theme() {
    if [[ ! -f "$THEME_SET_SCRIPT" ]]; then
        echo "  (omarchy-theme-set not present, nothing to unpatch)" >&2
        return 0
    fi

    if grep -q "# Omarchy-Hue Integration" "$THEME_SET_SCRIPT"; then
        sed -i '/# Omarchy-Hue Integration/,/^fi$/d' "$THEME_SET_SCRIPT"
        echo "✓ Removed Omarchy-Hue patch from omarchy-theme-set" >&2
    else
        echo "  (no patch found, leaving current version intact)" >&2
    fi

    return 0
}