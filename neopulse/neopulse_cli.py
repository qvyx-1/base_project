#!/usr/bin/env python3
"""NeoPulse CLI — Steuere deinen ESP32 NeoPixel-Streifen direkt vom Terminal."""
import json
import urllib.request
import time
import sys

ESP = "192.168.0.91"  # <-- Hier ggf. deine IP eintragen
PORT = 8080

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

def status():
    r = api("GET", "/api/info")
    s = api("GET", "/api/state")
    print(f"\n{'='*45}")
    print(f"  NeoPulse @ {ESP}:{PORT}")
    print(f"  Chip:     {r.get('chip','?')}")
    print(f"  CPU:      {r.get('cpu_freq',0)//1000000} MHz")
    print(f"  RAM frei: {r.get('free_mem',0)//1024} KB")
    print(f"  Pixels:   {s.get('num_pixels',0)} @ Pin {s.get('config',{}).get('pin','?')}")
    print(f"  Helligk.: {s.get('config',{}).get('brightness',100)}%")
    print(f"  WiFi:     {s.get('wifi',{}).get('sta',{}).get('ip','-')}")
    print(f"{'='*45}\n")

def effect(name, params=None, duration=8):
    if params is None: params = {}
    print(f"▶ Starte {name} ({duration}s)...")
    r = api("POST", "/api/effect/run", {"type": name, "params": params, "duration_ms": duration*1000})
    print(f"  Antwort: {r.get('status','?')}")
    return r

def brightness(val):
    r = api("POST", "/api/config/brightness", {"brightness": val})
    print(f"Helligkeit: {r.get('brightness',val)}%")

def pixel(idx, r, g, b):
    api("POST", "/api/pixels/set", {"pixels": [[idx, [r,g,b]]]})

def fill(r, g, b):
    pixels = [[i, [r,g,b]] for i in range(64)]
    api("POST", "/api/pixels/set", {"pixels": pixels})
    print(f"Alle Pixel: ({r},{g},{b})")

def reset():
    print("⚠ ESP32 Neustart...")
    api("POST", "/api/restart/soft")
    time.sleep(1)
    for _ in range(30):
        try:
            s = api("GET", "/api/state")
            if s.get("status") == "ok": break
        except: pass
        time.sleep(1)
    print("ESP32 wieder online.\n")

def menu():
    while True:
        print()
        print("╔══════════════════════════════════╗")
        print("║      NEOBPULSE CLI  v1.0         ║")
        print("╠══════════════════════════════════╣")
        print("║ 1) ⚡  Strobe                   ║")
        print("║ 2) 🔥 Fire (Feuer)              ║")
        print("║ 3) 🚨 Emergency US               ║")
        print("║ 4) 🇩🇪 Blaulicht DE              ║")
        print("║ 5) 🌈 Rainbow                    ║")
        print("║ 6) 💫 Breathing                  ║")
        print("║                                 ║")
        print("║ 7) 🎨 Pixel setzen              ║")
        print("║ 8) 🎨 Alle Pixel füllen          ║")
        print("║ 9) 💡 Helligkeit                ║")
        print("║ ═                               ║")
        print("║ s) Status anzeigen              ║")
        print("║ r) ⚠ ESP32 neustarten          ║")
        print("║ q) Beenden                      ║")
        print("╚══════════════════════════════════╝")
        print()

        c = input("❯ ").strip().lower()

        if c == "1":
            freq = input("  Frequenz (Hz) [3]: ").strip()
            freq = float(freq) if freq else 3.0
            effect("strobe", {"frequency": freq}, duration=10)
        elif c == "2":
            intensity = input("  Intensität (0.1-1.0) [1.0]: ").strip()
            intensity = float(intensity) if intensity else 1.0
            effect("fire", {"intensity": intensity}, duration=12)
        elif c == "3":
            freq = input("  Frequenz (Hz) [2]: ").strip()
            freq = float(freq) if freq else 2.0
            effect("emergency_us", {"frequency": freq}, duration=10)
        elif c == "4":
            freq = input("  Frequenz (Hz) [1.5]: ").strip()
            freq = float(freq) if freq else 1.5
            effect("emergency_de", {"frequency": freq}, duration=10)
        elif c == "5":
            speed = input("  Speed (0.1-5.0) [1.0]: ").strip()
            speed = float(speed) if speed else 1.0
            effect("rainbow", {"speed": speed}, duration=12)
        elif c == "6":
            freq = input("  Frequenz (Hz) [0.5]: ").strip()
            freq = float(freq) if freq else 0.5
            effect("breathing", {"frequency": freq}, duration=10)
        elif c == "7":
            idx = int(input("  Pixel # (0-63): "))
            r = int(input("  Rot (0-255): "))
            g = int(input("  Grün (0-255): "))
            b = int(input("  Blau (0-255): "))
            pixel(idx, r, g, b)
        elif c == "8":
            r = int(input("  Rot (0-255): "))
            g = int(input("  Grün (0-255): "))
            b = int(input("  Blau (0-255): "))
            fill(r, g, b)
        elif c == "9":
            v = int(input("  Helligkeit (0-100): "))
            brightness(v)
        elif c == "s":
            status()
        elif c == "r":
            reset()
        elif c == "q":
            print("Tschüss! 👋")
            sys.exit(0)
        else:
            print("❌ Unbekannte Eingabe")

if __name__ == "__main__":
    status()
    menu()
