# server.py -- HTTP server with API routing for NeoPulse ESP32 firmware
import asyncio

import network
import ujson
from animation_engine import AnimationEngine
from effects import get_effect, list_effects
from neopixel_driver import NeoPixelDriver

from config import get_config, get_system_info, get_wifi_status, update_config

# Global state
driver = None
animation = None
current_show = None
current_effect_task = None
server_task = None


def init_global_state():
    """Initialize global driver and animation objects."""
    global driver, animation
    cfg = get_config()
    np_cfg = cfg["neopixel"]
    driver = NeoPixelDriver(
        pin_num=np_cfg["pin"],
        num_pixels=np_cfg["num_pixels"],
        bpp=np_cfg["bpp"],
        timing=np_cfg["timing"],
    )
    # Set up zones
    for zone in cfg.get("zones", []):
        driver.zones.append((zone["start"], zone["end"], zone["name"]))
    animation = AnimationEngine(driver)


# --- API Handlers ---

def handle_get_state():
    """Handle GET /api/state"""
    colors = driver.get_colors()[:16]  # Send first 16 for preview
    return {
        "status": "ok",
        "pixels": len(colors),
        "num_pixels": driver.num_pixels,
        "current_scene": animation.current_scene["name"] if animation.current_scene else None,
        "playing": animation.running,
        "wifi": get_wifi_status(),
        "system": get_system_info(),
        "config": {
            "brightness": get_config().get("brightness", 100),
            "pin": get_config()["neopixel"]["pin"],
            "num_pixels": get_config()["neopixel"]["num_pixels"],
        },
    }


def handle_get_shows():
    """Handle GET /api/shows"""
    try:
        with open("/shows.json", "r") as f:
            shows = ujson.load(f)
        return {"status": "ok", "shows": shows}
    except OSError:
        return {"status": "ok", "shows": []}


def handle_post_shows(data):
    """Handle POST /api/shows - Save a show"""
    try:
        # Load existing shows
        try:
            with open("/shows.json", "r") as f:
                shows = ujson.load(f)
        except OSError:
            shows = []

        # Check if show exists, update or append
        found = False
        for i, s in enumerate(shows):
            if s.get("id") == data.get("id"):
                shows[i] = data
                found = True
                break

        if not found:
            shows.append(data)

        with open("/shows.json", "w") as f:
            ujson.dump(shows, f)

        return {"status": "ok", "id": data.get("id")}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def handle_get_show(data):
    """Handle GET /api/shows/:id"""
    show_id = data.get("id")
    try:
        with open("/shows.json", "r") as f:
            shows = ujson.load(f)
        for s in shows:
            if s.get("id") == show_id:
                return {"status": "ok", "show": s}
        return {"status": "error", "message": "Show not found"}
    except OSError:
        return {"status": "error", "message": "No shows stored"}


def handle_delete_show(data):
    """Handle DELETE /api/shows/:id"""
    show_id = data.get("id")
    try:
        with open("/shows.json", "r") as f:
            shows = ujson.load(f)
        shows = [s for s in shows if s.get("id") != show_id]
        with open("/shows.json", "w") as f:
            ujson.dump(shows, f)
        return {"status": "ok"}
    except OSError:
        return {"status": "error", "message": "No shows stored"}


def handle_post_play(data):
    """Handle POST /api/play - Start playing a show"""
    global current_show

    show_id = data.get("show_id")
    try:
        with open("/shows.json", "r") as f:
            shows = ujson.load(f)
        for s in shows:
            if s.get("id") == show_id:
                current_show = s
                # Start playing in background
                asyncio.create_task(_play_show_loop(s))
                return {"status": "ok", "show": s["name"]}
        return {"status": "error", "message": "Show not found"}
    except OSError:
        return {"status": "error", "message": "No shows stored"}


async def _play_show_loop(show):
    """Play a show definition with scene transitions."""
    scenes = show.get("scenes", [])

    for scene_def in scenes:
        scene_id = scene_def.get("scene_id")

        # Load the scene
        try:
            with open("/shows.json", "r") as f:
                all_shows = ujson.load(f)
            for s in all_shows:
                if s.get("id") == scene_id:
                    scene = s
                    break
            else:
                continue
        except OSError:
            continue

        # Handle transition
        transition = scene_def.get("transition", "instant")
        if transition == "fade" and scene_def.get("duration", 0) > 0:
            # Simple fade: just play the scene
            pass

        await animation.play_scene(scene)


def handle_post_pixels(data):
    """Handle POST /api/pixels/set - Set individual pixels"""
    pixels = data.get("pixels", [])
    for idx, color in pixels:
        driver.set_pixel(idx, color)
    driver.write()
    return {"status": "ok"}


