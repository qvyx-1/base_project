# neopixel_driver.py -- High-level NeoPixel driver for ESP32-S3
# Supports up to 256 LEDs with zone-based control

import neopixel


class NeoPixelDriver:
    """NeoPixel driver with zone support and helper methods."""

    def __init__(self, pin_num, num_pixels=64, bpp=3, timing=1):
        if num_pixels > 256:
            raise ValueError("Max 256 pixels supported")

        self.num_pixels = num_pixels
        self.bpp = bpp
        self.pin = neopixel.NeoPixel(
            __import__("machine").Pin(pin_num, __import__("machine").Pin.OUT),
            num_pixels,
            bpp=bpp,
            timing=timing,
        )

        # Current pixel colors (cached)
        self._colors = [(0, 0, 0)] * num_pixels

        # Zone definitions: list of (start, end, name)
        self.zones = []

    def set_pixel(self, index, color):
        """Set a single pixel color. Index 0-255."""
        if 0 <= index < self.num_pixels:
            self._colors[index] = color
            self.pin[index] = color

    def set_pixels(self, start, end, color):
        """Set a range of pixels to the same color."""
        for i in range(start, min(end, self.num_pixels)):
            self._colors[i] = color
            self.pin[i] = color

    def set_zone(self, zone_id, color):
        """Set all pixels in a zone to a color."""
        if zone_id < len(self.zones):
            start, end, name = self.zones[zone_id]
            self.set_pixels(start, end + 1, color)

    def fill(self, color):
        """Fill all pixels with a single color."""
        self.pin.fill(color)
        self._colors = [color] * self.num_pixels

    def write(self):
        """Write current pixel data to the strip."""
        self.pin.write()

    def get_pixel(self, index):
        """Get the color of a single pixel."""
        if 0 <= index < self.num_pixels:
            return self._colors[index]
        return (0, 0, 0)

    def get_colors(self):
        """Get all pixel colors as a list."""
        return list(self._colors)

    def set_all_colors(self, colors):
        """Set all pixel colors from a list. Truncates or pads as needed."""
        for i in range(min(len(colors), self.num_pixels)):
            self._colors[i] = colors[i]
            self.pin[i] = colors[i]

    def clear(self):
        """Turn off all pixels."""
        self.fill((0, 0, 0))

    # --- Helper methods for effects ---

    @staticmethod
    def interpolate_color(c1, c2, t):
        """Linear interpolation between two RGB colors. t in [0, 1]."""
        t = max(0, min(1, t))
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Convert HSV (h: 0-360, s: 0-255, v: 0-255) to RGB."""
        s_norm = s / 255.0
        v_norm = v / 255.0

        c = v_norm * s_norm
        x = c * (1 - abs((h / 60.0) % 2 - 1))
        m = v_norm - c

        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

    @staticmethod
    def rainbow_color(index, total, offset=0):
        """Get a rainbow color for a given index."""
        hue = ((index * 360 // total) + offset) % 360
        return NeoPixelDriver.hsv_to_rgb(hue, 255, 255)

    def gradient(self, start_idx, end_idx, c1, c2):
        """Create a gradient between two colors across a range."""
        length = end_idx - start_idx
        colors = []
        for i in range(length):
            t = i / max(1, length - 1)
            colors.append(self.interpolate_color(c1, c2, t))
        return colors

    def set_gradient(self, start_idx, end_idx, c1, c2):
        """Set a gradient across pixel indices."""
        colors = self.gradient(start_idx, end_idx, c1, c2)
        for i, color in enumerate(colors):
            idx = start_idx + i
            if idx < self.num_pixels:
                self._colors[idx] = color
                self.pin[idx] = color

    def set_rainbow(self, offset=0):
        """Set all pixels to a rainbow pattern."""
        for i in range(self.num_pixels):
            color = self.rainbow_color(i, self.num_pixels, offset)
            self._colors[i] = color
            self.pin[i] = color

    def breathing_effect(self, color, brightness_pct):
        """Apply breathing (fade) effect to all pixels."""
        b = (
            int(color[0] * brightness_pct / 100),
            int(color[1] * brightness_pct / 100),
            int(color[2] * brightness_pct / 100),
        )
        self.fill(b)
