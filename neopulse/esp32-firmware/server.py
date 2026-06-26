# server.py -- NeoPulse HTTP Server
# Blocking polling loop: while True / time.sleep_ms(10)
# Ctrl+C raises KeyboardInterrupt -> handled in main.py
import socket
import time

import ujson
from effects import get_effect, list_effects

from config import get_config, get_system_info, get_wifi_status, update_config

# Set by run_server(driver)
_driver = None


def run_server(driver):
    """Start the HTTP server. Blocks until Ctrl+C."""
    global _driver
    _driver = driver

    port = get_config().get("web", {}).get("port", 8080)
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(4)
    srv.setblocking(False)
    print("Server on port", port, "-- Ctrl+C to stop")

    try:
        while True:
            time.sleep_ms(10)
            try:
                conn, addr = srv.accept()
            except OSError:
                continue  # no connection waiting, loop again

            try:
                _handle(conn)
            except Exception as e:
                print("Handler error:", e)
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
    finally:
        srv.close()  # immer schließen: Ctrl+C oder Exception → kein EADDRINUSE


def _handle(conn):
    conn.settimeout(5)
    data = conn.recv(4096)
    if not data:
        return

    # Parse request line
    line = data.split(b"\r\n")[0].decode("utf-8", "ignore")
    parts = line.split(" ")
    if len(parts) < 2:
        return
    method, path = parts[0], parts[1]

    # Parse body
    body = b""
    hdr_end = data.find(b"\r\n\r\n")
    if hdr_end >= 0:
        body = data[hdr_end + 4 :]
        for h in data[:hdr_end].split(b"\r\n"):
            if h.lower().startswith(b"content-length:"):
                clen = int(h.split(b":")[1].strip())
                while len(body) < clen:
                    try:
                        body += conn.recv(clen - len(body))
                    except Exception:
                        break
                break

    status, ctype, content = _route(method, path, body)

    header = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: {}\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Connection: close\r\n\r\n"
    ).format(status, ctype)
    conn.sendall(header.encode())
    if isinstance(content, str):
        content = content.encode()
    conn.sendall(content)


def _route(method, path, body):
    # Root -> index
    if path == "/":
        path = "/index.html"

    # Static file
    if path == "/index.html":
        return "200 OK", "text/html", _read_file("/web/index.html")

    # CORS preflight
    if method == "OPTIONS":
        return "204 No Content", "text/plain", ""

    # Decode JSON body once
    req = {}
    if body:
        try:
            req = ujson.loads(body.decode("utf-8"))
        except Exception:
            pass

    # --- API routes ---
    if path == "/api/state":
        cfg = get_config()
        r = {
            "status": "ok",
            "num_pixels": _driver.num_pixels if _driver else 0,
            "playing": False,
            "wifi": get_wifi_status(),
            "system": get_system_info(),
            "config": {
                "pin": cfg["neopixel"]["pin"],
                "num_pixels": cfg["neopixel"]["num_pixels"],
                "brightness": cfg.get("brightness", 80),
            },
        }
        return "200 OK", "application/json", ujson.dumps(r)

    if path == "/api/effects":
        return (
            "200 OK",
            "application/json",
            ujson.dumps({"status": "ok", "effects": list_effects()}),
        )

    if path == "/api/info":
        return "200 OK", "application/json", ujson.dumps(get_system_info())

    if path == "/api/effect/run" and method == "POST":
        etype = req.get("type")
        params = req.get("params", {})
        dur = req.get("duration_ms", 5000)
        try:
            cls = get_effect(etype)
            cls.run(_driver, params, dur)
            return "200 OK", "application/json", ujson.dumps({"status": "ok", "effect": etype})
        except Exception as e:
            return "200 OK", "application/json", ujson.dumps({"status": "error", "message": str(e)})

    if path == "/api/pixels/set" and method == "POST":
        if not _driver:
            return (
                "503",
                "application/json",
                ujson.dumps({"status": "error", "message": "driver not ready"}),
            )
        for item in req.get("pixels", []):
            _driver.set_pixel(int(item[0]), tuple(item[1]))
        _driver.write()
        return "200 OK", "application/json", ujson.dumps({"status": "ok"})

    if path == "/api/config/brightness" and method == "POST":
        b = max(0, min(100, int(req.get("brightness", 80))))
        update_config({"brightness": b})
        return "200 OK", "application/json", ujson.dumps({"status": "ok", "brightness": b})

    if path == "/api/pixels/fill" and method == "POST":
        if _driver:
            color = tuple(req.get("color", [0, 0, 0]))
            _driver.fill(color)
            _driver.write()
        return "200 OK", "application/json", ujson.dumps({"status": "ok"})

    return "404 Not Found", "text/plain", "Not Found"


def _read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return "<html><body><h1>Not Found</h1><p>" + path + "</p></body></html>"
