"""Color picker widget for NeoPulse Studio."""

import tkinter as tk
from tkinter import colorchooser, ttk


class ColorPickerWidget(ttk.Frame):
    """A color picker with hex input, color swatch, and RGB sliders."""

    def __init__(self, parent, initial_color=(255, 0, 0), on_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.current_color = list(initial_color)

        # Color swatch
        self.swatch = tk.Label(
            self, bg=self._rgb_to_hex(initial_color), width=6, height=2, relief="solid", bd=1
        )
        self.swatch.pack(side=tk.LEFT, padx=(0, 8))
        self.swatch.bind("<Button-1>", lambda e: self._choose_color())

        # Hex input
        self.hex_var = tk.StringVar(value=self._rgb_to_hex(initial_color))
        hex_entry = ttk.Entry(self, textvariable=self.hex_var, width=10)
        hex_entry.pack(side=tk.LEFT, padx=(0, 8))
        hex_entry.bind("<Return>", lambda e: self._from_hex())

        # RGB sliders
        for i, (label, val) in enumerate(
            [("R", initial_color[0]), ("G", initial_color[1]), ("B", initial_color[2])]
        ):
            row = ttk.Frame(self)
            row.pack(fill=tk.X, padx=4)

            ttk.Label(row, text=f"{label}:", width=4).pack(side=tk.LEFT)

            slider = ttk.Scale(
                row,
                from_=0,
                to=255,
                orient=tk.HORIZONTAL,
                command=lambda v, idx=i: self._update_rgb(idx, float(v)),
            )
            slider.set(val)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))

            val_label = ttk.Label(row, text=str(val), width=4)
            val_label.pack(side=tk.LEFT)
            self._slider_labels = getattr(self, "_slider_labels", {})
            self._slider_labels[label] = val_label

    def _rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex string."""
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def _choose_color(self):
        """Open color chooser dialog."""
        color = colorchooser.askcolor(color=self._rgb_to_hex(tuple(self.current_color)))
        if color[1]:
            self.set_color(tuple(int(c) for c in color[0]))

    def _from_hex(self):
        """Parse hex string to RGB."""
        hex_val = self.hex_var.get()
        if hex_val.startswith("#") and len(hex_val) == 7:
            try:
                r = int(hex_val[1:3], 16)
                g = int(hex_val[3:5], 16)
                b = int(hex_val[5:7], 16)
                self.set_color((r, g, b))
            except ValueError:
                pass

    def _update_rgb(self, idx, value):
        """Update RGB value from slider."""
        self.current_color[idx] = int(value)
        if self._slider_labels:
            labels = ["R", "G", "B"]
            self._slider_labels[labels[idx]].config(text=str(int(value)))
        hex_val = self._rgb_to_hex(tuple(self.current_color))
        self.hex_var.set(hex_val)
        self.swatch.config(bg=hex_val)
        if self.on_change:
            self.on_change(tuple(self.current_color))

    def get_color(self):
        """Get current color as RGB tuple."""
        return tuple(self.current_color)

    def set_color(self, rgb):
        """Set color from RGB tuple."""
        self.current_color = list(rgb)
        hex_val = self._rgb_to_hex(rgb)
        self.hex_var.set(hex_val)
        self.swatch.config(bg=hex_val)
        sliders = [self.current_color[0], self.current_color[1], self.current_color[2]]
        for i, s in enumerate(self.winfo_children[2:5]):  # RGB slider frames
            if hasattr(s, "children"):
                for child in s.winfo_children():
                    if isinstance(child, ttk.Scale):
                        child.set(sliders[i])
                    elif isinstance(child, ttk.Label) and sliders[i] == int(child.cget("text")):
                        pass
        if self.on_change:
            self.on_change(tuple(self.current_color))
