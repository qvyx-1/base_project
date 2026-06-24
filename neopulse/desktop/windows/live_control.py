"""Live Control window for NeoPulse Studio."""
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


class LiveControlWindow(tk.Toplevel):
    """Window for live control of connected ESP32 device."""

    def __init__(self, parent, esp_connection=None):
        super().__init__(parent)
        self.esp = esp_connection
        self.polling = False

        self.title("NeoPulse — Live Steuerung")
        self.geometry("500x600")

        self.transient(parent)
        self.grab_set()

        self._build_ui()

        if self.esp:
            self._connect()

    def _build_ui(self):
        """Build the live control UI."""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Connection status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_var = tk.StringVar(value="Nicht verbunden")
        ttk.Label(status_frame, textvariable=self.status_var,
                 foreground="#f44336").pack(side=tk.LEFT)

        ttk.Button(status_frame, text="Verbinden", command=self._connect).pack(side=tk.RIGHT)

        # Pixel preview (large)
        preview_frame = ttk.LabelFrame(main_frame, text="Live Vorschau", padding=10)
        preview_frame.pack(fill=tk.X, pady=(0, 10))

        self.live_preview_canvas = tk.Canvas(
            preview_frame, width=450, height=40, bg="#0a0a0a"
        )
        self.live_preview_canvas.pack()

        # Create pixel dots
        self.live_pixels = []
        for i in range(64):
            x = i * 7 + 2
            rect = self.live_preview_canvas.create_rectangle(
                x, 5, x + 5, 25, fill="#000", outline="#333", width=1
            )
            self.live_pixels.append(rect)

        # Manual pixel control
        manual_frame = ttk.LabelFrame(main_frame, text="Manuelle Pixel Steuerung", padding=10)
        manual_frame.pack(fill=tk.X, pady=(0, 10))

        # Single pixel set
        row = ttk.Frame(manual_frame)
        row.pack(fill=tk.X, pady=2)

        ttk.Label(row, text="Pixel #").pack(side=tk.LEFT)
        self.pixel_idx_var = tk.IntVar(value=0)
        ttk.Spinbox(row, from_=0, to=255, textvariable=self.pixel_idx_var, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Label(row, text="Farbe:").pack(side=tk.LEFT, padx=(10, 5))
        self.live_color_var = tk.StringVar(value="#ff0000")
        ttk.Entry(row, textvariable=self.live_color_var, width=10).pack(side=tk.LEFT, padx=5)

        ttk.Button(row, text="Setzen", command=self._set_single_pixel).pack(side=tk.LEFT, padx=5)

        # Brightness control
        bright_frame = ttk.LabelFrame(main_frame, text="Helligkeit", padding=10)
        bright_frame.pack(fill=tk.X, pady=(0, 10))

        self.brightness_var = tk.IntVar(value=80)
        ttk.Scale(bright_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                 variable=self.brightness_var).pack(fill=tk.X)

        ttk.Label(bright_frame, textvariable=self.brightness_var).pack()

        ttk.Button(bright_frame, text="Helligkeit senden", command=self._set_brightness).pack(pady=(5, 0))

        # Effects
        effects_frame = ttk.LabelFrame(main_frame, text="Effekte", padding=10)
        effects_frame.pack(fill=tk.X, pady=(0, 10))

        effects = [
            ("strobe", "⚡ Strobe"),
            ("fire", "🔥 Fire"),
            ("emergency_us", "🚨 Emergency US"),
            ("emergency_de", "🇩🇪 Blaulicht DE"),
            ("rainbow", "🌈 Rainbow"),
            ("breathing", "💫 Breathing"),
        ]

        for effect_id, label in effects:
            ttk.Button(effects_frame, text=label, width=20,
                      command=lambda e=effect_id: self._run_effect(e)).pack(pady=2)

        # Show list
        shows_frame = ttk.LabelFrame(main_frame, text="Gespeicherte Shows", padding=10)
        shows_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.shows_listbox = tk.Listbox(shows_frame, height=5, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(shows_frame, orient=tk.VERTICAL, command=self.shows_listbox.yview)
        self.shows_listbox.configure(yscrollcommand=scrollbar.set)

        self.shows_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(shows_frame, text="▶ Abspielen", command=self._play_selected_show).pack(pady=(5, 0))

        # Restart button
        ttk.Button(main_frame, text="⚠ ESP32 Neustarten", command=self._restart_esp).pack(fill=tk.X)

    def _connect(self):
        """Connect to ESP32."""
        if not self.esp:
            # Ask for IP
            dialog = tk.Toplevel(self)
            dialog.title("ESP32 verbinden")
            dialog.geometry("300x150")

            ttk.Label(dialog, text="IP-Adresse:").pack(pady=(10, 5))
            ip_var = tk.StringVar(value="192.168.1.100")
            ttk.Entry(dialog, textvariable=ip_var).pack(pady=5)

            def confirm():
                from desktop.esp.connection import ESPConnection
                self.esp = ESPConnection(ip_var.get())
                dialog.destroy()
                self._connect()

            ttk.Button(dialog, text="Verbinden", command=confirm).pack(pady=(10, 5))
            return

        try:
            state = self.esp.get_state()
            if state.get("status") == "ok":
                self.status_var.set(f"Verbunden: {self.esp.ip}")
                self.status_var.foreground = "#4caf50"
                self._load_shows()
                self._start_polling()
            else:
                self.status_var.set("Verbindung fehlgeschlagen")
                self.status_var.foreground = "#f44336"
        except Exception as e:
            self.status_var.set(f"Fehler: {str(e)}")
            self.status_var.foreground = "#f44336"

    def _load_shows(self):
        """Load saved shows from ESP32."""
        try:
            shows = self.esp.get_shows()
            self.shows_listbox.delete(0, tk.END)
            for show in shows:
                self.shows_listbox.insert(tk.END, show.get("name", "Untitled"))
        except Exception as e:
            print(f"Failed to load shows: {e}")

    def _set_single_pixel(self):
        """Set a single pixel color."""
        if not self.esp:
            return

        idx = self.pixel_idx_var.get()
        hex_color = self.live_color_var.get()

        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)

            result = self.esp.set_pixels([(idx, [r, g, b])])
            if result.get("status") == "ok":
                # Update preview
                hex_str = "#{:02x}{:02x}{:02x}".format(r, g, b)
                self.live_preview_canvas.itemconfig(self.live_pixels[idx], fill=hex_str)
        except Exception as e:
            messagebox.showerror("Fehler", f"Pixel setzen fehlgeschlagen: {e}")

    def _set_brightness(self):
        """Send brightness to ESP32."""
        if not self.esp:
            return

        try:
            result = self.esp.set_brightness(self.brightness_var.get())
            if result.get("status") == "ok":
                messagebox.showinfo("Erfolg", f'Helligkeit auf {result.get("brightness", 0)}% gesetzt.')
        except Exception as e:
            messagebox.showerror("Fehler", f"Helligkeit setzen fehlgeschlagen: {e}")

    def _run_effect(self, effect_type):
        """Run an effect on the ESP32."""
        if not self.esp:
            return

        try:
            result = self.esp.run_effect(effect_type, duration_ms=10000)
            if result.get("status") == "ok":
                messagebox.showinfo("Effekt", f'Effekt "{effect_type}" gestartet.')
            else:
                messagebox.showerror("Fehler", result.get("message", "Unbekannter Fehler"))
        except Exception as e:
            messagebox.showerror("Fehler", f"Effekt starten fehlgeschlagen: {e}")

    def _play_selected_show(self):
        """Play the selected show."""
        selection = self.shows_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Show aus.")
            return

        try:
            shows = self.esp.get_shows()
            idx = selection[0]
            if idx < len(shows):
                result = self.esp.play_show(shows[idx].get("id"))
                if result.get("status") == "ok":
                    messagebox.showinfo("Abspielen", f'Show "{result.get("show", "")}" wird abgespielt.')
        except Exception as e:
            messagebox.showerror("Fehler", f"Show abspielen fehlgeschlagen: {e}")

    def _restart_esp(self):
        """Restart the ESP32."""
        if not self.esp:
            return

        if messagebox.askyesno("Bestätigung", "ESP32 wirklich neustarten?"):
            try:
                result = self.esp.restart(soft=True)
                if result.get("status") == "ok":
                    messagebox.showinfo("Neustart", "ESP32 wird neu gestartet...")
                    self.polling = False
            except Exception as e:
                messagebox.showerror("Fehler", f"Restart fehlgeschlagen: {e}")

    def _start_polling(self):
        """Start polling ESP32 state."""
        self.polling = True

        def poll():
            if not self.polling:
                return

            try:
                state = self.esp.get_state()
                # Update pixel preview with current colors
                colors = state.get("pixels", [])
                if colors:
                    for i, color in enumerate(colors[:len(self.live_pixels)]):
                        hex_str = "#{:02x}{:02x}{:02x}".format(*color)
                        self.live_preview_canvas.itemconfig(self.live_pixels[i], fill=hex_str)
            except:
                pass

            self.after(500, poll)

        poll()

    def destroy(self):
        """Clean up on close."""
        self.polling = False
        super().destroy()
