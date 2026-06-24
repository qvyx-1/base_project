# 🎨 NeoPulse — ESP32 NeoPixel Controller
## Walt-Disney-Methode Entwurf

---

# 1. 🌈 Der Träumer (Visionär)

## Die Vision

Stell dir vor: Du hast eine LED-Streifen-Lichterkette, die du mit einem eleganten Desktop-Programm von deinem Linux-Rechner aus steuern kannst — wie eine professionelle Lichtsteuerung für Events, Wohnzimmer-Atmosphäre oder kreative Installationen.

**Die Traum-Vision:**

### Die ESP32-Firmware
- Ein vollwertiger **Webserver auf dem ESP32**, der ein interaktives Webinterface bereitstellt
- **NeoPixel-Treiber** mit Unterstützung für beliebig viele LEDs (speicherbedingt)
- **Keyframe-basiertes Animationssystem**: Du definierst Farben an bestimmten Zeitpunkten, dazwischen wird automatisch interpoliert
- **Szenen und Shows**: Mehrere Keyframes werden zu Szenen gruppiert, mehrere Szenen zu Shows
- **Parametrierbare Effekte** zwischen Keyframes:
  - 🚨 Emergency Vehicle (US): Rot/Blau abwechselnd
  - 🇩🇪 Blaulicht (DE): Blau blinkend
  - ⚡ Strobe: Blitzlicht mit konfigurierbarer Frequenz und Farbe
  - 🔥 Fire: Feuer-/Flammeneffekt mit parametrierbarer Intensität
  - 🌈 Rainbow: Farbverlauf über alle LEDs
  - 💫 Breathing: Sanftes Ein/Ausfaden
- **Speicherung** auf dem ESP32 Flash (JSON-basiert)
- **Live-Vorschau** im Webinterface mit Echtzeit-Farbpreview

### Die Tkinter-Desktop-App ("NeoPulse Studio")
- **ESP32-Einrichtungswizard**:
  - MicroPython-Firmware automatisch herunterladen und flashen
  - WiFi-SSID/Passwort konfigurieren
  - NeoPixel-Konfiguration (Anzahl LEDs, GPIO-Pin, Typ)
  - Debugging über WebREPL einrichten
  - ESP32 neu starten / soft-reset
- **Show-Editor**:
  - Visuelle Keyframe-Zeitleiste (wie in einem Videobearbeitungsprogramm)
  - Farbauswahl mit Color-Picker
  - Szenen-Management: Erstellen, umbenennen, löschen, duplizieren
  - Show-Assembly: Mehrere Szenen zu einer Show zusammenfassen
  - Effekte zwischen Keyframes zuweisen und parametrisieren
  - Timeline-Preview mit Echtzeit-Simulation
- **ESP32-Kommunikation**:
  - Automatische Erkennung des ESP32 im lokalen Netzwerk (mDNS/Bonjour)
  - Upload von Shows/Szenen per HTTP API
  - Live-Steuerung: Farben/Effekte in Echtzeit senden
  - Firmware-Update-Funktion direkt aus der App
- **Datei-Management**:
  - Shows als JSON-Datei exportieren/importieren
  - Projektdateien (.npulse) mit mehreren Shows
  - Vorlagen-Bibliothek für gängige Effekte

### Die "Wow"-Faktoren
- 🎭 **Effekt-Komposition**: Mehrere Effekte gleichzeitig (z.B. Fire + Rainbow-Mix)
- 📊 **Wellenformen**: Sägezahn, Sinus, Dreieck als Interpolationsmodus
- ⏱️ **Timing-Präzision**: Millisekunden-genaue Keyframe-Timing
- 🔄 **Loop-Modi**: Einzel-Loop, Endlos-Loop, Ping-Pong (Vor/Zurück)
- 📱 **Responsive Webinterface**: Auch vom Smartphone steuerbar
- 🔊 **Audio-Reaktivität** (optional): Mikrofon am ESP32 für musik-synchronisierte Effekte

---

