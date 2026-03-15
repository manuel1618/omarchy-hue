#!/bin/bash
# Omarchy-Hue Bridge API Client
# Handles all Philips Hue Bridge API interactions using curl

DISCOVERY_URL="https://discovery.meethue.com"

# ============================================================================
# Helper Functions
# ============================================================================

_validate_ip() {
    local ip="$1"
    [[ "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
}

# ============================================================================
# Discovery & Connection
# ============================================================================

hue_discover() {
    local response
    response=$(curl -s --max-time 10 "$DISCOVERY_URL" 2>/dev/null)
    
    if [[ -n "$response" ]]; then
        echo "$response" | jq -r '.[0].internalipaddress // empty' 2>/dev/null
    fi
}

hue_test_connection() {
    local bridge_ip="$1"
    
    if ! _validate_ip "$bridge_ip"; then
        return 1
    fi
    
    local response
    response=$(curl -s --max-time 5 "http://$bridge_ip/api/config" 2>/dev/null)
    [[ -n "$response" ]]
}

hue_register() {
    local bridge_ip="$1"
    
    if ! _validate_ip "$bridge_ip"; then
        echo "Error: Invalid IP address" >&2
        return 1
    fi
    
    local hostname
    hostname=$(hostname)
    local devicetype="omarchy-hue-sync#$hostname"
    
    local response
    response=$(curl -s --max-time 5 \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"devicetype\":\"$devicetype\"}" \
        "http://$bridge_ip/api" 2>/dev/null)
    
    # Check for success
    local username
    username=$(echo "$response" | jq -r '.[0].success.username // empty' 2>/dev/null)
    
    if [[ -n "$username" ]]; then
        echo "$username"
        return 0
    fi
    
    # Check for error
    local error_type
    error_type=$(echo "$response" | jq -r '.[0].error.type // empty' 2>/dev/null)
    
    if [[ "$error_type" == "101" ]]; then
        echo "Error: Link button not pressed on bridge" >&2
        return 1
    else
        local error_desc
        error_desc=$(echo "$response" | jq -r '.[0].error.description // "Unknown error"' 2>/dev/null)
        echo "Error: $error_desc" >&2
        return 1
    fi
}

# ============================================================================
# Authenticated API Calls
# ============================================================================

hue_api_get() {
    local endpoint="$1"
    local bridge_ip="$2"
    local username="$3"
    
    if ! _validate_ip "$bridge_ip"; then
        echo "Error: Invalid IP address" >&2
        return 1
    fi
    
    curl -s --connect-timeout 2 --max-time 5 \
        "http://$bridge_ip/api/$username$endpoint" 2>/dev/null
}

hue_api_put() {
    local endpoint="$1"
    local data="$2"
    local bridge_ip="$3"
    local username="$4"
    
    if ! _validate_ip "$bridge_ip"; then
        echo "Error: Invalid IP address" >&2
        return 1
    fi
    
    curl -s --connect-timeout 2 --max-time 5 \
        -X PUT \
        -H "Content-Type: application/json" \
        -d "$data" \
        "http://$bridge_ip/api/$username$endpoint" 2>/dev/null
}

# ============================================================================
# Rooms & Lights
# ============================================================================

hue_get_rooms() {
    local bridge_ip="$1"
    local username="$2"
    
    local response
    response=$(hue_api_get "/groups" "$bridge_ip" "$username")
    
    # Filter only Room type groups and convert to array
    echo "$response" | jq -c '
        to_entries 
        | map(select(.value.type == "Room") 
        | {id: .key, name: .value.name, lights: .value.lights})
        | sort_by(.name)' 2>/dev/null
}

hue_get_lights() {
    local bridge_ip="$1"
    local username="$2"
    
    local response
    response=$(hue_api_get "/lights" "$bridge_ip" "$username")
    
    # Convert to array with id embedded
    echo "$response" | jq -c '
        to_entries 
        | map({id: .key, name: .value.name, type: .value.type, state: .value.state})' 2>/dev/null
}

hue_get_room_lights() {
    local room_id="$1"
    local bridge_ip="$2"
    local username="$3"
    
    # Get all rooms
    local rooms
    rooms=$(hue_get_rooms "$bridge_ip" "$username")
    
    # Find the specific room
    local room_light_ids
    room_light_ids=$(echo "$rooms" | jq -r --arg rid "$room_id" '
        .[] | select(.id == $rid) | .lights | .[]' 2>/dev/null)
    
    if [[ -z "$room_light_ids" ]]; then
        echo "[]"
        return
    fi
    
    # Get all lights
    local all_lights
    all_lights=$(hue_get_lights "$bridge_ip" "$username")
    
    # Filter to only lights in this room
    local result="["
    local first=true
    while IFS= read -r light_id; do
        local light
        light=$(echo "$all_lights" | jq -c --arg lid "$light_id" '.[] | select(.id == $lid)' 2>/dev/null)
        if [[ -n "$light" ]]; then
            if [[ "$first" == true ]]; then
                first=false
            else
                result+=","
            fi
            result+="$light"
        fi
    done <<< "$room_light_ids"
    result+="]"
    
    echo "$result"
}

hue_set_light_state() {
    local light_id="$1"
    local state_json="$2"
    local bridge_ip="$3"
    local username="$4"
    
    hue_api_put "/lights/$light_id/state" "$state_json" "$bridge_ip" "$username" >/dev/null
}

hue_set_group_action() {
    local group_id="$1"
    local action_json="$2"
    local bridge_ip="$3"
    local username="$4"
    
    hue_api_put "/groups/$group_id/action" "$action_json" "$bridge_ip" "$username" >/dev/null
}
