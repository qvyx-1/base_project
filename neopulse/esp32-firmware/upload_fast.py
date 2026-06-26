"""Upload firmware to ESP32-S3.

Strategy:
- boot.py wartet 5 Sekunden bevor IRQ aktiv wird.
- In diesen 5 Sekunden muessen alle Dateien hochgeladen sein.
- mpremote 'resume' verhindert soft-reset.
- Ctrl+C vor jedem Aufruf stoppt laufenden Server.
"""

import os
import time

import serial

FW = "/home/daniel/python-projects/base_project/neopulse/esp32-firmware"
PORT = "/dev/ttyACM0"


def _interrupt():
    """Ctrl+C senden: unterbricht laufenden Server."""
    try:
        s = serial.Serial(PORT, 115200, timeout=0.5)
        for _ in range(4):
            s.write(b"\x03")
            time.sleep(0.1)
        time.sleep(0.5)
        s.read(2000)
        s.close()
        time.sleep(0.3)
    except Exception as e:
        print("  interrupt error:", e)


def mp(cmd):
    """Einmalig Ctrl+C, dann mpremote mit 'resume'."""
    _interrupt()
    rc = os.system(f"mpremote connect {PORT} resume {cmd}")
    return rc == 0


def cp(local, remote):
    ok = mp(f'cp "{local}" :{remote}')
    if not ok:
        time.sleep(0.5)
        ok = mp(f'cp "{local}" :{remote}')
    return ok


# -- Schnell-Check: REPL erreichbar? ---------------------------------------
print("Interrupting ESP32...")
_interrupt()

print("Checking REPL (5s Window)...")
ok = mp("exec \"print('REPL OK')\"")
if not ok:
    print("WARN: REPL nicht sofort erreichbar.")
    print("  boot.py wartet 5 Sekunden. Upload wird trotzdem versucht...")
    time.sleep(1)  # Kurz warten bis boot.py die 5s-Wartezeit beendet hat

# -- Directories (resume: kein soft-reset) ----------------------------------
print("\n=== Directories ===")
mp("exec \"import os; [os.mkdir(d) for d in ['effects','web'] if d not in os.listdir('/')]\"")

# -- Core files (boot.py ZULETZT) ------------------------------------------
print("\n=== Core files ===")
for f in [
    "config.py",
    "neopixel_driver.py",
    "animation_engine.py",
    "server.py",
    "main.py",
    "boot.py",  # boot.py zuletzt: aktiviert Auto-Boot erst nach dem Upload
]:
    ok = cp(f"{FW}/{f}", f)
    if not ok:
        time.sleep(0.5)
        ok = cp(f"{FW}/{f}", f)
    print(f"  {f}: {'OK' if ok else 'FAIL'}")

# -- Effects ----------------------------------------------------------------
print("\n=== Effects ===")
for ef in [
    "__init__.py",
    "strobe.py",
    "fire.py",
    "rainbow.py",
    "breathing.py",
    "emergency_us.py",
    "emergency_de.py",
]:
    ok = cp(f"{FW}/effects/{ef}", f"effects/{ef}")
    print(f"  {ef}: {'OK' if ok else 'FAIL'}")

# -- Web --------------------------------------------------------------------
print("\n=== Web ===")
ok = cp(f"{FW}/web/index.html", "web/index.html")
print(f"  index.html: {'OK' if ok else 'FAIL'}")

# -- Config JSON ------------------------------------------------------------
print("\n=== Config ===")
mp(
    "exec \"import ujson; c={'wifi':{'ssid':'ANDROID_WIRELESS3','password':'GlugiJkeue89'},'neopixel':{'pin':21,'num_pixels':64},'brightness':80,'web':{'port':8080}}; open('/config.json','w').write(ujson.dumps(c)); print('config.json written')\""
)

# -- Verify -----------------------------------------------------------------
print("\n=== Verify ===")
mp(
    "exec \"import os; files=['boot.py','main.py','server.py','config.py','neopixel_driver.py','effects/__init__.py','web/index.html','/config.json']; [print(f, os.stat(f)[6], 'bytes') for f in files]\""
)

print("\n=== Soft-Reset -- Server startet automatisch ===")
_interrupt()
try:
    s = serial.Serial(PORT, 115200, timeout=0.5)
    s.write(b"\x04")  # Ctrl+D = soft reset
    time.sleep(15)  # WiFi-Verbindung abwarten
    out = s.read_all()
    print(out.decode("utf-8", errors="replace"))
    s.close()
except Exception as e:
    print("Reset error:", e)
    print("Manuell: ESP aus/einstecken oder Ctrl+D im REPL")

print("""
=== DONE ===
Web-Interface:  http://192.168.0.91:8080/
API:            http://192.168.0.91:8080/api/state
AP-Fallback:    http://192.168.4.1:8080/

Naechster Upload: python3 upload_fast.py (stoppt Server automatisch)
""")
