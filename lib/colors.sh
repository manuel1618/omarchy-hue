#!/bin/bash
# Omarchy-Hue Color Utilities
# Color parsing, conversion, and palette management

# ============================================================================
# Theme Detection & File Resolution
# ============================================================================

colors_get_current_theme() {
    if command -v omarchy-theme-current &>/dev/null; then
        omarchy-theme-current | tr '[:upper:]' '[:lower:]' | tr ' ' '-'
    else
        echo "gruvbox"
    fi
}

colors_find_theme_file() {
    local theme="$1"
    local theme_nodash="${theme//-/}"
    
    # Priority 1: ~/.local/share/omarchy/themes/<theme>/colors.toml
    local path="$HOME/.local/share/omarchy/themes/$theme/colors.toml"
    if [[ -f "$path" ]]; then
        echo "$path"
        return 0
    fi
    
    # Priority 1b: Try without dashes
    path="$HOME/.local/share/omarchy/themes/$theme_nodash/colors.toml"
    if [[ -f "$path" ]]; then
        echo "$path"
        return 0
    fi
    
    # Priority 2: ~/.local/share/omarchy-new/themes/<theme>/colors.toml
    if [[ -d "$HOME/.local/share/omarchy-new" ]]; then
        path="$HOME/.local/share/omarchy-new/themes/$theme/colors.toml"
        if [[ -f "$path" ]]; then
            echo "$path"
            return 0
        fi
        
        path="$HOME/.local/share/omarchy-new/themes/$theme_nodash/colors.toml"
        if [[ -f "$path" ]]; then
            echo "$path"
            return 0
        fi
    fi
    
    # Priority 3: ~/.config/omarchy/themes/<theme>/alacritty.toml (old format)
    path="$HOME/.config/omarchy/themes/$theme/alacritty.toml"
    if [[ -f "$path" ]]; then
        echo "$path"
        return 0
    fi
    
    path="$HOME/.config/omarchy/themes/$theme_nodash/alacritty.toml"
    if [[ -f "$path" ]]; then
        echo "$path"
        return 0
    fi
    
    return 1
}

# ============================================================================
# TOML Parsing
# ============================================================================

colors_parse_toml() {
    local file="$1"
    
    # Simple TOML parser for key = "value" format
    # Returns: key=value pairs (one per line)
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        
        # Parse key = "value" or key = 'value'
        if [[ "$line" =~ ^[[:space:]]*([a-z_0-9]+)[[:space:]]*=[[:space:]]*[\"\'](#[0-9a-fA-F]{6})[\"\'] ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            echo "${key}=${value}"
        fi
    done < "$file"
}

colors_parse_alacritty() {
    local file="$1"
    local current_section=""
    
    # Parse alacritty.toml [colors.*] sections
    # Map to standard color names
    while IFS= read -r line; do
        # Track section
        if [[ "$line" =~ ^\[colors\.(.+)\] ]]; then
            current_section="${BASH_REMATCH[1]}"
            continue
        fi
        
        # Skip non-color sections
        [[ -z "$current_section" ]] && continue
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        
        # Parse key = "value"
        if [[ "$line" =~ ^[[:space:]]*([a-z_]+)[[:space:]]*=[[:space:]]*[\"\'](#[0-9a-fA-F]{6})[\"\'] ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            
            # Map alacritty color names to standard names
            case "$current_section.$key" in
                primary.background) echo "background=$value" ;;
                primary.foreground) echo "foreground=$value" ;;
                cursor.cursor) echo "cursor=$value" ;;
                cursor.text) echo "cursor_text=$value" ;;
                selection.background) echo "selection_background=$value" ;;
                selection.text) echo "selection_foreground=$value" ;;
                normal.black) echo "color0=$value" ;;
                normal.red) echo "color1=$value" ;;
                normal.green) echo "color2=$value" ;;
                normal.yellow) echo "color3=$value" ;;
                normal.blue) echo "color4=$value" ;;
                normal.magenta) echo "color5=$value" ;;
                normal.cyan) echo "color6=$value" ;;
                normal.white) echo "color7=$value" ;;
                bright.black) echo "color8=$value" ;;
                bright.red) echo "color9=$value" ;;
                bright.green) echo "color10=$value" ;;
                bright.yellow) echo "color11=$value" ;;
                bright.blue) echo "color12=$value" ;;
                bright.magenta) echo "color13=$value" ;;
                bright.cyan) echo "color14=$value" ;;
                bright.white) echo "color15=$value" ;;
            esac
        fi
    done < "$file"
}

