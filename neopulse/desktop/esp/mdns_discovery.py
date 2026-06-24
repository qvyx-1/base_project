"""mDNS discovery module for NeoPulse Studio."""

import socket


class MDNSDiscovery:
    """Discovers NeoPulse ESP32 devices on the local network using mDNS/Bonjour."""

    # mDNS group and port
    MDNS_GROUP = "224.0.0.251"
    MDNS_PORT = 5353

    # Service type for NeoPulse
    SERVICE_TYPE = "_neopulse._tcp.local."

    def __init__(self):
        self._discovered = []
        self._running = False
        self._thread = None

    def start_discovery(self, timeout: float = 5.0) -> list:
        """Start mDNS discovery and return found devices."""
        self._discovered = []

        # Use UDP multicast to discover services
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.settimeout(timeout)

            # Send PTR query for our service type
            query = self._build_query(self.SERVICE_TYPE)
            sock.sendto(query, (self.MDNS_GROUP, self.MDNS_PORT))

            # Also try simple HTTP ping on common IPs
            local_devices = self._scan_local_subnet()
            self._discovered.extend(local_devices)

        except Exception as e:
            print(f"mDNS discovery error: {e}")

        return self._discovered

    def _build_query(self, service_type: str) -> bytes:
        """Build a simple mDNS PTR query."""
        # Simple DNS query for PTR record
        packet = bytearray()

        # Header: ID, flags, question count
        packet += b"\x00\x00"  # ID
        packet += b"\x01\x00"  # Flags: standard query
        packet += b"\x00\x01"  # Questions: 1
        packet += b"\x00\x00"  # Answer RRs: 0
        packet += b"\x00\x00"  # Authority RRs: 0
        packet += b"\x00\x00"  # Additional RRs: 0

        # Question: PTR for service type
        for part in service_type.split("."):
            packet += bytes([len(part)]) + part.encode()
        packet += b"\x00"  # End of name

        # Query type: PTR (12), class: IN (1)
        packet += b"\x00\x0c"  # Type
        packet += b"\x00\x01"  # Class

        return bytes(packet)

    def _scan_local_subnet(self) -> list:
        """Scan local subnet for ESP32 devices by pinging common IPs."""
        discovered = []

        try:
            # Get local IP to determine subnet
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Extract first 3 octets
            parts = local_ip.split(".")
            subnet = ".".join(parts[:3])

            # Scan IPs in subnet (limit to avoid slow scans)
            for i in range(1, 30):
                ip = f"{subnet}.{i}"
                if self._ping_device(ip):
                    discovered.append(
                        {
                            "ip": ip,
                            "hostname": f"neopulse-{ip.split('.')[-1]}",
                            "service_type": self.SERVICE_TYPE,
                        }
                    )
        except Exception as e:
            print(f"Subnet scan error: {e}")

        return discovered

    def _ping_device(self, ip: str, timeout: float = 0.5) -> bool:
        """Check if an ESP32 device responds on port 80."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 80))
            sock.close()
            return result == 0
        except:
            return False

    def discover_by_http(self, subnet: str = None) -> list:
        """Discover devices by trying HTTP requests."""
        discovered = []

        if subnet is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                parts = local_ip.split(".")
                subnet = ".".join(parts[:3])
            except:
                subnet = "192.168.1"

        for i in range(1, 50):
            ip = f"{subnet}.{i}"
            try:
                import urllib.request

                url = f"http://{ip}:80/api/state"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=1) as resp:
                    data = eval(resp.read().decode())  # Simple eval for MicroPython JSON
                    if data.get("status") == "ok":
                        discovered.append(
                            {
                                "ip": ip,
                                "state": data,
                                "hostname": f"neopulse-{i}",
                            }
                        )
            except:
                pass

        return discovered


# Convenience function
def discover_neopulse_devices(timeout: float = 5.0) -> list:
    """Quick function to discover NeoPulse devices."""
    discovery = MDNSDiscovery()

    # Try mDNS first
    devices = discovery.start_discovery(timeout)

    # Also try HTTP scan
    http_devices = discovery.discover_by_http()

    # Merge results
    seen_ips = {d["ip"] for d in devices}
    for d in http_devices:
        if d["ip"] not in seen_ips:
            devices.append(d)
            seen_ips.add(d["ip"])

    return devices
