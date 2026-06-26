import time

import serial

FW = "/home/daniel/python-projects/base_project/neopulse/esp32-firmware"


def reset_and_get():
    s = serial.Serial("/dev/ttyACM0", 115200, timeout=0.2)
    s.setDTR(False)
    time.sleep(0.03)
    s.setRTS(True)
    time.sleep(0.03)
    s.setDTR(True)
    time.sleep(0.03)
    s.setRTS(False)
    time.sleep(0.3)
    time.sleep(0.5)
    out = s.read(1000)
    s.close()
    return out


def write_file(esp_path, local_path):
    with open(local_path) as f:
        content = f.read()
    s = serial.Serial("/dev/ttyACM0", 115200, timeout=0.2)
    s.setDTR(False)
    time.sleep(0.03)
    s.setRTS(True)
    time.sleep(0.03)
    s.setDTR(True)
    time.sleep(0.03)
    s.setRTS(False)
    time.sleep(0.3)
    time.sleep(0.3)
    s.read(500)

    s.write(b"f=open('" + esp_path.encode() + b"','w')\n")
    time.sleep(0.05)
    for line in content.split("\n"):
        el = line.replace("\\", "\\\\").replace("'", "\\'")
        cmd = "f.write('" + el + "\\n')\n"
        s.write(cmd.encode())
        time.sleep(0.005)
    s.write(b"f.close()\n")
    time.sleep(0.2)
    s.read(500)
    s.close()
    print("  " + esp_path + ": " + str(len(content)) + "B")


def send(cmds):
    s = serial.Serial("/dev/ttyACM0", 115200, timeout=0.2)
    s.setDTR(False)
    time.sleep(0.03)
    s.setRTS(True)
    time.sleep(0.03)
    s.setDTR(True)
    time.sleep(0.03)
    s.setRTS(False)
    time.sleep(0.3)
    time.sleep(0.3)
    s.read(500)
    for c in cmds:
        s.write((c + "\n").encode())
        time.sleep(0.05)
    time.sleep(0.3)
    out = s.read(2000)
    s.close()
    return out.decode("utf-8", errors="replace")


# 1. Clean
print("=== Clean old files ===")
send(
    ["import os"]
    + [
        f"try: os.remove('{f}')\nexcept: pass"
        for f in [
            "boot.py",
            "main.py",
            "server.py",
            "config.py",
            "neopixel_driver.py",
            "animation_engine.py",
        ]
    ]
)
print("  OK")

# 2. Main
print("=== Upload ===")
for f in [
    "boot.py",
    "config.py",
    "neopixel_driver.py",
    "animation_engine.py",
    "server.py",
    "main.py",
]:
    write_file("/" + f, FW + "/" + f)

# 3. Effects dir
print("=== Effects ===")
send(["import os", "try: os.mkdir('effects')\nexcept: pass"])
for ef in [
    "__init__.py",
    "strobe.py",
    "fire.py",
    "rainbow.py",
    "breathing.py",
    "emergency_us.py",
    "emergency_de.py",
]:
    write_file("/effects/" + ef, FW + "/effects/" + ef)

# 4. Web dir + index
print("=== Web ===")
send(
    [
        "import os",
        "try: os.mkdir('web')\nexcept: pass",
        "import json",
        "c={'wifi':{'ssid':'ANDROID_WIRELESS3','password':'GlugiJkeue89'},'neopixel':{'pin':21,'num_pixels':64},'brightness':80}",
        "with open('/config.json','w') as f: json.dump(c,f)",
    ]
)
write_file("/web/index.html", FW + "/web/index.html")

# 5. Verify
print("=== Verify ===")
out = send(
    [
        "import os",
        "for f in ['boot.py','main.py','server.py','config.py','neopixel_driver.py','effects/fire.py','web/index.html']:",
        "  try: s=os.stat(f); print(f+' '+str(s[6])+'B')",
        "  except: print(f+' MISSING')",
    ]
)
print(out[:500] if out else "(empty)")
print("\n=== DONE ===")