# ============================================================================
# Color Palette Generation
# ============================================================================

colors_get_palette() {
    local theme
    theme=$(colors_get_current_theme)
    
    local theme_file
    theme_file=$(colors_find_theme_file "$theme")
    
    if [[ -z "$theme_file" ]]; then
        return 1
    fi
    
    # Parse based on file type
    local colors
    if [[ "$theme_file" == *.toml ]] && [[ "$theme_file" == */colors.toml ]]; then
        colors=$(colors_parse_toml "$theme_file")
    else
        colors=$(colors_parse_alacritty "$theme_file")
    fi
    
    # Build weighted palette
    # Format: name:hex:weight (one per line)
    # Weights: foreground/background=3, accent=1, color0-15=1, selection=0.3, cursor=0 (excluded)
    
    while IFS='=' read -r key value; do
        case "$key" in
            foreground|background)
                echo "$key:$value:3"
                ;;
            accent)
                echo "$key:$value:1"
                ;;
            color[0-9]|color1[0-5])
                echo "$key:$value:1"
                ;;
            selection_foreground|selection_background)
                echo "$key:$value:0.3"
                ;;
            cursor|cursor_text)
                # Excluded (weight 0) - skip
                ;;
        esac
    done <<< "$colors"
}

colors_pick_weighted() {
    local palette="$1"  # Palette as multiline string
    
    # Convert fractional weights to integers for bash random selection
    # 0.3 -> 3, 1 -> 10, 3 -> 30
    local -a names=()
    local -a hexes=()
    local -a weights=()
    
    while IFS=':' read -r name hex weight; do
        # Convert weight to integer (multiply by 10, handle decimals)
        local int_weight
        if [[ "$weight" == "0.3" ]]; then
            int_weight=3
        elif [[ "$weight" == "1" ]]; then
            int_weight=10
        elif [[ "$weight" == "3" ]]; then
            int_weight=30
        else
            # Fallback: try to parse with bash (strip decimal)
            int_weight=$(printf "%.0f" "${weight//./}0" 2>/dev/null || echo 10)
        fi
        
        names+=("$name")
        hexes+=("$hex")
        weights+=("$int_weight")
    done <<< "$palette"
    
    # Calculate total weight
    local total_weight=0
    for w in "${weights[@]}"; do
        total_weight=$((total_weight + w))
    done
    
    # Pick random weighted color
    local random=$((RANDOM % total_weight))
    local cumulative=0
    
    for i in "${!names[@]}"; do
        cumulative=$((cumulative + weights[i]))
        if [[ $random -lt $cumulative ]]; then
            echo "${names[i]}:${hexes[i]}"
            return 0
        fi
    done
    
    # Fallback (should never reach here)
    echo "${names[0]}:${hexes[0]}"
}

# ============================================================================
# Color Conversion Functions
# ============================================================================

