# main.py -- Entry point for NeoPulse ESP32 firmware
# Safe boot: starts WiFi, config, and HTTP server
# Falls back gracefully if anything fails - NEVER blocks REPL permanently

import time
import network
import machine

def boot():
    """Initialize NeoPulse system. Returns when WiFi+Server are ready."""
    try:
        print("=" * 40)
        print("NeoPulse ESP32-S3 v1.0")
        print("=" * 40)

        # 1. Config laden
        from config import get_config
        cfg = get_config()
        wifi_cfg = cfg['wifi']
        print("Config loaded, pin:", cfg['neopixel']['pin'])

        # 2. WiFi STA (Client) - nicht blockierend
        sta = network.WLAN(network.STA_IF)
        sta.active(True)

        ssid = wifi_cfg.get('ssid', '')
        password = wifi_cfg.get('password', '')

        if ssid and password:
            print("Connecting to:", ssid)
            sta.connect(ssid, password)
            for i in range(30):
                if sta.isconnected():
                    break
                time.sleep_ms(500)
            if sta.isconnected():
                print("STA mode:", sta.ifconfig()[0])
            else:
                print("STA failed, using AP")
                sta.active(False)
        else:
            print("No WiFi credentials, starting AP...")
            sta.active(False)

        # 3. AP Fallback falls STA nicht verbunden
        ap = network.WLAN(network.AP_IF)
        if not sta.isconnected():
            ap.active(True)
            ap.config(essid=wifi_cfg.get('ap_ssid', 'NeoPulse-ESP32'))
            pw = wifi_cfg.get('ap_password', 'neopulse123')
            if pw: ap.config(password=pw)
            print("AP mode:", wifi_cfg.get('ap_ssid', 'NeoPulse-ESP32'), "IP:", ap.ifconfig()[0])

        # 4. NeoPixel und Server-Initialisierung
        from server import init_global_state
        init_global_state()
        print("NeoPixel + Server initialized")

        # 5. Server starten
        import asyncio
        from server import _run_server

        loop = asyncio.get_event_loop()
        loop.create_task(_run_server(8080))
        print("\nServer on port 8080")

        # Zusammenfassung
        sta_ip = sta.ifconfig()[0] if sta.isconnected() else "-"
        ap_ip = ap.ifconfig()[0] if ap.active() else "-"
        print("\n=== NEOBPULSE READY ===")
        print("STA IP:", sta_ip)
        print("AP IP: ", ap_ip)
        print("WebUI:", "http://" + (sta_ip if sta.isconnected() else ap_ip) + ":8080")
        print("=" * 40)

        # Loop starten (blockiert, aber das ist gewollt)
        loop.run_forever()

    except Exception as e:
        print("\nXXX Boot error:", e, "XXX")
        print("REPL fallback - system still usable")
        # Driver global halten für manuelle Nutzung
