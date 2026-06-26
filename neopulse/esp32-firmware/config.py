# config.py -- Configuration management for ESP32 NeoPulse firmware

import ujson

CONFIG_FILE = "/config.json"
DEFAULT_CONFIG = {
    "wifi": {
        "ssid": "",
        "password": "",
        "mode": "sta",  # 'sta', 'ap', 'dual'
        "ap_ssid": "NeoPulse-ESP32",
        "ap_password": "neopulse123",
    },
    "neopixel": {
        "pin": 21,  # GPIO pin for NeoPixel data
        "num_pixels": 64,  # Max 256
        "bpp": 3,  # 3=RGB, 4=RGBW
        "timing": 1,  # 1=800kHz, 0=400kHz
    },
    "zones": [{"id": 0, "start": 0, "end": 63, "name": "Zone 1"}],
    "web": {
        "port": 8080,
        "password": "",  # Empty = no auth
    },
    "brightness": 100,  # 0-100%
}

_config = None


def _load_config():
    """Load config from flash storage."""
    global _config
    try:
        with open(CONFIG_FILE, "r") as f:
            _config = ujson.load(f)
        # Merge with defaults for any missing keys
        _merge_defaults(_config, DEFAULT_CONFIG)
    except (OSError, ValueError):
        _config = ujson.loads(ujson.dumps(DEFAULT_CONFIG))
        _save_config()


def _merge_defaults(target, source):
    """Recursively merge source defaults into target."""
    for key, value in source.items():
        if key not in target:
            target[key] = value
        elif isinstance(value, dict) and isinstance(target[key], dict):
            _merge_defaults(target[key], value)


def _save_config():
    """Save config to flash storage."""
    try:
        with open(CONFIG_FILE, "w") as f:
            ujson.dump(_config, f)
    except OSError:
        pass


def get_config():
    """Get the current configuration."""
    if _config is None:
        _load_config()
    return _config


def update_config(updates):
    """Update configuration with new values. Returns updated config."""
    if _config is None:
        _load_config()

    def deep_update(base, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                deep_update(base[key], value)
            else:
                base[key] = value

    deep_update(_config, updates)
    _save_config()
    return _config


def gc_free():
    """Get free memory in bytes."""
    import gc

    gc.collect()
    return gc.mem_free()


def get_system_info():
    """Get system information."""
    import machine

    try:
        chip_id = machine.unique_id().hex()
    except Exception:
        chip_id = "unknown"

    return {
        "chip": "ESP32-S3",
        "firmware": "NeoPulse v1.0",
        "cpu_freq": machine.freq(),
        "free_mem": gc_free(),
        "chip_id": chip_id,
        "uptime": _get_uptime_ms(),
    }


def get_wifi_status():
    """Get current WiFi status."""
    import network

    result = {}
    sta = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    if sta.active():
        result["sta"] = {
            "active": sta.active(),
            "connected": sta.isconnected(),
            "ip": sta.ifconfig()[0] if sta.isconnected() else "",
        }
    if ap.active():
        result["ap"] = {
            "active": ap.active(),
            "ip": ap.ifconfig()[0],
            "ssid": get_config()["wifi"]["ap_ssid"],
        }
    return result


def _get_uptime_ms():
    """Get uptime in milliseconds."""
    try:
        import time

        return int(time.time() * 1000)
    except ImportError:
        return 0
