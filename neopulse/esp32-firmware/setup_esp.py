#!/usr/bin/env python3
"""NeoPulse ESP32 — sicheres Firmware-Setup ohne asyncio.
Der Server läuft in einer polling-loop die Ctrl+C-freundlich ist."""
import sys, os, time, json

PORT = "/dev/ttyACM0"
FW = os.path.dirname(os.path.abspath(__file__))

def serial_send(cmds, wait=0.02):
    """Sende Python-Befehle an ESP32 über raw serial."""
    import serial
    s = serial.Serial(PORT, 115200, timeout=0.2)
    # DTR Reset
    s.setDTR(False); time.sleep(0.03)
    s.setRTS(True); time.sleep(0.03)
    s.setDTR(True); time.sleep(0.03)
    s.setRTS(False); time.sleep(0.3)
    time.sleep(0.3)
    s.read(500)  # Clear boot output
    
    for cmd in cmds:
        s.write((cmd.replace("'", "'") + "\n").encode())
        time.sleep(wait)
    
    time.sleep(0.3)
    out = s.read(2000)
    s.close()
    return out.decode('utf-8', errors='replace')

def write_file(esp_path, local_path, chunk_size=20):
    """Schreibe eine lokale Datei auf den ESP32."""
    with open(local_path) as f:
        lines = f.read().split('\n')
    
    cmds = [f"f=open('{esp_path}','w')"]
    cmds += [f"f.write('{l.replace(chr(92),chr(92)+chr(92)).replace(\"'\",chr(92)+chr(39))}\\n')" for l in lines]
    cmds.append("f.close()")
    
    s = serial.Serial(PORT, 115200, timeout=0.2)
    s.setDTR(False); time.sleep(0.03)
    s.setRTS(True); time.sleep(0.03)
    s.setDTR(True); time.sleep(0.03)
    s.setRTS(False); time.sleep(0.3)
    time.sleep(0.3)
    s.read(500)
    
    for i, cmd in enumerate(cmds):
        s.write((cmd + "\n").encode())
        if i % chunk_size == 0:
            time.sleep(0.01)
    
    time.sleep(0.3)
    s.read(500)
    s.close()
    print(f"  {esp_path}: {len(lines)} lines")

print("=" * 50)
print("NeoPulse ESP32 Safe Setup")
print("=" * 50)

# Schritt 1: Alte boot.py/main.py löschen
print("\n[1/5] Alte Dateien löschen...")
serial_send([
    "import os",
    "for f in ['boot.py','main.py','server.py','config.py','neopixel_driver.py','animation_engine.py']:",
    "  try: os.remove(f)",
    "  except: pass",
])
print("  OK")

# Schritt 2: boot.py — NUR CPU-Frequenz, ruft NICHTS auf
print("\n[2/5] Sicheres boot.py schreiben...")
write_file("/boot.py", FW + "/boot.py")

# Schritt 3: config.py, neopixel_driver.py, animation_engine.py
print("\n[3/5] Module schreiben...")
for f in ["config.py", "neopixel_driver.py", "animation_engine.py"]:
    write_file("/" + f, FW + "/" + f)

# Schritt 4: Server — komplett ohne asyncio
print("\n[4/5] Server schreiben...")
write_file("/server.py", FW + "/server.py")

# Schritt 5: main.py — startet Server in Ctrl+C-freundlicher Schleife
print("\n[5/5] main.py schreiben...")
write_file("/main.py", FW + "/main.py")

# Schritt 6: Effects + Web + Config
print("\n[extra] Effects...")
serial_send(["import os", "os.mkdir('effects')"])
for f in os.listdir(FW + "/effects"):
    if f.endswith('.py'):
        write_file("/effects/" + f, FW + "/effects/" + f)

print("\n[extra] Web + Config...")
serial_send(["import os", "os.mkdir('web')"])
write_file("/web/index.html", FW + "/web/index.html")

# Config
serial_send([
    'import json',
    'cfg={"wifi":{"ssid":"ANDROID_WIRELESS3","password":"GlugiJkeue89"},"neopixel":{"pin":21,"num_pixels":64},"brightness":80}',
    'f=open("/config.json","w")',
    'json.dump(cfg,f)',
    'f.close()',
    'print("config.json written")',
])

print("\n=== ALL DONE ===")
print("ESP32 hat alle Dateien. Starte main.boot()...")
time.sleep(1)

# Test-Import
out = serial_send(["from config import get_config; c=get_config(); print('pin:',c['neopixel']['pin'],'pixels:',c['neopixel']['num_pixels'])"], wait=0.15)
print("Test:", out[:200])
