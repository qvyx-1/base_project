# effects/breathing.py -- Breathing (fade in/out) effect
import math
import time


class BreathingEffect:
    name = "Breathing"

    @staticmethod
    def run(driver, params, duration_ms):
        freq = params.get("frequency", 0.5)
        color = params.get("color", (255, 255, 255))
        start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
            t = (time.ticks_ms() / 1000.0 * freq) % 2
            if t > 1:
                t = 2 - t
            brightness = int(255 * (math.sin(t * math.pi / 2) ** 2))
            b = (
                int(color[0] * brightness / 255),
                int(color[1] * brightness / 255),
                int(color[2] * brightness / 255),
            )
            driver.fill(b)
            driver.write()

    @staticmethod
    def get_default_params():
        return {"frequency": 0.5, "color": (255, 255, 255)}

    @staticmethod
    def get_param_schema():
        return [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.1,
                "max": 3.0,
                "default": 0.5,
                "label": "Frequency (Hz)",
            },
            {"name": "color", "type": "rgb", "default": [255, 255, 255], "label": "Color"},
        ]
