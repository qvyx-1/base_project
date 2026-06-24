# effects/emergency_de.py -- German emergency vehicle pattern (Blaulicht)
import time


class EmergencyDEEffect:
    name = "Blaulicht (DE)"

    @staticmethod
    def run(driver, params, duration_ms):
        freq = params.get("frequency", 1.5)
        color_blue = params.get("color_blue", (0, 0, 255))
        start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
            phase = (time.ticks_ms() / 1000.0 * freq) % 4

            if phase < 0.5:
                # Solid blue
                driver.fill(color_blue)
            elif phase < 1.0:
                # Off
                driver.fill((0, 0, 0))
            elif phase < 2.0:
                # Fast flash (siren pattern)
                if int(time.ticks_ms() / 80) % 2:
                    driver.fill(color_blue)
                else:
                    driver.fill((0, 0, 0))
            else:
                # Off before repeat
                driver.fill((0, 0, 0))
            driver.write()

    @staticmethod
    def get_default_params():
        return {"frequency": 1.5, "color_blue": (0, 0, 255)}

    @staticmethod
    def get_param_schema():
        return [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.5,
                "max": 5.0,
                "default": 1.5,
                "label": "Frequency (Hz)",
            },
            {"name": "color_blue", "type": "rgb", "default": [0, 0, 255], "label": "Blue Color"},
        ]
