"""Omarchy-Hue Bridge Client

Philips Hue Bridge API client.
"""

import json
import socket
import urllib.request
from pathlib import Path
from .config import HUE_CREDENTIALS


def _validate_bridge_ip(bridge_ip: str) -> bool:
    """Validate bridge IP is a safe IPv4 dotted-quad (no hostnames, paths, or injection)."""
    if not bridge_ip or not isinstance(bridge_ip, str):
        return False
    parts = bridge_ip.strip().split(".")
    if len(parts) != 4:
        return False
    try:
        return all(
            p.isdigit() and 0 <= int(p) <= 255 for p in parts
        )
    except ValueError:
        return False


class HueBridge:
    """Client for Philips Hue Bridge API"""

    DISCOVERY_URL = "https://discovery.meethue.com"

    def __init__(self):
        self.bridge_ip = None
        self.username = None
        self.load_credentials()

    def load_credentials(self):
        """Load stored bridge credentials"""
        if not HUE_CREDENTIALS.exists():
            return
        try:
            with open(HUE_CREDENTIALS, "r", encoding="utf-8") as f:
                creds = json.load(f)
                bridge_ip = creds.get("bridge_ip")
                username = creds.get("username")
            if bridge_ip and _validate_bridge_ip(bridge_ip) and username:
                self.bridge_ip = bridge_ip
                self.username = username
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: could not load credentials from {HUE_CREDENTIALS}: {e}")

    def save_credentials(self):
        """Save bridge credentials"""
        with open(HUE_CREDENTIALS, "w", encoding="utf-8") as f:
            json.dump(
                {"bridge_ip": self.bridge_ip, "username": self.username}, f, indent=2
            )

    def discover(self) -> str:
        """Discover Hue bridge on network using N-UPnP"""
        try:
            with urllib.request.urlopen(
                self.DISCOVERY_URL, timeout=10
            ) as response:
                data = json.loads(response.read().decode())
                if data and len(data) > 0:
                    return data[0].get("internalipaddress")
        except Exception as e:
            print(f"Discovery error: {e}")

        return None

    def test_connection(self, bridge_ip: str) -> bool:
        """Test connection to bridge"""
        if not _validate_bridge_ip(bridge_ip):
            return False
        try:
            with urllib.request.urlopen(
                f"http://{bridge_ip}/api/config", timeout=5
            ) as response:
                return response.status == 200
        except (OSError, ValueError):
            return False

    def register(self, bridge_ip: str) -> str:
        """Register app with bridge (requires button press)"""
        if not _validate_bridge_ip(bridge_ip):
            raise ValueError("Invalid bridge IP address")
        device_name = f"omarchy-hue-sync#{socket.gethostname()}"
        data = json.dumps({"devicetype": device_name}).encode()

        req = urllib.request.Request(
            f"http://{bridge_ip}/api",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode())

                if result and len(result) > 0:
                    if "success" in result[0]:
                        username = result[0]["success"]["username"]
                        self.bridge_ip = bridge_ip
                        self.username = username
                        self.save_credentials()
                        return username
                    elif "error" in result[0]:
                        error_type = result[0]["error"].get("type")
                        if error_type == 101:
                            raise Exception("Link button not pressed on bridge")
                        else:
                            raise Exception(
                                f"Error {error_type}: {result[0]['error'].get('description')}"
                            )
        except Exception as e:
            raise Exception(f"Registration failed: {e}")

        return None

    def api_call(self, method: str, endpoint: str, data: dict = None):
        """Make authenticated API call"""
        if not self.bridge_ip or not self.username:
            raise Exception("Not authenticated with bridge")
        if not _validate_bridge_ip(self.bridge_ip):
            raise ValueError("Invalid bridge IP in credentials")

        url = f"http://{self.bridge_ip}/api/{self.username}{endpoint}"

        if data:
            json_data = json.dumps(data).encode()
            req = urllib.request.Request(
                url,
                data=json_data,
                headers={"Content-Type": "application/json"},
                method=method,
            )
        else:
            req = urllib.request.Request(url, method=method)

        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())

    def get_rooms(self) -> list:
        """Get all rooms from bridge"""
        data = self.api_call("GET", "/groups")
        rooms = []
        for group_id, group_data in data.items():
            if group_data.get("type") == "Room":
                rooms.append(
                    {
                        "id": group_id,
                        "name": group_data.get("name", f"Room {group_id}"),
                        "lights": group_data.get("lights", []),
                    }
                )
        return rooms

    def get_lights(self) -> list:
        """Get all lights from bridge"""
        data = self.api_call("GET", "/lights")
        lights = []
        for light_id, light_data in data.items():
            lights.append(
                {
                    "id": light_id,
                    "name": light_data.get("name", f"Light {light_id}"),
                    "type": light_data.get("type"),
                    "state": light_data.get("state", {}),
                    "modelid": light_data.get("modelid"),
                }
            )
        return lights

    def get_room_lights(self, room_id: str) -> list:
        """Get lights in a specific room"""
        rooms = self.get_rooms()
        room = next((r for r in rooms if r["id"] == room_id), None)

        if not room:
            return []

        all_lights = self.get_lights()
        return [l for l in all_lights if l["id"] in room["lights"]]

    def set_light_state(self, light_id: str, state: dict) -> bool:
        """Set light state (on/off, brightness, color)"""
        try:
            self.api_call("PUT", f"/lights/{light_id}/state", state)
            return True
        except Exception as e:
            print(f"  Error setting light {light_id}: {e}")
            return False

    def light_supports_color(self, light_id: str) -> bool:
        """Check if light supports color changes"""
        try:
            data = self.api_call("GET", f"/lights/{light_id}")
            if "state" in data:
                return "xy" in data["state"] or "hue" in data["state"]
        except Exception:
            pass
        return False
