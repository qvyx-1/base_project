# main.py -- NeoPulse boot sequence
# Usage: import main; main.boot()
# Ctrl+C stops the server, REPL stays alive
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
    driver.fill((0, 10, 0))  # dim green = booting
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

    # Always enable AP as fallback
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap_ssid = wifi_cfg.get("ap_ssid", "NeoPulse-ESP32")
    ap_pw = wifi_cfg.get("ap_password", "")
    if ap_pw:
        ap.config(essid=ap_ssid, password=ap_pw, authmode=3)
    else:
        ap.config(essid=ap_ssid)
    print("AP:", ap_ssid, "-->", ap.ifconfig()[0])

    # Try STA
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
