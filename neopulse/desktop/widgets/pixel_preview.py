"""Pixel preview widget for NeoPulse Studio."""

import tkinter as tk
from tkinter import ttk


class PixelPreviewWidget(ttk.Frame):
    """Visual preview of NeoPixel strip with configurable number of LEDs."""

    def __init__(self, parent, num_pixels=64, pixel_size=12, **kwargs):
        super().__init__(parent, **kwargs)
        self.num_pixels = num_pixels
        self.pixel_size = pixel_size
        self.pixels = []

        # Canvas for rendering pixels
        width = num_pixels * (pixel_size + 2)
        height = pixel_size + 4

        self.canvas = tk.Canvas(
            self, width=width, height=height, bg="#0a0a0a", highlightthickness=0
        )
        self.canvas.pack(padx=4, pady=4)

        # Create pixel rectangles
        for i in range(num_pixels):
            x = i * (pixel_size + 2) + 1
            rect = self.canvas.create_rectangle(
                x, 2, x + pixel_size, pixel_size + 2, fill="#000000", outline="#333333", width=1
            )
            self.pixels.append(rect)

    def update_colors(self, colors):
        """Update pixel colors. Truncates or pads as needed."""
        for i, rect in enumerate(self.pixels):
            if i < len(colors):
                r, g, b = colors[i]
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b)))
                )
                self.canvas.itemconfig(rect, fill=hex_color)
            else:
                self.canvas.itemconfig(rect, fill="#000000")

    def set_num_pixels(self, num):
        """Change the number of pixels displayed."""
        self.num_pixels = num
        # Clear and recreate
        self.canvas.delete("all")
        self.pixels.clear()

        width = num * (self.pixel_size + 2)
        self.canvas.config(width=width)

        for i in range(num):
            x = i * (self.pixel_size + 2) + 1
            rect = self.canvas.create_rectangle(
                x,
                2,
                x + self.pixel_size,
                self.pixel_size + 2,
                fill="#000000",
                outline="#333333",
                width=1,
            )
            self.pixels.append(rect)

    def clear(self):
        """Turn off all pixels."""
        for rect in self.pixels:
            self.canvas.itemconfig(rect, fill="#000000")