# 2. 🛠️ Der Realist (Planer & Macher)

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────┐
│           NeoPulse Studio (Tkinter Desktop App)     │
│  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ │
│  │ ESP Setup │ │ Show Ed. │ │ Live Ctrl│ │Proj. │ │
│  │ Wizard    │ │ (Timeline│ │ (Realtime│ │Mgr   │ │
│  └───────────┘ └──────────┘ └──────────┘ └──────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         HTTP API Client / mDNS Discovery    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         │  HTTP/WebSocket
┌─────────────────────────────────────────────────────┐
│              ESP32 (MicroPython)                     │
│  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ │
│  │ WiFi/AP   │ │ HTTP API │ │ NeoPixel │ │Flash │ │
│  │ Manager   │ │ Router   │ │ Driver   │ │Store │ │
│  └───────────┘ └──────────┘ └──────────┘ └──────┘ │
│  ┌─────────────────────────────────────────────┐   │
│  │  Animation Engine (Keyframe Interpolation)  │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  Effect Engine (Strobe, Fire, Emergency...) │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Phase 1: ESP32 MicroPython Firmware

### 1.1 Projektstruktur auf dem ESP32

```
esp32-firmware/
├── main.py                  # Entry point, startet alles
├── config.py                # Konfigurationsmanagement (WiFi, GPIO, etc.)
├── storage.py               # Flash-Speicher für Shows/Szenen (json + custom vfs)
├── server.py                # HTTP-Server mit asyncio
├── neopixel_driver.py       # NeoPixel-Treiber Wrapper
├── animation_engine.py      # Keyframe-Interpolation
├── effect_engine.py         # Effekte (Strobe, Fire, Emergency, etc.)
├── effects/
│   ├── __init__.py
│   ├── strobe.py            # Strobe-Effekt
│   ├── fire.py              # Feuer-Effekt
│   ├── emergency_us.py      # US Emergency (Rot/Blau)
│   ├── emergency_de.py      # DE Blaulicht
│   ├── rainbow.py           # Regenbogen
│   └── breathing.py         # Ein/Ausfaden
├── web/
│   ├── index.html           # Webinterface
│   ├── css/style.css
│   ├── js/app.js            # Haupt-JS
│   ├── js/editor.js         # Show-Editor
│   ├── js/timeline.js       # Timeline-Komponente
│   └── js/colorpicker.js    # Farbauswahl
├── lib/
│   └── neopixel.py          # NeoPixel Modul (aus micropython-lib)
└── boot.py                  # Boot-Sequenz, WiFi-Verbindung
```

### 1.2 Wichtige MicroPython-Konzepte

**WiFi-Modus (hybrid):**
```python
import network

def setup_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    # AP als Fallback
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
```

**NeoPixel-Ansteuerung (built-in):**
```python
from machine import Pin
from neopixel import NeoPixel

pin = Pin(0, Pin.OUT)
np = NeoPixel(pin, 256)  # 256 LEDs
np[0] = (255, 0, 0)      # Rot
np.write()                 # Aktualisieren
```

**HTTP-Server mit asyncio:**
```python
import asyncio
import ujson

async def handle_client(reader, writer):
    # HTTP Request lesen
    # Routing basierend auf URL/Method
    # JSON Response zurückgeben
    data = ujson.dumps({"status": "ok", "pixels": current_colors})
    writer.write(f"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n{data}")
    await writer.drain()
```

**Flash-Speicher:**
```python
import os
# Schreiben
with open('/shows.json', 'w') as f:
    ujson.dump(shows, f)
# Lesen
with open('/shows.json', 'r') as f:
    shows = ujson.load(f)
```

### 1.3 Datenmodelle

```python
# Szene (Scene)
scene = {
    "id": "scene_001",
    "name": "Abendstimmung",
    "keyframes": [
        {
            "time": 0,           # Sekunden ab Szenenstart
            "colors": [(255,0,0), (0,255,0), ...],  # pro LED eine Farbe
            "interpolation": "linear"  # oder "sine", "step", "sawtooth"
        },
        {
            "time": 5.0,
            "colors": [(0,0,255), (255,255,0), ...],
            "interpolation": "linear"
        }
    ],
    "loop_mode": "endless",       # single, endless, pingpong
    "duration": 10.0              # Gesamtdauer in Sekunden
}

# Show (mehrere Szenen)
show = {
    "id": "show_001",
    "name": "Geburtstagsparty",
    "scenes": [
        {"scene_id": "scene_001", "transition": "fade", "duration": 1.0},
        {"scene_id": "scene_002", "transition": "instant"},
        {"scene_id": "scene_003", "transition": "dissolve", "duration": 2.0}
    ],
    "loop_mode": "endless"
}

# Effekt-Zwischen-Keyframe
effect = {
    "type": "strobe",            # oder "fire", "emergency_us", "emergency_de", "rainbow", "breathing"
    "params": {
        "frequency": 3.0,        # Hz
        "color": (255, 0, 0),
        "intensity": 1.0
    },
    "duration": 4.0              # Sekunden
}
```

### 1.4 Animation Engine

```python
import asyncio
import math

class AnimationEngine:
    def __init__(self, num_pixels):
        self.num_pixels = num_pixels
        self.current_scene = None
        self.start_time = 0
        self.running = False
    
    def interpolate_color(self, c1, c2, t):
        """Interpoliert zwischen zwei RGB-Farben"""
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
    
    def get_frame_colors(self, scene, elapsed_time):
        """Berechnet die aktuellen Farben für einen gegebenen Zeitpunkt"""
        kf = scene['keyframes']
        
        if elapsed_time <= kf[0]['time']:
            return kf[0]['colors']
        if elapsed_time >= kf[-1]['time']:
            return kf[-1]['colors']
        
        # Finde die beiden umgebenden Keyframes
        for i in range(len(kf) - 1):
            if kf[i]['time'] <= elapsed_time <= kf[i+1]['time']:
                t = (elapsed_time - kf[i]['time']) / (kf[i+1]['time'] - kf[i]['time'])
                
                # Interpolationsmodus
                if scene.get('interpolation') == 'sine':
                    t = math.sin(t * math.pi / 2)
                elif scene.get('interpolation') == 'step':
                    t = 1.0 if t > 0.5 else 0.0
                
                return [self.interpolate_color(kf[i]['colors'][j], kf[i+1]['colors'][j], t)
                        for j in range(self.num_pixels)]
    
    async def run(self, np_driver):
        """Hauptschleife der Animation"""
        self.running = True
        while self.running:
            if self.current_scene:
                elapsed = asyncio.get_event_loop().time() - self.start_time
                
                # Loop-Modus
                duration = self.current_scene.get('duration', 10.0)
                loop = self.current_scene.get('loop_mode', 'single')
                if loop == 'endless':
                    elapsed = elapsed % duration
                elif loop == 'pingpong':
                    cycle = (elapsed % (duration * 2))
                    if cycle > duration:
                        cycle = duration - (cycle - duration)
                    elapsed = cycle
                
                colors = self.get_frame_colors(self.current_scene, elapsed)
                np_driver.set_colors(colors)
                np_driver.write()
            
            await asyncio.sleep_ms(16)  # ~60 FPS
```

### 1.5 Effekt-Engine

```python
import math
import time

class EffectEngine:
    @staticmethod
    def strobe(np_driver, params, duration):
        """Strobe-Effekt"""
        freq = params.get('frequency', 3.0)
        color = params.get('color', (255, 255, 255))
        start = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
            phase = (time.ticks_ms() / 1000 * freq) % 2
            if phase < 1:
                np_driver.fill(color)
            else:
                np_driver.fill((0, 0, 0))
            np_driver.write()
    
    @staticmethod
    def fire(np_driver, params, duration):
        """Feuer-Effekt"""
        intensity = params.get('intensity', 1.0)
        start = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
            colors = []
            for i in range(np_driver.n):
                r = min(255, int(255 * intensity * (0.7 + 0.3 * math.sin(i * 0.5 + time.ticks_ms() * 0.01))))
                g = min(255, int(200 * intensity * max(0, 0.5 + 0.5 * math.sin(i * 0.3 + time.ticks_ms() * 0.015))))
                b = 0
                colors.append((r, g, b))
            np_driver.set_colors(colors)
            np_driver.write()
    
    @staticmethod
    def emergency_us(np_driver, params, duration):
        """US Emergency: Rot und Blau abwechselnd"""
        freq = params.get('frequency', 2.0)
        start = time.ticks_ms()
        red = params.get('color_red', (255, 0, 0))
        blue = params.get('color_blue', (0, 0, 255))
        
        while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
            phase = (time.ticks_ms() / 1000 * freq) % 2
            color = red if phase < 1 else blue
            np_driver.fill(color)
            np_driver.write()
    
    @staticmethod
    def emergency_de(np_driver, params, duration):
        """DE Blaulicht: Blau blinkend mit Sireneneffekt"""
        freq = params.get('frequency', 1.5)
        start = time.ticks_ms()
        blue = params.get('color_blue', (0, 0, 255))
        
        while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
            phase = (time.ticks_ms() / 1000 * freq) % 4
            if phase < 1:
                np_driver.fill(blue)  # An
            elif phase < 2:
                np_driver.fill((0, 0, 0))  # Aus
            elif phase < 3:
                # Schnelles Blinken
                if int(time.ticks_ms() / 100) % 2:
                    np_driver.fill(blue)
                else:
                    np_driver.fill((0, 0, 0))
            else:
                np_driver.fill((0, 0, 0))
            np_driver.write()
    
    @staticmethod
    def rainbow(np_driver, params, duration):
        """Regenbogen-Effekt über alle LEDs"""
        start = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
            colors = []
            for i in range(np_driver.n):
                hue = (i * 360 // np_driver.n + time.ticks_ms() * 0.1) % 360
                r, g, b = hsv_to_rgb(hue, 255, 255)
                colors.append((r, g, b))
            np_driver.set_colors(colors)
            np_driver.write()
    
    @staticmethod
    def breathing(np_driver, params, duration):
        """Sanftes Ein/Ausfaden"""
        freq = params.get('frequency', 0.5)
        color = params.get('color', (255, 255, 255))
        start = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
            t = (time.ticks_ms() / 1000 * freq) % 2
            if t > 1:
                t = 2 - t
            brightness = int(255 * (math.sin(t * math.pi / 2) ** 2))
            np_driver.fill((int(c * brightness / 255) for c in color))
            np_driver.write()
```

## Phase 2: Tkinter Desktop-App ("NeoPulse Studio")

### 2.1 Projektstruktur

```
neopulse-studio/
├── main.py                  # Entry point, Hauptfenster
├── app.py                   # Application Klasse
├── windows/
│   ├── __init__.py
│   ├── setup_wizard.py      # ESP32-Einrichtungswizard
│   ├── show_editor.py       # Show-Editor mit Timeline
│   ├── live_control.py      # Live-Steuerungsfenster
│   └── project_manager.py   # Projektdatei-Management
├── models/
│   ├── __init__.py
│   ├── scene.py             # Scene Datenklasse
│   ├── show.py              # Show Datenklasse
│   ├── keyframe.py          # Keyframe Datenklasse
│   └── effect.py            # Effekt Datenklasse
├── esp/
│   ├── __init__.py
│   ├── connection.py        # ESP32 Verbindung (HTTP/mDNS)
│   ├── flasher.py           # MicroPython flashen (esptool)
│   ├── webrepl.py           # WebREPL Client
│   └── mdns_discovery.py    # mDNS/Bonjour Discovery
├── widgets/
│   ├── __init__.py
│   ├── color_picker.py      # Farbauswahl-Komponente
│   ├── timeline.py          # Timeline-Komponente
│   ├── pixel_preview.py     # LED-Vorschau-Komponente
│   └── scene_tree.py        # Szenen-Hierarchie-Baum
├── effects/
│   ├── __init__.py
│   ├── strobe_config.py     # Strobe Konfig-Widget
│   ├── fire_config.py       # Fire Konfig-Widget
│   └── emergency_config.py  # Emergency Konfig-Widget
├── templates/               # Vorlagen
│   ├── birthday.npulse
│   ├── christmas.npulse
│   └── party.npulse
├── assets/
│   └── icons/
└── config.json              # App-Einstellungen
```

### 2.2 ESP32-Einrichtungswizard (Setup Wizard)

**Schritt-für-Schritt-Flow:**

```python
# esp/flasher.py
import subprocess
import serial

class ESPFlasher:
    MICROPYTHON_FIRMWARE_URL = "https://micropython.org/resources/firmware/"
    
    def get_available_firmwares(self):
        """Listet verfügbare MicroPython Firmware für ESP32"""
        return [
            {"name": "ESP32 GENERIC", "url": "...", "chip": "esp32"},
            {"name": "ESP32-S2 GENERIC", "url": "...", "chip": "esp32-s2"},
            {"name": "ESP32-S3 GENERIC", "url": "...", "chip": "esp32-s3"},
            {"name": "ESP32-C3 GENERIC", "url": "...", "chip": "esp32-c3"},
        ]
    
    def flash_firmware(self, port, firmware_url=None, firmware_path=None):
        """Flasht MicroPython auf den ESP32"""
        cmd = [
            'esptool.py', '--port', port, '--baud', '460800',
            'write_flash', '-z', '0x1000', firmware_path or firmware_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def erase_flash(self, port):
        """Löscht den gesamten Flash"""
        cmd = ['esptool.py', '--port', port, 'erase_flash']
        return subprocess.run(cmd, capture_output=True).returncode == 0
    
    def enter_bootloader(self, port):
        """Versetzt ESP32 in Bootloader-Modus"""
        import serial
        with serial.Serial(port, 115200) as ser:
            ser.setDTR(False)
            import time; time.sleep(0.1)
            ser.setDTR(True)
            ser.setRTS(False)
    
    def detect_port(self):
        """Erkennt verfügbare ESP32 Ports"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.grep('ESP32')
        return [(p.device, p.description) for p in ports]
```

**WiFi-Konfiguration:**
```python
# esp/connection.py
class ESPConnection:
    def __init__(self, ip_address=None):
        self.ip = ip_address
        self.base_url = f"http://{ip_address}" if ip_address else None
    
    def configure_wifi(self, ssid, password):
        """Konfiguriert WiFi am ESP32"""
        import requests
        resp = requests.post(f"{self.base_url}/api/config/wifi", json={
            "ssid": ssid,
            "password": password
        })
        return resp.json()
    
    def restart(self, soft=True):
        """Startet ESP32 neu"""
        import requests
        endpoint = "/api/restart/soft" if soft else "/api/restart/hard"
        return requests.post(f"{self.base_url}{endpoint}")
    
    def upload_show(self, show_data):
        """Lädt eine Show zum ESP32"""
        import requests
        resp = requests.post(f"{self.base_url}/api/shows", json=show_data)
        return resp.json()
    
    def get_current_state(self):
        """Ermittelt aktuellen Zustand des ESP32"""
        import requests
        return requests.get(f"{self.base_url}/api/state").json()
```

### 2.3 Show-Editor (Timeline-basiert)

**Hauptkomponenten:**

```python
# windows/show_editor.py
import tkinter as tk
from tkinter import ttk, colorchooser

class ShowEditorWindow:
    def __init__(self, parent, show=None):
        self.parent = parent
        self.show = show or Show()
        
        # Hauptlayout
        self.window = tk.Toplevel(parent)
        self.window.title(f"Show Editor — {self.show.name}")
        
        # Oben: Toolbar
        self.toolbar = ttk.Frame(self.window)
        self.toolbar.pack(fill=tk.X)
        # [Neue Szene] [Duplizieren] [Löschen] [Effekt hinzufügen] [Preview] [Upload]
        
        # Mitte links: Szenen-Hierarchie
        self.scene_tree = SceneTreeWidget(self.window)
        self.scene_tree.pack(side=tk.LEFT, fill=tk.Y)
        
        # Mitte: Timeline
        self.timeline = TimelineWidget(self.window, show=self.show)
        self.timeline.pack(fill=tk.BOTH, expand=True)
        
        # Unten: Pixel-Vorschau
        self.pixel_preview = PixelPreviewWidget(self.window)
        self.pixel_preview.pack(fill=tk.X)
        
        # Rechts: Eigenschaften-Panel
        self.properties = PropertiesPanel(self.window)
        self.properties.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_keyframe(self, scene_id, time, colors):
        """Fügt einen Keyframe hinzu"""
        kf = Keyframe(time=time, colors=colors)
        self.show.add_keyframe(scene_id, kf)
        self.timeline.refresh()
    
    def set_effect_between(self, scene_id, start_time, end_time, effect_type, params):
        """Weist einen Effekt zwischen zwei Zeitpunkten zu"""
        effect = Effect(type=effect_type, params=params)
        self.show.set_effect(scene_id, start_time, end_time, effect)
    
    def preview(self):
        """Simuliert die Show lokal"""
        self.timeline.start_preview()
    
    def upload_to_esp(self, esp_ip):
        """Lädt die Show zum ESP32 hoch"""
        conn = ESPConnection(esp_ip)
        return conn.upload_show(self.show.to_dict())
```

### 2.4 Farbauswahl-Komponente

```python
# widgets/color_picker.py
import tkinter as tk
from tkinter import ttk, colorchooser

class ColorPickerWidget(ttk.Frame):
    def __init__(self, parent, initial_color=(255, 0, 0), on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.current_color = initial_color
        
        # Farbfeld
        self.swatch = tk.Label(self, bg=self.rgb_to_hex(initial_color), width=4)
        self.swatch.pack(side=tk.LEFT)
        self.swatch.bind('<Button-1>', lambda e: self.choose_color())
        
        # RGB-Slider
        for i, label in enumerate(['R', 'G', 'B']):
            slider = ttk.Scale(self, from_=0, to=255, orient=tk.HORIZONTAL,
                             command=lambda v, idx=i: self.update_rgb(idx))
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def choose_color(self):
        color = colorchooser.askcolor(color=self.rgb_to_hex(self.current_color))
        if color[1]:
            self.set_color(tuple(int(c) for c in color[0]))
    
    def set_color(self, rgb):
        self.current_color = rgb
        self.swatch.config(bg=self.rgb_to_hex(rgb))
        if self.on_change:
            self.on_change(rgb)
```

### 2.5 Timeline-Komponente

```python
# widgets/timeline.py
import tkinter as tk

class TimelineWidget(tk.Canvas):
    def __init__(self, parent, show, width=800, height=200):
        super().__init__(parent, width=width, height=height, bg='#1a1a2e')
        self.show = show
        self.zoom = 50  # Pixel pro Sekunde
        self.offset_x = 50
        
        self.draw_time_ruler()
        self.draw_scenes()
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
    
    def draw_time_ruler(self):
        """Zeichnet die Zeitachse"""
        for t in range(0, int(self.show.duration) + 1):
            x = self.offset_x + t * self.zoom
            self.create_line(x, 0, x, 20, fill='#444')
            self.create_text(x, 25, text=f"{t}s", fill='#888', font=('Arial', 8))
    
    def draw_scenes(self):
        """Zeichnet Szenen als Blöcke auf der Timeline"""
        y = 40
        for scene in self.show.scenes:
            x = self.offset_x + scene.start_time * self.zoom
            w = scene.duration * self.zoom
            color = self.scene_to_color(scene)
            self.create_rectangle(x, y, x + w, y + 30, fill=color, outline='white')
            self.create_text(x + w/2, y + 15, text=scene.name, fill='white', font=('Arial', 9))
    
    def draw_keyframes(self):
        """Zeichnet Keyframe-Marker"""
        for kf in self.show.keyframes:
            x = self.offset_x + kf.time * self.zoom
            # Diamant-Form als Marker
            s = 6
            self.create_polygon(
                x, y - s, x + s, y, x, y + s, x - s, y,
                fill='yellow', outline='orange'
            )
    
    def start_preview(self):
        """Startet die Timeline-Preview"""
        self.preview_running = True
        self._animate()
    
    def _animate(self):
        if not getattr(self, 'preview_running', False):
            return
        # Simuliere Farbwerte basierend auf aktueller Position
        pass
```

### 2.6 Pixel-Vorschau-Komponente

```python
# widgets/pixel_preview.py
import tkinter as tk

class PixelPreviewWidget(tk.Frame):
    def __init__(self, parent, num_pixels=64):
        super().__init__(parent)
        self.num_pixels = num_pixels
        self.pixels = []
        self.canvas = tk.Canvas(self, width=num_pixels * 12, height=30, bg='#0a0a0a')
        self.canvas.pack(pady=5)
        
        for i in range(num_pixels):
            x = i * 12 + 2
            rect = self.canvas.create_rectangle(x, 5, x + 8, 20, fill='#000', outline='#333')
            self.pixels.append(rect)
    
    def update_colors(self, colors):
        """Aktualisiert die Vorschau mit neuen Farben"""
        for i, rect in enumerate(self.pixels):
            if i < len(colors):
                r, g, b = colors[i]
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                self.canvas.itemconfig(rect, fill=hex_color)
```

## Phase 3: Datenfluss & API-Design

### 3.1 ESP32 HTTP API Endpunkte

| Methode | Pfad | Beschreibung | Request Body | Response |
|---------|------|-------------|--------------|----------|
| GET | `/api/state` | Aktueller Zustand | — | `{pixels, scene, effect, wifi}` |
| GET | `/api/shows` | Alle gespeicherten Shows | — | `[show1, show2, ...]` |
| POST | `/api/shows` | Neue Show speichern | `show` JSON | `{id, status}` |
| GET | `/api/shows/:id` | Show laden | — | `show` JSON |
| DELETE | `/api/shows/:id` | Show löschen | — | `{status}` |
| POST | `/api/play` | Show abspielen | `{"show_id": "..."}` | `{status}` |
| POST | `/api/pixels/set` | Einzelne Pixel setzen | `{"pixels": [...]}` | `{status}` |
| POST | `/api/effect/run` | Effekt starten | `{"type": "...", "params": {...}}` | `{status}` |
| POST | `/api/config/wifi` | WiFi konfigurieren | `{"ssid": "...", "password": "..."}` | `{status}` |
| POST | `/api/restart/soft` | Soft-Reset | — | `{status}` |
| POST | `/api/restart/hard` | Hard-Reset | — | `{status}` |
| GET | `/api/info` | ESP32 Info | — | `{chip, firmware, flash, uptime}` |

### 3.2 Beispiel: Show-Upload von Tkinter zu ESP32

```python
# In der Tkinter App:
show_data = {
    "id": "show_001",
    "name": "Party Mix",
    "scenes": [
        {
            "id": "scene_001",
            "name": "Intro",
            "keyframes": [
                {"time": 0, "colors": [(0,0,0)] * 64},
                {"time": 2.0, "colors": self.generate_gradient(64, (255,0,0), (0,0,255))},
                {"time": 5.0, "colors": [(255,255,255)] * 64}
            ],
            "interpolation": "linear",
            "loop_mode": "single",
            "duration": 5.0
        }
    ],
    "loop_mode": "endless"
}

# Upload zum ESP32
conn = ESPConnection("192.168.1.100")
result = conn.upload_show(show_data)
```

---

# 3. 🔍 Der Kritiker (Qualitätssicherer)

## Fallstricke, Risiken und Schwachstellen

### 3.1 ESP32-Firmware — Speicherprobleme ⚠️ KRITISCH

**Problem:** Der ESP32 hat begrenzten RAM (~520 KB internal SRAM) und Flash (~4 MB). MicroPython hat eine kleine Heap-Größe.

**Konsequenzen:**
- Ein 256-LED-Streifen mit Full-Color pro Pixel = 256 × 3 = 768 Bytes nur für die Daten — das wird eng!
- Mehrere Shows im Speicher? Unmöglich bei komplexen Shows.
- JSON-Parsing kann viel RAM verbrauchen.

**Gegenmaßnahmen:**
1. **Chunked Übertragung**: Shows nicht als ganzes JSON laden, sondern pixelweise/streaming
2. **Komprimierung**: Zeilenkompression für Show-Daten (z.B. RLE für wiederholte Farben)
3. **Begrenzte LED-Anzahl**: Max 128-256 LEDs als Hard-Limit in der UI anzeigen
4. **Scene-on-Demand**: Nur die aktuelle Szene im RAM halten, vorherige verwerfen
5. **Speicher-Monitoring**: `gc.collect()` und `gc.mem_free()` regelmäßig prüfen

### 3.2 Echtzeit-Performance ⚠️ HOCH

**Problem:** MicroPython ist langsamer als CPython. NeoPixel-Timing ist timing-kritisch (800kHz).

**Konsequenzen:**
- Interpolation bei vielen LEDs + komplexen Effekten kann ruckeln
- HTTP-Server + NeoPixel-Aktualisierung konkurrieren um CPU-Zeit
- asyncio Preemption kann zu Timing-Problemen führen

**Gegenmaßnahmen:**
1. **RMT-Channel nutzen**: ESP32 hat RMT (Remote Control) Peripheral für präzise NeoPixel-Timing — das entlastet die CPU!
2. **Effekte in C/ESP-IDF**: Kritische Pfade als ESP-IDF Component schreiben
3. **FPS-Limitierung**: Nicht bei 60 FPS rendern, sondern bei ~30-50 FPS (16-33ms Intervall)
4. **Pixel-Batching**: Alle Pixel auf einmal senden, nicht einzeln

### 3.3 WiFi-Stabilität ⚠️ MITTEL

**Problem:** WiFi kann instabil sein, Verbindungsabbrüche sind wahrscheinlich.

**Konsequenzen:**
- Tkinter App verliert Verbindung zum ESP32
- Show-Upload bricht ab → korrupte Daten
- Live-Steuerung ruckelt

**Gegenmaßnahmen:**
1. **AP-Mode Fallback**: Wenn WiFi-Verbindung fehlt, startet ESP32 als Access Point
2. **Retry-Logik**: Automatische Wiederconnect bei Abbruch
3. **Chunked Uploads mit Checksummen**: Bei Unterbrechung kann von der letzten intakten Chunk weitergemacht werden
4. **Heartbeat-Mechanismus**: Regelmäßige Ping-Nachrichten zur Verbindungsgesundheitsprüfung

### 3.4 Tkinter App — Cross-Platform ⚠️ MITTEL

**Problem:** Tkinter läuft auf Linux, aber die esptool-Kommunikation mit dem ESP32 benötigt Serial-Port-Zugriff.

**Konsequenzen:**
- Serial-Port-Berechtigungen unter Linux (`dialout` Gruppe)
- mDNS Discovery funktioniert nicht auf allen Systemen gleich
- USB-Treiber für ESP32 müssen installiert sein

**Gegenmaßnahmen:**
1. **Setup-Anleitung**: Explizite Anleitung für `sudo usermod -aG dialout $USER`
2. **Manuelle Port-Eingabe**: Als Fallback wenn automatische Erkennung fehlschlägt
3. **Web-basierte Alternative**: Falls Desktop-App Probleme macht, WebREPL als Fallback

### 3.5 Datenintegrität ⚠️ MITTEL

**Problem:** Flash-Speicher hat begrenzte Write-Cycles (~100.000).

**Konsequenzen:**
- Häufiges Speichern von Shows kann Flash verschleißen
- Stromausfall während des Schreibens → korrupte Daten

**Gegenmaßnahmen:**
1. **Write-Aware Storage**: Änderungen nur bei explizitem "Speichern"-Klick
2. **Backup/Restore**: Automatische Backup-Datei anlegen vor jedem Write
3. **Versionierung**: Zwei Kopien der Show-Daten (A/B Partitioning)

### 3.6 Webinterface auf ESP32 ⚠️ MITTEL

**Problem:** Das Webinterface muss extrem leichtgewichtig sein.

**Konsequenzen:**
- Kein JavaScript-Frameworks (React, Vue) — zu groß
- CSS muss inline oder minimal sein
- HTML muss so klein wie möglich sein

**Gegenmaßnahmen:**
1. **Minimalistisches HTML**: Nur essentielles Markup, keine externen Dependencies
2. **Inline CSS/JS**: Alles in einer HTML-Datei für weniger HTTP-Overhead
3. **WebSocket statt Polling**: Für Live-Updates effizienter als HTTP-Polling
4. **Canvas-basierte Vorschau**: Statt DOM-Manipulation mit hunderten divs

### 3.7 Effekte — Design ⚠️ NIEDRIG

**Problem:** Zu viele Effekte machen die UI unübersichtlich.

**Gegenmaßnahmen:**
1. **Kern-Effekte zuerst**: Strobe, Fire, Emergency (US/DE), Rainbow, Breathing
2. **Erweiterbar**: Plugin-Architektur für neue Effekte
3. **Misch-Modus**: Effekte kombinierbar mit Gewichtung

---

# 🎯 Fazit / Nächste Schritte

## Priorisierte Implementierungs-Reihenfolge

### Sprint 1: ESP32 Grundgerüst (1-2 Tage)
1. [ ] ESP32 WiFi-Verbindung (STA + AP Fallback)
2. [ ] NeoPixel-Basis-Treiber mit RMT-Channel
3. [ ] HTTP-Server mit grundlegenden API-Endpunkten
4. [ ] Pixel setzen/getzen über API

### Sprint 2: Animation & Effekte (2-3 Tage)
5. [ ] Keyframe-Engine mit linearer Interpolation
6. [ ] Loop-Modi (single, endless, pingpong)
7. [ ] Effekt-Engine: Strobe, Fire, Emergency US/DE
8. [ ] Flash-Speicher für Shows

### Sprint 3: Webinterface (2 Tage)
9. [ ] Leichtgewichtiges HTML/CSS/JS Interface
10. [ ] Keyframe-Editor im Browser
11. [ ] Farbauswahl und Timeline
12. [ ] Show-Upload und -Abspielung

### Sprint 4: Tkinter Desktop App (3-4 Tage)
13. [ ] ESP32-Einrichtungswizard (Flash, WiFi, Konfig)
14. [ ] Show-Editor mit Timeline
15. [ ] Farbauswahl und Pixel-Vorschau
16. [ ] HTTP-Client für ESP32-Kommunikation

### Sprint 5: Integration & Verfeinerung (2 Tage)
17. [ ] mDNS Discovery
18. [ ] Live-Steuerung in Echtzeit
19. [ ] Show-Export/Import als JSON
20. [ ] Projektdatei (.npulse) Format

## Technische Empfehlungen

1. **ESP32 Variante**: ESP32-S3 empfohlen (mehr RAM, USB-C native) oder klassischer ESP32-DevKit
2. **NeoPixel-Typ**: WS2812B (am weitesten verbreitet, beste MicroPython-Unterstützung)
3. **LED-Anzahl**: Start mit 32-64 LEDs als MVP, skalierbar bis ~256
4. **esptool.py**: `pip install esptool` für den Flasher in der Tkinter App
5. **mDNS**: `avahi-daemon` unter Linux für Discovery

## Offene Fragen (zu klären)

1. Wie viele LEDs maximal? (bestimmt RAM-Anforderungen)
2. Welcher ESP32-Chip? (ESP32, ESP32-S2, S3, C3?)
3. Einzelner Streifen oder mehrere unabhängige Zonen?
4. Braucht es Power-Injection bei >60 LEDs?
5. Soll die Tkinter App auch Windows/macOS unterstützen?
