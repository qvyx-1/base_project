#!/usr/bin/env python3
"""NeoPulse CLI — Steuere deinen ESP32 NeoPixel-Streifen direkt vom Terminal.

Erweiterte Version mit Block-Definitionen, lokaler Effekt-Simulation
und paralleler Block-Wiedergabe via /api/pixels/set.
"""

import json
import math
import sys
import time
import urllib.request

ESP = "192.168.0.91"
PORT = 8080
NUM_PIXELS = 64

blocks: list[dict] = []


def hsv_to_rgb(h, s, v):
    s_norm = s / 255.0
    v_norm = v / 255.0
    c = v_norm * s_norm
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v_norm - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def color_mul(color, factor):
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))


# --- Lokale Effekt-Simulation ---


def compute_strobe(block, t):
    freq = block.get("params", {}).get("frequency", 3.0)
    color = block.get("params", {}).get("color", (255, 255, 255))
    phase = (t * freq) % 2
    c = color if phase < 1 else (0, 0, 0)
    return [c] * (block["end"] - block["start"] + 1)


def compute_fire(block, t):
    intensity = block.get("params", {}).get("intensity", 1.0)
    n = block["end"] - block["start"] + 1
    colors = []
    for i in range(n):
        r = min(255, int(255 * intensity * (0.7 + 0.3 * math.sin(i * 0.5 + t * 3))))
        g = min(255, int(180 * intensity * max(0, 0.4 + 0.6 * math.sin(i * 0.3 + t * 2.5))))
        colors.append((r, g, 0))
    return colors


def compute_emergency_us(block, t):
    freq = block.get("params", {}).get("frequency", 2.0)
    c_red = block.get("params", {}).get("color_red", (255, 0, 0))
    c_blue = block.get("params", {}).get("color_blue", (0, 0, 255))
    c = c_red if (t * freq) % 2 < 1 else c_blue
    return [c] * (block["end"] - block["start"] + 1)


def compute_emergency_de(block, t):
    freq = block.get("params", {}).get("frequency", 1.5)
    c_blue = block.get("params", {}).get("color_blue", (0, 0, 255))
    phase = (t * freq) % 4
    if phase < 0.5:
        c = c_blue
    elif phase < 1.0:
        c = (0, 0, 0)
    elif phase < 2.0:
        c = c_blue if int(t * 12.5) % 2 else (0, 0, 0)
    else:
        c = (0, 0, 0)
    return [c] * (block["end"] - block["start"] + 1)


