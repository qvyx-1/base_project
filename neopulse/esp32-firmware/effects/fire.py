# effects/fire.py -- Fire/flame effect
import math
import time


class FireEffect:
    name = "Fire"

    @staticmethod
    def run(driver, params, duration_ms):
        intensity = params.get("intensity", 1.0)
        start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
            t = time.ticks_ms() * 0.001
            colors = []
            for i in range(driver.num_pixels):
                # Fire color palette: black -> red -> orange -> yellow -> white
                r = min(255, int(255 * intensity * (0.7 + 0.3 * math.sin(i * 0.5 + t * 3))))
                g = min(255, int(180 * intensity * max(0, 0.4 + 0.6 * math.sin(i * 0.3 + t * 2.5))))
                b = 0
                colors.append((r, g, b))
            driver.set_all_colors(colors)
            driver.write()

    @staticmethod
    def get_default_params():
        return {"intensity": 1.0}

    @staticmethod
    def get_param_schema():
        return [
            {
                "name": "intensity",
                "type": "float",
                "min": 0.1,
                "max": 1.0,
                "default": 1.0,
                "label": "Intensity",
            },
        ]
