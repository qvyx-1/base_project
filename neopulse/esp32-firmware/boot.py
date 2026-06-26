# boot.py -- Nur GPIO 0 Polling + /noboot, dann ENDEN
# ====================================================
# WICHTIG: boot.py muss ENDEN. MicroPython startet dann main.py.
# main.py prueft /noboot und startet Server ODER laesst REPL frei.
import time

import machine

machine.freq(240000000)

print("NeoPulse v1.0 | BOOT fuer REPL-Modus (5s)...")

_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
_boot = False
for _ in range(50):
    time.sleep_ms(100)
    if not _pin.value():
        _boot = True
        break

if _boot:
    open("/noboot", "w").close()
    print("NeoPulse v1.0 | REPL-Modus (/noboot)")
    print("  Server: import main; main.boot()")
else:
    print("NeoPulse v1.0 | Server startet...")
    # KEIN import main.main.boot() HIER!
    # boot.py endet -> MicroPython startet main.py -> main.py bootet Server