def compute_rainbow(block, t):
    speed = block.get("params", {}).get("speed", 1.0)
    start, n = block["start"], block["end"] - block["start"] + 1
    return [
        hsv_to_rgb((start + i) * 360 // NUM_PIXELS + t * 50 * speed, 255, 255) for i in range(n)
    ]


def compute_breathing(block, t):
    freq = block.get("params", {}).get("frequency", 0.5)
    color = block.get("params", {}).get("color", (255, 255, 255))
    pt = (t * freq) % 2
    if pt > 1:
        pt = 2 - pt
    bri = int(255 * (math.sin(pt * math.pi / 2) ** 2))
    c = (int(color[0] * bri / 255), int(color[1] * bri / 255), int(color[2] * bri / 255))
    return [c] * (block["end"] - block["start"] + 1)


EFFECT_REGISTRY = {
    "strobe": {"fn": compute_strobe, "defaults": {"frequency": 3.0, "color": (255, 255, 255)}},
    "fire": {"fn": compute_fire, "defaults": {"intensity": 1.0}},
    "emergency_us": {
        "fn": compute_emergency_us,
        "defaults": {"frequency": 2.0, "color_red": (255, 0, 0), "color_blue": (0, 0, 255)},
    },
    "emergency_de": {
        "fn": compute_emergency_de,
        "defaults": {"frequency": 1.5, "color_blue": (0, 0, 255)},
    },
    "rainbow": {"fn": compute_rainbow, "defaults": {"speed": 1.0}},
    "breathing": {
        "fn": compute_breathing,
        "defaults": {"frequency": 0.5, "color": (255, 255, 255)},
    },
}

# --- API ---


def api(method, path, data=None):
    url = f"http://{ESP}:{PORT}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"status": "error", "message": str(e)}


def send_pixels(pixel_list):
    api("POST", "/api/pixels/set", {"pixels": [[i, list(c)] for i, c in pixel_list]})


def status():
    r = api("GET", "/api/state")
    print(f"\n{'=' * 45}")
    print(f"  NeoPulse @ {ESP}:{PORT}")
    print(f"  Pixels: {r.get('num_pixels', 0)} @ Pin {r.get('config', {}).get('pin', '?')}")
    print(f"  Brightness: {r.get('config', {}).get('brightness', 100)}%")
    print(f"  WiFi: {r.get('wifi', {}).get('sta', {}).get('ip', '-')}")
    print(f"{'=' * 45}")
    if blocks:
        print("  Blocks:")
        for i, b in enumerate(blocks):
            eff = b.get("effect") or "-"
            print(
                f"    {i}: {b['name']} [{b['start']}-{b['end']}] {b.get('brightness', 100)}% -> {eff}"
            )


def effect(name, params=None, duration=8):
    if params is None:
        params = {}
    print(f"  Starting {name} ({duration}s)...")
    r = api(
        "POST", "/api/effect/run", {"type": name, "params": params, "duration_ms": duration * 1000}
    )
    print(f"  -> {r.get('status', '?')}")


def create_block():
    print("\n-- New Block --")
    name = input("  Name: ").strip()
    if not name:
        return
    try:
        start = int(input("  Start LED: "))
        end = int(input("  End LED:   "))
    except ValueError:
        print("  Invalid number")
        return
    if start < 0 or end >= NUM_PIXELS or start > end:
        print(f"  Invalid range (0-{NUM_PIXELS - 1})")
        return
    br = max(0, min(100, int(input("  Brightness % [100]: ").strip() or "100")))
    blocks.append(
        {"name": name, "start": start, "end": end, "brightness": br, "effect": None, "params": {}}
    )
    print(f"  OK: '{name}' [{start}-{end}] {br}%")


def assign_effect():
    if not blocks:
        print("  No blocks. Create one first (b).")
        return
    for i, b in enumerate(blocks):
        print(f"  [{i}] {b['name']} [{b['start']}-{b['end']}]")
    try:
        idx = int(input("\n  Block #: "))
    except ValueError:
        return
    if idx < 0 or idx >= len(blocks):
        return
    eff_names = list(EFFECT_REGISTRY.keys())
    for i, n in enumerate(eff_names):
        print(f"    [{i}] {n}")
    try:
        e_idx = int(input("  Effect # (Enter=none): ").strip())
        eff_name = eff_names[e_idx]
    except (ValueError, IndexError):
        blocks[idx]["effect"] = None
        blocks[idx]["params"] = {}
        print("  Effect removed.")
        return
    reg = EFFECT_REGISTRY[eff_name]
    params = dict(reg["defaults"])
    blocks[idx]["effect"] = eff_name
    blocks[idx]["params"] = params
    print(f"  OK: {blocks[idx]['name']} -> {eff_name}")


def play_blocks():
    active = [b for b in blocks if b.get("effect")]
    if not active:
        print("  No effects assigned. Use 'e' first.")
        return
    print(f"  Playing {len(active)} block effects... (Ctrl+C to stop)")
    s = api("GET", "/api/state")
    global_br = s.get("config", {}).get("brightness", 100) / 100.0
    try:
        t0 = time.time()
        while True:
            t = time.time() - t0
            all_px = [(0, 0, 0)] * NUM_PIXELS
            for b in blocks:
                fn = EFFECT_REGISTRY.get(b.get("effect"), {}).get("fn")
                if not fn:
                    continue
                colors = fn(b, t)
                block_br = b.get("brightness", 100) / 100.0
                if block_br < 1.0:
                    colors = [color_mul(c, block_br) for c in colors]
                for off, c in enumerate(colors):
                    idx = b["start"] + off
                    if idx < NUM_PIXELS:
                        all_px[idx] = c
            if global_br < 1.0:
                all_px = [color_mul(c, global_br) for c in all_px]
            send_pixels(list(enumerate(all_px)))
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n  Stopped.")
        send_pixels([(i, (0, 0, 0)) for i in range(NUM_PIXELS)])
        time.sleep(0.05)
        send_pixels([(i, (0, 0, 0)) for i in range(NUM_PIXELS)])


def menu():
    while True:
        print("\n╔══════════════════════════════╗")
        print("║   NEOPULSE CLI  v2.0        ║")
        print("╠══════════════════════════════╣")
        print("║ 1) Strobe     2) Fire       ║")
        print("║ 3) Emerg US   4) Blaulicht  ║")
        print("║ 5) Rainbow    6) Breathing  ║")
        print("║                              ║")
        print("║ b) New block                 ║")
        print("║ e) Assign effect to block     ║")
        print("║ t) Play blocks               ║")
        print("║ T) Stop all                  ║")
        print("║ 9) Brightness                ║")
        print("║ s) Status                    ║")
        print("║ q) Quit                      ║")
        print("╚══════════════════════════════╝")
        c = input("> ").strip().lower()

        if c == "1":
            effect("strobe", {"frequency": 3.0})
        elif c == "2":
            effect("fire", {"intensity": 1.0})
        elif c == "3":
            effect("emergency_us", {"frequency": 2.0})
        elif c == "4":
            effect("emergency_de", {"frequency": 1.5})
        elif c == "5":
            effect("rainbow", {"speed": 1.0})
        elif c == "6":
            effect("breathing", {"frequency": 0.5})
        elif c == "9":
            v = int(input("  Brightness (0-100): "))
            api("POST", "/api/config/brightness", {"brightness": v})
            print(f"  OK: {v}%")
        elif c == "b":
            create_block()
        elif c == "e":
            assign_effect()
        elif c == "t":
            play_blocks()
        elif c == "T":
            send_pixels([(i, (0, 0, 0)) for i in range(NUM_PIXELS)])
            print("  Stopped.")
        elif c == "s":
            status()
        elif c == "q":
            print("Bye!")
            sys.exit(0)
        else:
            print("  Unknown")


if __name__ == "__main__":
    status()
    menu()
