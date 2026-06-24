# boot.py -- NeoPulse autostart on reset
import machine
machine.freq(240000000)

# Start main system
try:
    import main
    main.boot()
except Exception as e:
    print("Boot error:", e)
    print("REPL available")
