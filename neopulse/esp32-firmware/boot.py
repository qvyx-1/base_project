# boot.py -- Auto-Boot: CPU-Freq setzen, dann Server starten
# Ctrl+C im Server -> REPL verfuegbar
# Fehler -> Traceback anzeigen, KEIN machine.reset()
import time

import machine

machine.freq(240000000)

# USB-Enumeration abwarten: ohne Pause faellt USB-JTAG beim Start aus
# (Linux: "can't set config #1, error -32")
time.sleep(10)

try:
    import main

    main.boot()
except KeyboardInterrupt:
    print("Boot interrupted -- REPL available")
except Exception as e:
    import sys

    sys.print_exception(e)
    print("Boot error above -- REPL available (not resetting)")