def handle_post_effect(data):
    """Handle POST /api/effect/run - Run an effect"""
    global current_effect_task

    effect_type = data.get("type")
    params = data.get("params", {})
    duration = data.get("duration_ms", 5000)

    try:
        effect_cls = get_effect(effect_type)
        # Stop any running effect
        animation.stop()

        current_effect_task = asyncio.create_task(_run_effect(effect_cls, params, duration))
        return {"status": "ok", "effect": effect_type}
    except ValueError as e:
        return {"status": "error", "message": str(e)}


async def _run_effect(effect_cls, params, duration_ms):
    """Run an effect for a specified duration."""
    await effect_cls.run(driver, params, duration_ms)


def handle_post_config_wifi(data):
    """Handle POST /api/config/wifi - Configure WiFi"""
    ssid = data.get("ssid", "")
    password = data.get("password", "")

    update_config({"wifi": {"ssid": ssid, "password": password}})

    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connection (max 10 seconds)
    import time
    for _ in range(20):
        if wlan.isconnected():
            break
        time.sleep_ms(500)

    return {
        "status": "ok",
        "connected": wlan.isconnected(),
        "ip": list(wlan.ifconfig())[0] if wlan.isconnected() else "",
    }


def handle_post_restart(data):
    """Handle POST /api/restart/* - Restart ESP32"""
    restart_type = data.get("type", "soft")
    asyncio.create_task(_do_restart(restart_type))
    return {"status": "ok", "restarting": True}


async def _do_restart(restart_type):
    """Perform a restart after sending response."""
    await asyncio.sleep(1)
    if restart_type == "hard":
        import machine
        machine.reset()
    else:
        import machine
        machine.soft_reset()


def handle_post_brightness(data):
    """Handle POST /api/config/brightness - Set brightness"""
    brightness = data.get("brightness", 100)
    brightness = max(0, min(100, brightness))
    update_config({"brightness": brightness})
    return {"status": "ok", "brightness": brightness}


def handle_get_effects():
    """Handle GET /api/effects - List available effects"""
    return {"status": "ok", "effects": list_effects()}


def handle_post_pixels_zone(data):
    """Handle POST /api/pixels/zone - Set zone colors"""
    zone_id = data.get("zone", 0)
    color = tuple(data.get("color", [0, 0, 0]))
    driver.set_zone(zone_id, color)
    driver.write()
    return {"status": "ok"}


def handle_get_info():
    """Handle GET /api/info - System info"""
    return get_system_info()


# --- HTTP Server ---

API_ROUTES = {
    ("GET", "/api/state"): handle_get_state,
    ("GET", "/api/shows"): handle_get_shows,
    ("POST", "/api/shows"): handle_post_shows,
    ("GET", "/api/shows/id"): handle_get_show,
    ("DELETE", "/api/shows/id"): handle_delete_show,
    ("POST", "/api/play"): handle_post_play,
    ("POST", "/api/pixels/set"): handle_post_pixels,
    ("POST", "/api/effect/run"): handle_post_effect,
    ("POST", "/api/config/wifi"): handle_post_config_wifi,
    ("POST", "/api/restart/soft"): lambda d: handle_post_restart({"type": "soft"}),
    ("POST", "/api/restart/hard"): lambda d: handle_post_restart({"type": "hard"}),
    ("POST", "/api/config/brightness"): handle_post_brightness,
    ("GET", "/api/effects"): handle_get_effects,
    ("POST", "/api/pixels/zone"): handle_post_pixels_zone,
    ("GET", "/api/info"): handle_get_info,
}


async def handle_client(reader, writer):
    """Handle a single HTTP client connection."""
    try:
        # Read request line
        request_line = await asyncio.wait_for(reader.readline(), timeout=5)
        if not request_line:
            return

        method, path, _ = request_line.decode("utf-8", errors="replace").strip().split(" ", 2)

        # Read headers
        headers = {}
        content_length = 0
        while True:
            line = await asyncio.wait_for(reader.readline(), timeout=5)
            if line == b"\r\n" or not line:
                break
            key, _, value = line.decode("utf-8", errors="replace").strip().partition(":")
            headers[key.lower()] = value.strip()
            if key.lower() == "content-length":
                content_length = int(value)

        # Read body
        body = b""
        if content_length > 0:
            body = await asyncio.wait_for(reader.readexactly(content_length), timeout=5)

        # Route the request
        status, content_type, response_body = _route_request(method, path, body)

        # Send response
        response = f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n"
        response += response_body
        writer.write(response.encode("utf-8"))
        await writer.drain()

    except Exception as e:
        try:
            error_resp = f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError: {str(e)}"
            writer.write(error_resp.encode("utf-8"))
            await writer.drain()
        except:
            pass
    finally:
        try:
            await asyncio.wait_for(writer.wait_closed(), timeout=1)
        except:
            pass


