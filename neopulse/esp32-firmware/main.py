# main.py -- NeoPulse boot sequence
# Wird von MicroPython automatisch ausgefuehrt NACH boot.py.
# Prueft /noboot:
#   - /noboot existiert -> nichts tun (REPL bleibt frei)
#   - /noboot existiert nicht -> boot() startet Server
#
# Manuell: import main; main.boot()
import os
import time

import network


def boot():
    print("=" * 40)
    print("NeoPulse ESP32-S3 v1.0")
    print("=" * 40)

    # 1. Config
    from config import get_config

    cfg = get_config()
    print("Config OK, pin:", cfg["neopixel"]["pin"])

    # 2. WiFi -- STA first, AP always as fallback
    _setup_wifi(cfg)

    # 3. NeoPixel driver
    from neopixel_driver import NeoPixelDriver

    driver = NeoPixelDriver(cfg["neopixel"]["pin"], cfg["neopixel"]["num_pixels"])
    driver.fill((0, 10, 0))
    driver.write()
    print("NeoPixel ready:", driver.num_pixels, "LEDs")

    # 4. HTTP server (blocking, Ctrl+C stops it)
    from server import run_server

    try:
        run_server(driver)
    except KeyboardInterrupt:
        print("Server stopped via Ctrl+C -- REPL available")
        driver.fill((0, 0, 0))
        driver.write()
    except Exception as e:
        print("Server error:", e)
        import sys

        sys.print_exception(e)


def _setup_wifi(cfg):
    wifi_cfg = cfg.get("wifi", {})
    ssid = wifi_cfg.get("ssid", "")
    pw = wifi_cfg.get("password", "")

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap_ssid = wifi_cfg.get("ap_ssid", "NeoPulse-ESP32")
    ap_pw = wifi_cfg.get("ap_password", "")
    if ap_pw:
        ap.config(essid=ap_ssid, password=ap_pw, authmode=3)
    else:
        ap.config(essid=ap_ssid)
    print("AP:", ap_ssid, "-->", ap.ifconfig()[0])

    if ssid:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if not sta.isconnected():
            print("WiFi STA connecting:", ssid)
            sta.connect(ssid, pw)
            for _ in range(20):
                if sta.isconnected():
                    break
                time.sleep_ms(500)
        if sta.isconnected():
            print("WiFi STA:", sta.ifconfig()[0])
        else:
            print("WiFi STA: failed, AP only")


# --- Module-Level Code: wird von MicroPython automatisch ausgefuehrt --------
_noboot = False
try:
    os.stat("/noboot")
    _noboot = True
except OSError:
    pass

if _noboot:
    print("NeoPulse v1.0 | /noboot vorhanden -> REPL-Modus")
    print("  Server: import main; main.boot()")
    print("  /noboot loeschen: import os; os.remove('/noboot'); machine.soft_reset()")
else:
    boot()
