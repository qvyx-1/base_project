# effects/emergency_us.py -- US Emergency vehicle pattern (Red/Blue alternating)
import time


class EmergencyUSEffect:
    name = "Emergency (US)"

    @staticmethod
    def run(driver, params, duration_ms):
        freq = params.get("frequency", 2.0)
        color_red = params.get("color_red", (255, 0, 0))
        color_blue = params.get("color_blue", (0, 0, 255))
        start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
            phase = (time.ticks_ms() / 1000.0 * freq) % 2
            color = color_red if phase < 1 else color_blue
            driver.fill(color)
            driver.write()

    @staticmethod
    def get_default_params():
        return {"frequency": 2.0, "color_red": (255, 0, 0), "color_blue": (0, 0, 255)}

    @staticmethod
    def get_param_schema():
        return [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.5,
                "max": 10.0,
                "default": 2.0,
                "label": "Frequency (Hz)",
            },
            {"name": "color_red", "type": "rgb", "default": [255, 0, 0], "label": "Red Color"},
            {"name": "color_blue", "type": "rgb", "default": [0, 0, 255], "label": "Blue Color"},
        ]