def _route_request(method, path, body):
    """Route a request to the appropriate handler."""

    # Serve static files from /web/
    if path == "/":
        path = "/index.html"

    static_files = {
        "/index.html": ("text/html", _serve_file("/web/index.html")),
        "/css/style.css": ("text/css", _serve_file("/web/css/style.css")),
        "/js/app.js": ("application/javascript", _serve_file("/web/js/app.js")),
        "/js/editor.js": ("application/javascript", _serve_file("/web/js/editor.js")),
        "/js/timeline.js": ("application/javascript", _serve_file("/web/js/timeline.js")),
    }

    if path in static_files:
        content_type, file_content = static_files[path]
        return "200 OK", content_type, file_content

    # API routes - check exact match first
    key = (method, path)
    if key in API_ROUTES:
        handler = API_ROUTES[key]
        try:
            if method in ("POST", "PUT", "PATCH"):
                data = ujson.loads(body.decode("utf-8")) if body else {}
                result = handler(data)
            else:
                result = handler()
            if isinstance(result, dict):
                return "200 OK", "application/json", ujson.dumps(result)
            return "200 OK", "text/plain", str(result)
        except Exception as e:
            return "200 OK", "application/json", ujson.dumps({"status": "error", "message": str(e)})

    # API routes with path parameters (e.g., /api/shows/123)
    if path.startswith("/api/shows/"):
        parts = path.split("/")
        if len(parts) == 4 and parts[3]:
            show_id = parts[3]
            if method == "GET":
                return "200 OK", "application/json", ujson.dumps(handle_get_show({"id": show_id}))
            elif method == "DELETE":
                return "200 OK", "application/json", ujson.dumps(handle_delete_show({"id": show_id}))

    # 404
    return "404 Not Found", "text/plain", "Not Found"


def _serve_file(path):
    """Read and serve a static file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except OSError:
        return "<html><body>File not found</body></html>"


def start_server():
    """Start the HTTP server (synchronous entry point for main.py)."""
    global server_task

    cfg = get_config()
    port = cfg.get("web", {}).get("port", 8080)

    # Initialize globals
    init_global_state()

    # Start WiFi
    _ensure_wifi()

    # Start server as asyncio task
    loop = asyncio.get_event_loop()
    server_task = loop.create_task(_run_server(port))

    # Run forever
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Server shutting down...")
        if server_task:
            server_task.cancel()
        loop.close()


def _ensure_wifi():
    """Ensure WiFi is active (STA or AP mode)."""
    import network
    cfg = get_config()
    wifi_cfg = cfg["wifi"]

    # Try STA mode
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if wifi_cfg.get("ssid") and wifi_cfg.get("password"):
        sta.connect(wifi_cfg["ssid"], wifi_cfg["password"])
        for _ in range(20):
            if sta.isconnected():
                return
            import time
            time.sleep_ms(500)

    # Fallback to AP mode
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(ssid=wifi_cfg.get("ap_ssid", "NeoPulse-ESP32"))
    if wifi_cfg.get("ap_password"):
        ap.config(password=wifi_cfg["ap_password"])


async def _handle_raw_client(conn):
    """Handle a raw socket client connection."""
    try:
        reader = asyncio.StreamReader()
        reader.set_exception = lambda e: None  # MicroPython compat
        proto = asyncio.StreamReaderProtocol(reader)
    except Exception:
        pass

    try:
        # Read request with raw socket
        conn.setblocking(False)
        data = b""
        for _ in range(50):
            await asyncio.sleep(0.02)
            try:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data:
                    break
            except OSError:
                break

        if not data:
            return

        # Parse HTTP request line
        lines = data.split(b"\r\n")
        if not lines:
            return
        req_line = lines[0].decode("utf-8", "ignore")
        parts = req_line.split(" ")
        if len(parts) < 2:
            return
        method, path = parts[0], parts[1]

        # Parse body (Content-Length)
        body = b""
        header_end = data.find(b"\r\n\r\n")
        if header_end >= 0:
            body = data[header_end + 4:]
            # Try to read remaining body bytes
            for hline in lines[1:]:
                if hline.lower().startswith(b"content-length:"):
                    clen = int(hline.split(b":")[1].strip())
                    while len(body) < clen:
                        await asyncio.sleep(0.01)
                        try:
                            body += conn.recv(clen - len(body))
                        except OSError:
                            break
                    break

        status, content_type, content = _route_request(method, path, body)

        if isinstance(content, str):
            content = content.encode("utf-8")

        response = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            "Connection: close\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "\r\n"
        ).encode("utf-8") + content

        conn.sendall(response)

    except Exception as e:
        try:
            err = f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError: {e}"
            conn.sendall(err.encode("utf-8"))
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


async def _run_server(port):
    """Run the HTTP server using non-blocking sockets (MicroPython compatible)."""
    import socket as _socket

    srv = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    srv.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(5)
    srv.setblocking(False)

    print(f"NeoPulse HTTP server started on port {port}")

    while True:
        await asyncio.sleep(0.01)
        try:
            conn, addr = srv.accept()
            asyncio.create_task(_handle_raw_client(conn))
        except OSError:
            pass


# Initialize on import
try:
    import os
except ImportError:
    pass
