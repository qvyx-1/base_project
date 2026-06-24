"""ESP32 HTTP connection module for NeoPulse Studio."""

import json
import socket
import urllib.error
import urllib.request


class ESPConnection:
    """Handles HTTP communication with the ESP32 device."""

    def __init__(self, ip_address: str, port: int = 80, timeout: float = 5.0):
        self.ip = ip_address
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{ip_address}:{port}"

    def _request(self, method: str, path: str, data: dict = None) -> dict:
        """Send an HTTP request to the ESP32 and return JSON response."""
        url = f"{self.base_url}{path}"

        if data is not None:
            body = json.dumps(data).encode("utf-8")
        else:
            body = None

        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = response.read().decode("utf-8")
                return json.loads(result)
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot connect to ESP32 at {self.ip}:{self.port}: {e}")
        except socket.timeout:
            raise ConnectionError(f"Timeout connecting to ESP32 at {self.ip}:{self.port}")

    def get_state(self) -> dict:
        """Get current ESP32 state."""
        return self._request("GET", "/api/state")

    def get_shows(self) -> list:
        """Get all saved shows from ESP32."""
        result = self._request("GET", "/api/shows")
        return result.get("shows", [])

    def save_show(self, show_data: dict) -> dict:
        """Save a show to ESP32 flash storage."""
        return self._request("POST", "/api/shows", show_data)

    def get_show(self, show_id: str) -> dict:
        """Get a specific show by ID."""
        result = self._request("GET", f"/api/shows/{show_id}")
        return result.get("show", {})

    def delete_show(self, show_id: str) -> dict:
        """Delete a show from ESP32."""
        return self._request("DELETE", f"/api/shows/{show_id}")

    def play_show(self, show_id: str) -> dict:
        """Start playing a show on the ESP32."""
        return self._request("POST", "/api/play", {"show_id": show_id})

    def set_pixels(self, pixels: list) -> dict:
        """Set individual pixel colors. pixels = [(index, (r,g,b)), ...]"""
        return self._request("POST", "/api/pixels/set", {"pixels": pixels})

    def run_effect(self, effect_type: str, params: dict = None, duration_ms: int = 5000) -> dict:
        """Run an effect on the ESP32."""
        return self._request(
            "POST",
            "/api/effect/run",
            {
                "type": effect_type,
                "params": params or {},
                "duration_ms": duration_ms,
            },
        )

    def configure_wifi(self, ssid: str, password: str) -> dict:
        """Configure WiFi credentials on the ESP32."""
        return self._request(
            "POST",
            "/api/config/wifi",
            {
                "ssid": ssid,
                "password": password,
            },
        )

    def restart(self, soft: bool = True) -> dict:
        """Restart the ESP32."""
        path = "/api/restart/soft" if soft else "/api/restart/hard"
        return self._request("POST", path, {})

    def set_brightness(self, brightness: int) -> dict:
        """Set LED brightness (0-100)."""
        return self._request(
            "POST",
            "/api/config/brightness",
            {
                "brightness": max(0, min(100, brightness)),
            },
        )

    def get_effects(self) -> dict:
        """Get list of available effects."""
        return self._request("GET", "/api/effects")

    def get_info(self) -> dict:
        """Get ESP32 system information."""
        return self._request("GET", "/api/info")

    def ping(self) -> bool:
        """Check if the ESP32 is reachable."""
        try:
            state = self.get_state()
            return state.get("status") == "ok"
        except (ConnectionError, Exception):
            return False

    def discover(self) -> list:
        """Try to discover ESP32 on local network (basic implementation)."""
        # Try common IPs in local subnet
        import ipaddress

        discovered = []

        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Scan local subnet
            network = ipaddress.ip_network(local_ip + "/24", strict=False)

            for host in list(network.hosts())[:50]:  # Scan first 50 IPs
                esp = ESPConnection(str(host), timeout=1.0)
                if esp.ping():
                    discovered.append(
                        {
                            "ip": str(host),
                            "state": esp.get_state(),
                        }
                    )
        except Exception as e:
            print(f"Discovery error: {e}")

        return discovered
