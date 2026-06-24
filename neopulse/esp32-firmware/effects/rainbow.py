# effects/rainbow.py -- Rainbow wave effect
import time


class RainbowEffect:
    name = "Rainbow"

    @staticmethod
    def run(driver, params, duration_ms):
        speed = params.get("speed", 1.0)
        start = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
            t = time.ticks_ms() * 0.001 * speed
            colors = []
            for i in range(driver.num_pixels):
                hue = ((i * 360 // driver.num_pixels) + t * 50) % 360
                r, g, b = driver.hsv_to_rgb(hue, 255, 255)
                colors.append((r, g, b))
            driver.set_all_colors(colors)
            driver.write()

    @staticmethod
    def get_default_params():
        return {"speed": 1.0}

    @staticmethod
    def get_param_schema():
        return [
            {
                "name": "speed",
                "type": "float",
                "min": 0.1,
                "max": 5.0,
                "default": 1.0,
                "label": "Speed",
            },
        ]
