---
name: neopulse-esp32
description: > 
  Komplette Architektur, Implementierung und Inbetriebnahme des NeoPulse-Projekts
  auf ESP32-S3 mit MicroPython. Enthält HTTP-Webserver (blocking polling loop),
  NeoPixel-Treiber, Effekt-Engine, WiFi-STA/AP-Hybrid-Modus und Web-Interface.
  Enthält verifizierte Lösungen für die drei häufigsten Bugs.
applyTo: neopulse/**
---

# NeoPulse — ESP32-S3 NeoPixel Controller Skill

## 1. Architektur-Übersicht

```
┌──────────────────────────────────────────────────────────┐
│                   ESP32-S3 (MicroPython)                   │
│                                                           │
│  ┌──────────────────────────────┐  ┌──────────────────┐  │
│  │  HTTP Server                 │  │  NeoPixel        │  │
│  │  blocking polling loop       │  │  Driver          │  │
│  │  while True: sleep_ms(10)    │  │  (RMT/GPIO 21)   │  │
│  │  Port 8080                   │  └──────────────────┘  │
│  └──────────────────────────────┘                        │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  WiFi: STA (192.168.0.91) + AP (192.168.4.1)     │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Wichtig:** asyncio ist für dieses Projekt NICHT nötig. Der blocking polling
loop mit `time.sleep_ms(10)` funktioniert zuverlässig:
- `time.sleep_ms()` ist von Ctrl+C unterbrechbar → REPL kehrt zurück
- WiFi-Stack läuft im Hintergrund (MicroPython-Interrupt-basiert)
- Einfacher zu debuggen als asyncio

### Korrekte Architektur (verifiziert mit MicroPython v1.28.0)

```python
# boot.py — NUR CPU-Frequenz, KEIN import main
# Warum: boot.py crasht nie, ESP32 fällt nicht in Download-Modus
import machine
machine.freq(240000000)
print("NeoPulse v1.0 | import main; main.boot()")

# main.py — Server + WiFi, Ctrl+C stoppt sauber
def boot():
    # 1. Config laden
    # 2. WiFi STA versuchen, AP immer aktivieren
    # 3. NeoPixel-Driver erstellen
    # 4. run_server(driver) aufrufen — blockiert, Ctrl+C stoppt
    from server import run_server
    try:
        run_server(driver)          # blockiert hier
    except KeyboardInterrupt:
        print("Server stopped -- REPL available")

# server.py — blocking loop, Driver als Parameter
def run_server(driver):            # Driver MUSS übergeben werden!
    _driver = driver               # Modul-global setzen
    srv = socket.socket()
    srv.setblocking(False)
    while True:
        time.sleep_ms(10)          # Ctrl+C unterbricht hier
        try:
            conn, addr = srv.accept()
        except OSError:
            continue               # keine neue Verbindung, normal
        try:
            _handle(conn)
        except Exception as e:
            print("Handler error:", e)  # NIEMALS except:pass!
```

### Die drei häufigsten Bugs — und warum sie so gefährlich sind

| Bug | Symptom | Warum tückisch | Fix |
|-----|---------|----------------|-----|
| `driver = None` in server.py, nie gesetzt | Server startet, antwortet aber nie auf Requests | `except: pass` schluckt den `AttributeError` lautlos — Connection close ohne HTTP-Response, kein Hinweis im Log | `run_server(driver)` — Driver als Parameter übergeben |
| `except: pass` überall | Keine Fehlermeldungen, alles scheint OK | Alle Exceptions (auch echte Bugs) werden unsichtbar, Server tut so als ob alles ok | `except Exception as e: print("Error:", e)` |
| `machine.reset()` on exception | Jeder Boot-Fehler → sofortiger Neustart | Verhindert jedes Debugging, Fehlermeldung geht verloren, möglicher Reboot-Loop | Fehler ausgeben, NICHT resetten: `import sys; sys.print_exception(e)` |

## 2. Projektstruktur

```
neopulse/
├── README.md                        # Ausführliche Dokumentation
├── neopulse_cli.py                  # CLI-Tool für Terminal-Steuerung
├── upload_firmware.sh               # Upload-Script (mpremote)
├── esp32-firmware/                  # MicroPython Firmware für ESP32
│   ├── boot.py                      # Nur CPU-Freq, kein main-Boot
│   ├── main.py                      # boot() startet WiFi + Server + asyncio
│   ├── config.py                    # JSON-Konfiguration aus Flash
│   ├── server.py                    # asyncio-HTTP-Server mit API-Routing
│   ├── neopixel_driver.py           # NeoPixel-Wrapper (Zonen, HSV→RGB)
│   ├── animation_engine.py          # Keyframe-Interpolation
│   ├── effects/                     # Effekt-Module
│   │   ├── __init__.py              # Registry
│   │   ├── strobe.py                # Blitzlicht
│   │   ├── fire.py                  # Feuer
│   │   ├── emergency_us.py          # US-Rot/Blau
│   │   ├── emergency_de.py          # DE-Blaulicht
│   │   ├── rainbow.py               # Regenbogen
│   │   └── breathing.py             # Atmen
│   ├── web/
│   │   ├── index.html               # Web-Interface (HTML/CSS/JS inline)
│   │   └── js/app.js                # Optional ausgelagert
│   └── do_upload.py                 # Python Upload-Skript (Serial)
├── desktop/                         # Tkinter Desktop App (WIP)
│   ├── models/                      # Datenmodelle
│   ├── esp/                         # ESP32-Kommunikation
│   ├── widgets/                     # UI-Komponenten
│   └── windows/                     # Fenster
└── emulator/
    └── index.html                   # Browser-Simulator
```

## 3. Inbetriebnahme

### 3.1 Voraussetzungen

```bash
# Python 3.9+
python3 --version

# Installieren
pip install pyserial esptool mpremote

# User zur dialout-Gruppe (Linux)
sudo usermod -aG dialout $USER
# → Neuanmeldung erforderlich!
```

### 3.2 MicroPython flashen

**Mit BOOT-Taste:**
1. ESP32 per USB verbinden
2. BOOT-Taste gedrückt HALTEN
3. Befehl ausführen:

```bash
esptool --port /dev/ttyACM0 erase-flash
esptool --port /dev/ttyACM0 --baud 460800 write-flash \
  --flash-mode dio --flash-freq 80m \
  0x0 /pfad/zu/ESP32_GENERIC_S3-*.bin
```
4. BOOT-Taste loslassen
5. RESET drücken (oder kurz BOOT)

**Prüfen:**
```bash
mpremote connect /dev/ttyACM0 exec "print('REPL OK')"
# → b"REPL OK\r\n"
```

### 3.3 Firmware hochladen

**Warum DTR-Reset NICHT funktioniert:**
DTR/RTS-Toggle öffnet und schließt den Serial-Port. Wenn danach `mpremote`
den Port öffnet, setzt dessen `serial.Serial()` DTR/RTS erneut → **Doppel-Reset**.
Der ESP startet zweimal durch, mpremote verpasst das REPL-Fenster →
`TransportError: could not enter raw repl`.

**Korrekte Methode: einmal Ctrl+C, dann mpremote direkt:**

```python
import serial, time, os

PORT = '/dev/ttyACM0'

# 1. Einmalig Ctrl+C senden — unterbricht laufenden Code
s = serial.Serial(PORT, 115200, timeout=0.5)
for _ in range(4):
    s.write(b'\x03')
    time.sleep(0.1)
time.sleep(0.5)
s.read(2000)  # Output leeren
s.close()
time.sleep(0.3)

# 2. mpremote wie gewohnt — kein Reset nötig
os.system('mpremote connect /dev/ttyACM0 cp boot.py :boot.py')
os.system('mpremote connect /dev/ttyACM0 cp server.py :server.py')
# ... für jede Datei
```

**Alle Dateien auf einmal hochladen:**
```bash
cd neopulse/esp32-firmware
python3 upload_fast.py
```

**Was upload_fast.py macht:**
1. Ctrl+C via Serial senden (unterbricht laufenden Server)
2. REPL-Verfügbarkeit prüfen (`mpremote exec "print('REPL OK')"`)
3. Verzeichnisse `effects/` und `web/` anlegen falls nicht vorhanden
4. Alle Dateien einzeln via `mpremote cp` hochladen
5. `config.json` neu schreiben
6. Verify: alle Dateien mit Größe ausgeben

**ESP im Bootloader-Modus (USB-ID `303a:4001` statt `303a:4001` normal)?**
```bash
esptool --port /dev/ttyACM0 run   # startet MicroPython ohne Neu-Flash
```
Danach REPL-Check: `mpremote connect /dev/ttyACM0 exec "print('OK')"`

### 3.4 Server starten

```bash
# REPL öffnen
mpremote connect /dev/ttyACM0

# Im REPL:
import main
main.boot()
```

Server läuft dann so lange bis Ctrl+C gedrückt wird. Nach Ctrl+C ist das REPL
sofort wieder verfügbar — kein Neustart nötig. Der Server-Socket wird im
`finally`-Block geschlossen, d.h. `main.boot()` kann danach direkt erneut
aufgerufen werden (kein `EADDRINUSE`).

### 3.5 Web-Interface öffnen

**Wichtig:** HTML-Interface und API laufen auf **demselben Server, demselben Port**.
Es gibt keinen separaten Webserver — alles läuft auf Port 8080.

| URL | Inhalt |
|-----|--------|
| `http://192.168.0.91:8080/` | Web-Interface (HTML/CSS/JS, 16 KB) |
| `http://192.168.4.1:8080/` | Dasselbe über AP (ohne Router) |
| `http://192.168.0.91:8080/api/state` | JSON API |

Browser auf `http://192.168.0.91:8080/` öffnen — fertig. API-Calls kommen
automatisch vom Web-Interface aus (JavaScript `fetch` auf demselben Host).

### 3.6 API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/state` | Systemstatus, WiFi, NeoPixel-Konfig |
| GET | `/api/effects` | Verfügbare Effekte |
| GET | `/api/info` | Systeminfo (Chip, RAM, CPU) |
| POST | `/api/effect/run` | `{"type":"rainbow","duration_ms":5000}` |
| POST | `/api/pixels/set` | `{"pixels":[[0,[255,0,0]],[1,[0,255,0]]]}` |
| POST | `/api/config/brightness` | `{"brightness":80}` |

**Test via curl:**
```bash
curl http://192.168.0.91:8080/api/state
curl -X POST http://192.168.0.91:8080/api/effect/run \
  -H "Content-Type: application/json" \
  -d '{"type":"rainbow","duration_ms":8000}'

# HTML-Seite laden (gleicher Server, gleicher Port!):
curl -I http://192.168.0.91:8080/
# → HTTP/1.1 200 OK, Content-Type: text/html, 16655 bytes
```

## 4. Fehlerbehebung

### 4.1 "USB JTAG/serial debug unit" (Download-Modus)
- **Ursache:** `boot.py` oder `main.py` crasht → Chip fällt in Bootloader
- **Lösung:** ESP aus/einstecken, dann `esptool --port /dev/ttyACM0 run`
- **Prävention:** `boot.py` minimal halten (NUR CPU-Frequenz)

### 4.2 "could not enter raw repl"
- **Ursache A:** DTR/RTS-Reset vor mpremote → Doppel-Reset, mpremote verpasst REPL
  - **Lösung:** DTR-Reset weglassen, stattdessen Ctrl+C senden (siehe 3.3)
- **Ursache B:** Server läuft noch und blockiert REPL
  - **Lösung:** Ctrl+C via Serial:
  ```python
  import serial, time
  s = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5)
  for _ in range(4): s.write(b'\x03'); time.sleep(0.1)
  time.sleep(0.5); s.read(2000); s.close()
  # Jetzt mpremote aufrufen
  ```
- **Prüfen ob REPL lebt:**
  ```bash
  mpremote connect /dev/ttyACM0 exec "print('alive')"
  ```

### 4.3 OSError: [Errno 112] EADDRINUSE beim Neustart
- **Ursache:** Server-Socket `srv` wird bei Ctrl+C nicht geschlossen → Port bleibt belegt
- **Falsch:** `while True:` ohne `try/finally` um den Loop
- **Richtig:** Server-Socket im `finally` schließen:
  ```python
  try:
      while True:
          time.sleep_ms(10)
          ...
  finally:
      srv.close()   # Ctrl+C oder Exception → Socket wird immer geschlossen
  ```
- Nach diesem Fix: `main.boot()` → Ctrl+C → `main.boot()` funktioniert direkt,
  kein Soft-Reset (`\x04`) nötig
- **Notfall-Reset falls doch EADDRINUSE:**
  ```python
  # Im REPL:
  import machine; machine.soft_reset()  # oder Ctrl+D
  ```

### 4.4 "mpremote: could not access port"
- **Ursache:** Port durch anderen Prozess belegt
- **Lösung:** `sudo fuser -k /dev/ttyACM0`

### 4.5 NeoPixel leuchtet nicht
- **Prüfen:** Richtiger GPIO-Pin? (ESP32-S3 = GPIO 21)
- **Prüfen:** Genug Strom? (5V, >2A für 64 LEDs)
- **Prüfen:** Datenleitung? (WS2812B = GPIO → DIN)

## 5. Wichtige MicroPython Besonderheiten

### Was funktioniert (verifiziert v1.28)
- **`time.sleep_ms(n)`** — funktioniert, von Ctrl+C unterbrechbar
- **`socket.setblocking(False)`** + polling loop — zuverlässiger HTTP-Server
- **`ujson`** statt `json` — MicroPython hat kein `json`-Modul
- **f-strings** — ab MicroPython 1.17 (v1.28 = OK)
- **`KeyboardInterrupt`** propagiert durch `except Exception` — weil KI von `BaseException` erbt, NICHT von `Exception`
- **WiFi-Stack** läuft im Hintergrund auch ohne asyncio

### Was NICHT funktioniert / zu vermeiden
- **`_thread`** — experimentell, instabil, nicht für Produktion
- **`asyncio.sleep_ms()`** — existiert nicht → `await asyncio.sleep(0.01)` falls asyncio
- **`serve_forever()`** — existiert in MicroPython asyncio nicht
- **`except: pass`** — verschluckt alle Fehler inkl. Bugs still, immer `except Exception as e: print(e)`
- **`machine.reset()` on exception** — verhindert Debugging, erzeugt Reboot-Loops
- **DTR/RTS-Reset vor jedem mpremote** — verursacht Doppel-Reset, mpremote schlägt fehl
- **`driver = None` als Modul-Global** — wenn der Driver später übergeben werden muss, immer als Parameter!

### USB-ID des ESP32-S3
- `303a:4001` — normaler Betrieb (MicroPython läuft) **und** manchmal Bootloader
- REPL-Check ist zuverlässiger: `mpremote connect /dev/ttyACM0 exec "print('OK')"`

## 6. Vollständige Server-Implementierung (verifiziert)

```python
# server.py -- blocking polling loop, kein asyncio
import socket, ujson, time
from config import get_config, get_wifi_status, get_system_info, update_config
from effects import list_effects, get_effect

_driver = None   # wird durch run_server(driver) gesetzt

def run_server(driver):
    """Startet den HTTP-Server. Blockiert bis Ctrl+C."""
    global _driver
    _driver = driver                   # WICHTIG: Driver als Parameter!

    port = get_config().get('web', {}).get('port', 8080)
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', port))
    srv.listen(4)
    srv.setblocking(False)
    print('Server on port', port, '-- Ctrl+C to stop')

    while True:
        time.sleep_ms(10)              # Ctrl+C unterbricht hier → KeyboardInterrupt
        try:
            conn, addr = srv.accept()
        except OSError:
            continue                   # Kein Client wartet, weiter
        try:
            _handle(conn)
        except Exception as e:
            print('Handler error:', e) # NIEMALS except:pass — Fehler müssen sichtbar sein
        finally:
            try: conn.close()
            except Exception: pass

def _handle(conn):
    conn.settimeout(5)
    data = conn.recv(4096)
    if not data:
        return
    line = data.split(b'\r\n')[0].decode('utf-8', 'ignore')
    parts = line.split(' ')
    if len(parts) < 2:
        return
    method, path = parts[0], parts[1]
    # Body parsen
    body = b''
    hdr_end = data.find(b'\r\n\r\n')
    if hdr_end >= 0:
        body = data[hdr_end + 4:]
    status, ctype, content = _route(method, path, body)
    header = 'HTTP/1.1 {}\r\nContent-Type: {}\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n'.format(status, ctype)
    conn.sendall(header.encode())
    conn.sendall(content.encode() if isinstance(content, str) else content)

def _route(method, path, body):
    if path == '/': path = '/index.html'
    if path == '/index.html':
        try:
            return '200 OK', 'text/html', open('/web/index.html').read()
        except OSError:
            return '404 Not Found', 'text/plain', 'Not Found'
    req = {}
    if body:
        try: req = ujson.loads(body.decode('utf-8'))
        except Exception: pass
    if path == '/api/state':
        cfg = get_config()
        return '200 OK', 'application/json', ujson.dumps({
            'status': 'ok',
            'num_pixels': _driver.num_pixels if _driver else 0,
            'wifi': get_wifi_status(),
            'system': get_system_info(),
            'config': {'pin': cfg['neopixel']['pin'],
                       'num_pixels': cfg['neopixel']['num_pixels'],
                       'brightness': cfg.get('brightness', 80)}
        })
    if path == '/api/effects':
        return '200 OK', 'application/json', ujson.dumps({'status': 'ok', 'effects': list_effects()})
    if path == '/api/effect/run' and method == 'POST':
        try:
            cls = get_effect(req.get('type'))
            cls.run(_driver, req.get('params', {}), req.get('duration_ms', 5000))
            return '200 OK', 'application/json', ujson.dumps({'status': 'ok'})
        except Exception as e:
            return '200 OK', 'application/json', ujson.dumps({'status': 'error', 'message': str(e)})
    return '404 Not Found', 'text/plain', 'Not Found'
```

## 7. main.py — vollständige Boot-Sequenz

```python
# main.py -- NeoPulse boot sequence
import time, network, machine

def boot():
    print('=' * 40)
    print('NeoPulse ESP32-S3 v1.0')
    print('=' * 40)
    from config import get_config
    cfg = get_config()
    _setup_wifi(cfg)
    from neopixel_driver import NeoPixelDriver
    driver = NeoPixelDriver(cfg['neopixel']['pin'], cfg['neopixel']['num_pixels'])
    driver.fill((0, 10, 0)); driver.write()  # dim grün = läuft
    print('NeoPixel ready:', driver.num_pixels, 'LEDs')
    from server import run_server
    try:
        run_server(driver)           # blockiert hier
    except KeyboardInterrupt:
        print('Server stopped -- REPL available')
        driver.fill((0, 0, 0)); driver.write()
    except Exception as e:
        print('Server error:', e)
        raise                        # NICHT machine.reset() — Fehler sichtbar lassen!

def _setup_wifi(cfg):
    wifi_cfg = cfg.get('wifi', {})
    ssid = wifi_cfg.get('ssid', '')
    pw   = wifi_cfg.get('password', '')
    # AP immer aktivieren als Fallback
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=wifi_cfg.get('ap_ssid', 'NeoPulse-ESP32'))
    print('AP:', ap.ifconfig()[0])
    # STA versuchen
    if ssid:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if not sta.isconnected():
            sta.connect(ssid, pw)
            for _ in range(20):
                if sta.isconnected(): break
                time.sleep_ms(500)
        if sta.isconnected():
            print('WiFi STA:', sta.ifconfig()[0])
        else:
            print('WiFi STA: failed, AP only')
```
