# 🎨 NeoPulse — ESP32 NeoPixel Controller & Show Editor

Ein vollständiges System zur Steuerung von WS2812/NeoPixel LED-Streifen über einen ESP32-Mikrocontroller mit einer leistungsstarken Tkinter-Desktop-App und einem browserbasierten Emulator.

---

## 📋 Inhaltsverzeichnis

- [Features](#features)
- [Architektur](#architektur)
- [Projektstruktur](#projektstruktur)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [ESP32-Firmware](#esp32-firmware)
- [Desktop App](#desktop-app)
- [Emulator](#emulator)
- [API-Referenz](#api-referenz)
- [Effekte](#effekte)
- [Datenformate](#datenformate)
- [Fehlersuche](#fehlersuche)

---

## ✨ Features

### ESP32-Firmware (MicroPython)
- **WiFi STA + AP Modus** — Verbindung zum Router oder direkter Access Point
- **HTTP API Server** — RESTful API für alle Steuerungsfunktionen
- **NeoPixel-Treiber** — Bis zu 256 LEDs mit Zonen-Unterstützung
- **Keyframe-basierte Animation** — Lineare, Sinus-, Schritt- und Ease-In/Out-Interpolation
- **Loop-Modi** — Single, Endless, Ping-Pong
- **6 parametrierbare Effekte** — Strobe, Fire, Emergency (US/DE), Rainbow, Breathing
- **Flash-Speicher** — Shows werden auf dem ESP32 gespeichert
- **Webinterface** — Browser-basierte Steuerung direkt am Gerät

### Desktop App (Tkinter)
- **ESP32-Einrichtungswizard** — Schritt-für-Schritt Einrichtungsassistent
  - Automatische Gerätesuche (mDNS/HTTP-Scan)
  - MicroPython-Firmware flashen (esptool.py)
  - WiFi-Konfiguration
  - NeoPixel-Konfiguration (GPIO, LED-Anzahl, Helligkeit)
- **Show Editor** — Visuelle Keyframe-basierte Show-Erstellung
  - Timeline-Editor mit Drag & Drop
  - Pixel-Vorschau in Echtzeit
  - Szenen-Hierarchie-Baum
  - Interpolationsmodi und Loop-Einstellungen
- **Live Steuerung** — Echtzeit-Steuerung des verbundenen ESP32
  - Einzelne Pixel setzen
  - Helligkeitsregelung
  - Effekte starten
  - Shows abspielen
- **Projekt-Manager** — Verwalten mehrerer Show-Projekte
- **Emulator-Integration** — Direkter Start des Browser-Emulators

### Emulator (Browser)
- **Vollständiger NeoPixel-Simulator** — Simuliert ESP32-Verhalten im Browser
- **Keyframe-Editor** — Gleicher Editor wie in der Desktop App
- **6 Effekte** — Alle Effekte mit Echtzeit-Vorschau
- **Zonen-Management** — Aufteilung des LED-Streifens in Zonen
- **Show-Speicherung** — LocalStorage für Shows
- **FPS-Monitoring** — Performance-Metriken

---

## 🏗️ Architektur

```
┌──────────────────────────────────────────────────────────────┐
│                  NeoPulse Studio (Tkinter)                    │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────┐          │
│  │ Setup Wizard │ │ Show Editor │ │ Live Control │          │
│  │              │ │             │ │              │          │
│  │ • Gerät suchen│ │ • Timeline │ │ • Pixel setzen│          │
│  │ • Firmware   │ │ • Keyframes │ │ • Effekte    │          │
│  │ • WiFi Config│ │ • Szenen    │ │ • Shows absp. │          │
│  │ • NeoPixel   │ │ • Vorschau  │ │              │          │
│  └──────────────┘ └─────────────┘ └──────────────┘          │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           HTTP Client / mDNS Discovery              │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                          │ HTTP/JSON
┌──────────────────────────────────────────────────────────────┐
│              ESP32-S3 (MicroPython Firmware)                  │
│  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ WiFi/AP   │ │ HTTP API │ │ NeoPixel │ │ Animation    │  │
│  │ Manager   │ │ Router   │ │ Driver   │ │ Engine       │  │
│  └───────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Effekte: Strobe | Fire | Emergency | Rainbow      │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Webinterface (HTML/CSS/JS) + Flash-Speicher        │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              Browser Emulator (HTML5/JS)                      │
│  • Vollständiger NeoPixel-Simulator                         │
│  • Keyframe-Editor mit Timeline                             │
│  • Alle 6 Effekte mit Echtzeit-Vorschau                     │
│  • Zonen-Management                                         │
│  • LocalStorage für Shows                                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 Projektstruktur

```
neopulse/
├── README.md                          # Diese Datei
├── neopulse-design.md                 # Walt-Disney-Methode Entwurf
│
├── esp32-firmware/                    # MicroPython Firmware für ESP32
│   ├── boot.py                        # Boot-Sequenz, Default-Konfig
│   ├── main.py                        # Entry Point
│   ├── config.py                      # Konfigurationsmanagement
│   ├── server.py                      # HTTP Server + API Routing
│   ├── neopixel_driver.py             # NeoPixel-Treiber mit Zonen
│   ├── animation_engine.py            # Keyframe-Interpolation
│   │
│   ├── effects/                       # Effekt-Implementierungen
│   │   ├── __init__.py                # Effekt-Registry
│   │   ├── strobe.py                  # Strobe-Effekt
│   │   ├── fire.py                    # Feuer-Effekt
│   │   ├── emergency_us.py            # US Emergency (Rot/Blau)
│   │   ├── emergency_de.py            # DE Blaulicht
│   │   ├── rainbow.py                 # Regenbogen-Effekt
│   │   └── breathing.py               # Ein/Ausfaden
│   │
│   └── web/                           # Webinterface
│       ├── index.html                 # Hauptseite
│       ├── css/style.css              # Styles
│       └── js/
│           ├── app.js                 # Hauptanwendung
│           └── timeline.js            # Timeline-Editor
│
├── desktop/                           # Tkinter Desktop App
│   ├── main.py                        # Entry Point
│   ├── app.py                         # Hauptanwendung
│   │
│   ├── models/                        # Datenmodelle
│   │   ├── __init__.py
│   │   ├── scene.py                   # Szene (Keyframes, Interpolation)
│   │   ├── show.py                    # Show (Szenen-Sammlung)
│   │   ├── keyframe.py                # Einzelner Keyframe
│   │   └── effect.py                  # Effekt-Definitionen
│   │
│   ├── esp/                           # ESP32 Kommunikation
│   │   ├── __init__.py
│   │   ├── connection.py              # HTTP Client
│   │   ├── flasher.py                 # Firmware Flash (esptool)
│   │   └── mdns_discovery.py          # Gerätesuche
│   │
│   ├── widgets/                       # Tkinter Widgets
│   │   ├── __init__.py
│   │   ├── color_picker.py            # Farbauswahl
│   │   ├── pixel_preview.py           # LED-Vorschau
│   │   ├── timeline.py                # Timeline-Editor
│   │   └── scene_tree.py              # Szenen-Baum
│   │
│   └── windows/                       # UI Fenster
│       ├── __init__.py
│       ├── setup_wizard.py            # Einrichtungsassistent
│       ├── show_editor.py             # Show-Editor
│       ├── live_control.py            # Live-Steuerung
│       └── project_manager.py         # Projekt-Manager
│
└── emulator/                          # Browser-Emulator
    └── index.html                     # Vollständiger Simulator
```

---

## 📦 Installation

### Voraussetzungen

**System:**
- Linux (getestet auf Ubuntu/Debian), Windows 10/11
- Python 3.9+
- ESP32-S3 Entwicklungsboard (Typ-C)

**Python-Abhängigkeiten:**
```bash
pip install pyserial tkinter
pip install esptool    # Für Firmware-Flash
```

**ESP32-Treiber (Linux):**
```bash
# Serial Port Zugriff
sudo usermod -aG dialout $USER
# Neuanmeldung erforderlich!

# Optional: USB-Treiber für CP2102/CH340
sudo apt install python3-serial
```

### Emulator (keine Installation nötig)
Der Emulator ist eine reine HTML5-Anwendung und läuft in jedem modernen Browser.

---

## 🚀 Schnellstart

### 1. ESP32 einrichten

```bash
# MicroPython Firmware herunterladen
wget https://micropython.org/resources/firmware/ESP32_S3_GENERIC-20240221-v1.23.0.bin

# Firmware flashen (Port anpassen!)
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_S3_GENERIC-*.bin

# Oder über die Desktop App:
python -m neopulse.desktop.main
# → "ESP32 Einrichten" → Assistent folgen
```

### 2. Desktop App starten

```bash
cd /home/daniel/python-projects/base_project/neopulse
python -m desktop.main
```

### 3. Emulator öffnen

```bash
# Einfach im Browser öffnen:
file:///home/daniel/python-projects/base_project/neopulse/emulator/index.html
```

---

## 🔧 ESP32-Firmware

### Konfiguration

Die Konfiguration wird im Flash-Speicher (`/config.json`) gespeichert:

```python
{
    "wifi": {
        "mode": "sta",           # sta, ap, dual
        "ssid": "MeinWiFi",
        "password": "geheim123",
        "ap_ssid": "NeoPulse-ESP32",
        "ap_password": "neopulse123"
    },
    "neopixel": {
        "pin": 38,               # GPIO Pin für Daten
        "num_pixels": 64,        # Anzahl LEDs (max 256)
        "bpp": 3,                # 3=RGB, 4=RGBW
        "timing": 1              # 1=800kHz, 0=400kHz
    },
    "brightness": 80,            # Helligkeit 0-100%
    "zones": [
        {"id": 0, "start": 0, "end": 63, "name": "Zone 1"}
    ]
}
```

### Firmware-Upload

```bash
# Alle Dateien zum ESP32 übertragen (ampy oder webrepl_cli.py)
ampy --port /dev/ttyUSB0 put esp32-firmware/main.py
ampy --port /dev/ttyUSB0 put esp32-firmware/config.py
ampy --port /dev/ttyUSB0 mkdir /web
ampy --port /dev/ttyUSB0 put esp32-firmware/web/index.html /web/index.html
```

### GPIO-Pin Belegung (ESP32-S3)

| Funktion | Pin | Bemerkung |
|----------|-----|-----------|
| NeoPixel Data | GPIO 38 | Standard, konfigurierbar |
| UART TX | GPIO 21 | REPL |
| UART RX | GPIO 20 | REPL |
| USB CDC | Native | Für Flashing |

---

## 💻 Desktop App

### Hauptfunktionen

#### Setup Wizard
1. **Gerät finden** — Automatisch oder manuell IP eingeben
2. **Firmware flashen** — MicroPython auf ESP32 installieren
3. **WiFi konfigurieren** — SSID und Passwort setzen
4. **NeoPixel konfigurieren** — GPIO, LED-Anzahl, Helligkeit

#### Show Editor
1. **Szene erstellen** — Neue Szene mit Keyframes
2. **Keyframes setzen** — Farben zu bestimmten Zeiten definieren
3. **Interpolation wählen** — Linear, Sinus, Stufe, Ease-In/Out
4. **Loop-Modus** — Single, Endless, Ping-Pong
5. **Speichern** — Als JSON oder .npulse Projekt

#### Live Steuerung
1. **Verbinden** — IP des ESP32 eingeben
2. **Pixel setzen** — Einzelne LEDs steuern
3. **Effekte starten** — Strobe, Fire, Emergency...
4. **Shows abspielen** — Gespeicherte Shows starten

### Screenshots der UI

```
┌─────────────────────────────────────────────────────────┐
│  NeoPulse Studio                    [ESP: Verbunden]    │
├─────────────────────────────────────────────────────────┤
│  Datei  ESP32  Editor  Hilfe                            │
├──────────────┬──────────────────────────────────────────┤
│  Szenen      │  Timeline                               │
│  ┌────────┐  │  ┌──────────────────────────────────┐  │
│  │Szene 1 │  │  │  [▶] [⏹] [+ Keyframe] [💾]     │  │
│  │10.0s 3kf│  │  │                                  │  │
│  ├────────┤  │  │  ●────●────●────●                │  │
│  │Szene 2 │  │  │  t=0   t=3   t=6   t=9          │  │
│  │15.0s 5kf│  │  └──────────────────────────────────┘  │
│  └────────┘  │                                          │
│              │  Pixel-Vorschau                           │
│  Eigenschaften│  [●●●●●●●●●●●●●●●●]                  │
│  Name:        │                                          │
│  [_________]  │                                          │
│  Dauer: 10.0s │                                          │
│  Interp:      │                                          │
│  [Linear ▼]   │                                          │
│  Loop:        │                                          │
│  [Endless ▼]  │                                          │
└──────────────┴──────────────────────────────────────────┘
```

---

## 🎮 Emulator

Der Emulator simuliert ein ESP32-Device vollständig im Browser.

### Features
- **64-256 LEDs** konfigurierbar
- **Keyframe-Editor** mit Timeline
- **6 Effekte** mit Echtzeit-Vorschau
- **Zonen-Management** (bis zu 8 Zonen)
- **Show-Speicherung** im LocalStorage
- **Interpolationsmodi**: Linear, Sinus, Stufe, Ease-In/Out

### Verwendung
1. Browser öffnen: `file:///.../neopulse/emulator/index.html`
2. Szene erstellen (+ Szene)
3. Keyframes hinzufügen (+ Keyframe)
4. Farbe wählen (Farbauswahl rechts)
5. Abspielen (▶ Play)
6. Effekte testen (Effekte links auswählen)

---

## 📡 API-Referenz

### Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/state` | Aktueller Zustand |
| GET | `/api/shows` | Alle Shows |
| POST | `/api/shows` | Show speichern |
| GET | `/api/shows/:id` | Show laden |
| DELETE | `/api/shows/:id` | Show löschen |
| POST | `/api/play` | Show abspielen |
| POST | `/api/pixels/set` | Pixel setzen |
| POST | `/api/effect/run` | Effekt starten |
| POST | `/api/config/wifi` | WiFi konfigurieren |
| POST | `/api/restart/soft` | Soft-Reset |
| POST | `/api/restart/hard` | Hard-Reset |
| POST | `/api/config/brightness` | Helligkeit setzen |
| GET | `/api/effects` | Effekte auflisten |
| GET | `/api/info` | Systeminfo |

### Beispiel: Show speichern

```python
import requests
import json

show = {
    "id": "show_party_001",
    "name": "Party Mix",
    "scenes": [
        {
            "scene_id": "scene_intro",
            "transition": "fade",
            "duration": 1.0
        },
        {
            "scene_id": "scene_rainbow",
            "transition": "instant"
        }
    ],
    "loop_mode": "endless"
}

requests.post('http://192.168.1.100/api/shows', json=show)
```

### Beispiel: Effekt starten

```python
requests.post('http://192.168.1.100/api/effect/run', json={
    "type": "fire",
    "params": {"intensity": 0.8},
    "duration_ms": 10000
})
```

---

## 🎭 Effekte

### Strobe (Blitzlicht)
- **Parameter:** frequency (0.1-20 Hz), color (RGB)
- **Verwendung:** Diskothek, Alarm, Aufmerksamkeit

### Fire (Feuer)
- **Parameter:** intensity (0.1-1.0)
- **Verwendung:** Kamin-Atmosphäre, Halloween

### Emergency (US)
- **Parameter:** frequency (0.5-10 Hz), color_red, color_blue
- **Verwendung:** US-Feuerwehr/Medical Pattern

### Blaulicht (DE)
- **Parameter:** frequency (0.5-5 Hz), color_blue
- **Verwendung:** Deutsche Einsatzfahrzeuge

### Rainbow (Regenbogen)
- **Parameter:** speed (0.1-5.0)
- **Verwendung:** Party, dekorative Beleuchtung

### Breathing (Atmen)
- **Parameter:** frequency (0.1-3 Hz), color (RGB)
- **Verwendung:** Entspannung, Nachtlicht

---

## 📄 Datenformate

### Show JSON Format

```json
{
    "id": "show_12345678",
    "name": "Geburtstagsparty",
    "scenes": [
        {
            "scene_id": "scene_001",
            "transition": "fade",
            "duration": 2.0
        },
        {
            "scene_id": "scene_002",
            "transition": "instant"
        }
    ],
    "loop_mode": "endless"
}
```

### Scene JSON Format

```json
{
    "id": "scene_001",
    "name": "Intro",
    "keyframes": [
        {
            "time": 0.0,
            "colors": [[255, 0, 0], [255, 0, 0], ...]
        },
        {
            "time": 5.0,
            "colors": [[0, 0, 255], [0, 0, 255], ...]
        }
    ],
    "interpolation": "linear",
    "loop_mode": "single",
    "duration": 10.0,
    "brightness": 100
}
```

---

## 🔍 Fehlersuche

### ESP32 verbindet nicht
1. **USB-Kabel prüfen** — Datenkabel verwenden (nicht nur Ladekabel)
2. **Boot-Taste drücken** — Beim Flashen BOOT-Taste gedrückt halten
3. **Port prüfen** — `ls /dev/ttyUSB*` oder `dmesg | grep tty`
4. **Berechtigungen** — `sudo usermod -aG dialout $USER`

### esptool.py nicht gefunden
```bash
pip install esptool
```

### Serial Port Zugriff verweigert
```bash
sudo usermod -aG dialout $USER
# Neuanmeldung erforderlich!
```

### Emulator zeigt nichts an
- Browser-Kompatibilität: Chrome, Firefox, Edge, Safari
- Lokal öffnen mit `file://` Protocol
- Keine Server-notwendig

### Shows werden nicht gespeichert
- ESP32 Flash-Speicher prüfen: `dfu-util --list` oder Webinterface `/api/state`
- Genug Flash-Speicher verfügbar?

---

## 📝 Lizenz

MIT License

## 🤝 Beitragend

Fragen, Issues und Pull Requests willkommen!

## 🔗 Links

- [MicroPython Dokumentation](https://docs.micropython.org/en/latest/)
- [ESP32-S3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [WS2812B Spezifikation](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf)
- [esptool.py](https://github.com/espressif/esptool)
