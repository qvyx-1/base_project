# effects/strobe.py -- Strobe light effect
import time


class StrobeEffect:
    name = "Strobe"

    @staticmethod
    def run(driver, params, duration_ms):
        freq = params.get("frequency", 3.0)
        color = params.get("color", (255, 255, 255))
        start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
            phase = (time.ticks_ms() / 1000.0 * freq) % 2
            if phase < 1:
                driver.fill(color)
            else:
                driver.fill((0, 0, 0))
            driver.write()

    @staticmethod
    def get_default_params():
        return {"frequency": 3.0, "color": (255, 255, 255)}

    @staticmethod
    def get_param_schema():
        return [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.1,
                "max": 20.0,
                "default": 3.0,
                "label": "Frequency (Hz)",
            },
            {"name": "color", "type": "rgb", "default": [255, 255, 255], "label": "Color"},
        ]