colors_hex_to_rgb() {
    local hex="$1"
    hex="${hex#\#}"  # Remove # if present
    
    local r=$((16#${hex:0:2}))
    local g=$((16#${hex:2:2}))
    local b=$((16#${hex:4:2}))
    
    echo "$r $g $b"
}

colors_apply_gamma() {
    local value="$1"  # 0-255
    
    # Simplified gamma correction using integer math (fixed-point with 10000 scale)
    # For sRGB: if (normalized > 0.04045) pow((normalized + 0.055) / 1.055, 2.4) else normalized / 12.92
    # We'll use a simplified approximation: pow(value/255, 2.2) for speed
    
    # Scale: 0-255 -> 0-10000 for fixed-point
    local normalized=$((value * 10000 / 255))
    
    # Simplified gamma 2.2 approximation: (x^2.2) ≈ (x^2 * x^0.2)
    # For simplicity, we'll use x^2 as approximation (close enough for LED color matching)
    local result=$((normalized * normalized / 10000))
    
    echo "$result"
}

colors_rgb_to_xyz() {
    local r="$1"
    local g="$2"
    local b="$3"
    
    # Apply gamma correction (returns 0-10000 scale)
    local r_norm g_norm b_norm
    r_norm=$(colors_apply_gamma "$r")
    g_norm=$(colors_apply_gamma "$g")
    b_norm=$(colors_apply_gamma "$b")
    
    # Convert to XYZ using standard RGB to XYZ matrix
    # Using integer coefficients (scaled by 10000)
    # Original: x = 0.4124*r + 0.3576*g + 0.1805*b
    # Scaled:   x = (4124*r + 3576*g + 1805*b) / 10000
    
    local x y z
    x=$(( (4124 * r_norm + 3576 * g_norm + 1805 * b_norm) / 10000 ))
    y=$(( (2126 * r_norm + 7152 * g_norm +  722 * b_norm) / 10000 ))
    z=$(( ( 193 * r_norm + 1192 * g_norm + 9505 * b_norm) / 10000 ))
    
    echo "$x $y $z"
}

colors_xyz_to_xy() {
    local x="$1"
    local y="$2"
    local z="$3"
    
    # Convert XYZ to xy chromaticity using integer math
    local total=$((x + y + z))
    
    if [[ $total -eq 0 ]]; then
        echo "0.3127 0.3290"  # D65 white point default
        return
    fi
    
    # Scale to get 4 decimal places: multiply by 10000, divide, then format
    local xy_x_scaled=$((x * 10000 / total))
    local xy_y_scaled=$((y * 10000 / total))
    
    # Convert to decimal format: 3127 -> 0.3127
    local xy_x="0.$(printf "%04d" $xy_x_scaled)"
    local xy_y="0.$(printf "%04d" $xy_y_scaled)"
    
    echo "$xy_x $xy_y"
}

colors_hex_to_xy() {
    local hex="$1"
    
    # Full conversion pipeline
    local rgb
    rgb=$(colors_hex_to_rgb "$hex")
    read -r r g b <<< "$rgb"
    
    local xyz
    xyz=$(colors_rgb_to_xyz "$r" "$g" "$b")
    read -r x y z <<< "$xyz"
    
    colors_xyz_to_xy "$x" "$y" "$z"
}

colors_clamp_gamut() {
    local xy_x="$1"
    local xy_y="$2"
    
    # Clamp to Philips Hue Gamut C limits using bash string comparison
    # Convert 0.XXXX to integer for comparison (remove 0. prefix)
    # Use 10# prefix to force base-10 interpretation (avoid octal errors with leading zeros)
    local x_int=$((10#${xy_x#0.}))
    local y_int=$((10#${xy_y#0.}))
    
    # Clamp X: 0.1000 to 0.8000
    if [[ $x_int -lt 1000 ]]; then
        xy_x="0.1000"
    elif [[ $x_int -gt 8000 ]]; then
        xy_x="0.8000"
    fi
    
    # Clamp Y: 0.1000 to 0.9000
    if [[ $y_int -lt 1000 ]]; then
        xy_y="0.1000"
    elif [[ $y_int -gt 9000 ]]; then
        xy_y="0.9000"
    fi
    
    echo "$xy_x $xy_y"
}

colors_add_variation() {
    local hex="$1"
    local percent="${2:-5}"
    
    local rgb
    rgb=$(colors_hex_to_rgb "$hex")
    read -r r g b <<< "$rgb"
    
    # Calculate max variation using bash integer math
    local max_variation
    max_variation=$(( (255 * percent) / 100 ))
    
    # Add random variation to each channel
    local variation
    variation=$((RANDOM % (2 * max_variation + 1) - max_variation))
    r=$((r + variation))
    r=$((r < 0 ? 0 : r > 255 ? 255 : r))
    
    variation=$((RANDOM % (2 * max_variation + 1) - max_variation))
    g=$((g + variation))
    g=$((g < 0 ? 0 : g > 255 ? 255 : g))
    
    variation=$((RANDOM % (2 * max_variation + 1) - max_variation))
    b=$((b + variation))
    b=$((b < 0 ? 0 : b > 255 ? 255 : b))
    
    printf "#%02x%02x%02x" "$r" "$g" "$b"
}

colors_percent_to_hue() {
    local percent="$1"
    echo $(( (percent * 254) / 100 ))
}

colors_get_randomized_brightness() {
    local base="$1"
    local variation="${2:-10}"
    
    local min=$((base - variation))
    local max=$((base + variation))
    min=$((min < 0 ? 0 : min))
    max=$((max > 100 ? 100 : max))
    
    local random_percent=$((RANDOM % (max - min + 1) + min))
    colors_percent_to_hue "$random_percent"
}
