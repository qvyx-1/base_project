#!/bin/bash
# NeoPulse ESP32 Firmware Upload Script
# Transfers all firmware files to ESP32 at /dev/ttyACM0

PORT="/dev/ttyACM0"
FIRMWARE_DIR="$(cd "$(dirname "$0")/esp32-firmware" && pwd)"

echo "=== NeoPulse ESP32 Firmware Upload ==="
echo "Port:  $PORT"
echo "Src:   $FIRMWARE_DIR"
echo ""

# Helper
upload() {
    local src="$1"
    local dest="$2"
    echo -n "  Upload $dest ... "
    mpremote connect "$PORT" cp "$src" ":$dest" 2>&1
    echo "OK"
}

# Create directories
echo "[1/5] Erstelle Verzeichnisse..."
mpremote connect "$PORT" exec "import os; dirs=['effects','web','web/static']
for d in dirs:
    try: os.mkdir(d)
    except: pass
print('dirs ok')" 2>&1

echo ""
echo "[2/5] Basis-Dateien..."
for f in boot.py config.py main.py server.py neopixel_driver.py animation_engine.py; do
    upload "$FIRMWARE_DIR/$f" "$f"
done

echo ""
echo "[3/5] Effects-Modul..."
for f in effects/__init__.py effects/strobe.py effects/fire.py effects/rainbow.py \
         effects/breathing.py effects/emergency_us.py effects/emergency_de.py; do
    upload "$FIRMWARE_DIR/$f" "$f"
done

echo ""
echo "[4/5] Webinterface..."
if [ -f "$FIRMWARE_DIR/web/index.html" ]; then
    upload "$FIRMWARE_DIR/web/index.html" "web/index.html"
fi

echo ""
echo "[5/5] Initialisiere config.json..."
mpremote connect "$PORT" exec "
import json
cfg = {
    'wifi': {'ssid':'','password':'','mode':'ap','ap_ssid':'NeoPulse-ESP32','ap_password':'neopulse123'},
    'neopixel': {'pin':21,'num_pixels':64,'bpp':3,'timing':1},
    'zones': [{'id':0,'start':0,'end':63,'name':'Zone 1'}],
    'web': {'port':80,'password':''},
    'brightness': 80
}
with open('/config.json','w') as f:
    json.dump(cfg, f)
print('config.json created with pin=21')
" 2>&1

echo ""
echo "=== Upload abgeschlossen ==="
echo ""
echo "ESP32 neustart..."
mpremote connect "$PORT" reset 2>&1

echo ""
echo "Warte 4 Sekunden auf Boot..."
sleep 4

echo ""
echo "=== ESP32 Boot-Output ==="
mpremote connect "$PORT" run /dev/stdin << 'PYEOF'
import time
time.sleep(1)
try:
    import config
    c = config.get_config()
    print("Config OK - Pin:", c['neopixel']['pin'])
    print("AP SSID:", c['wifi']['ap_ssid'])
except Exception as e:
    print("Config Fehler:", e)

try:
    import neopixel
    from machine import Pin
    np = neopixel.NeoPixel(Pin(21), 5)
    np[0] = (50, 0, 0)
    np[1] = (0, 50, 0)
    np[2] = (0, 0, 50)
    np[3] = (50, 50, 0)
    np[4] = (0, 50, 50)
    np.write()
    print("NeoPixel TEST: Pixel 0-4 leuchten!")
except Exception as e:
    print("NeoPixel Fehler:", e)
PYEOF
