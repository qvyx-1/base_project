"""Setup Wizard window for NeoPulse Studio."""

import os
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from desktop.esp.flasher import ESPFlasher
from desktop.esp.mdns_discovery import discover_neopulse_devices


class SetupWizardWindow(tk.Toplevel):
    """Wizard-style window for setting up the ESP32 device."""

    def __init__(self, parent, on_complete=None):
        super().__init__(parent)
        self.on_complete = on_complete
        self.flash = ESPFlasher()

        self.title("NeoPulse — ESP32 Einrichtung")
        self.geometry("700x550")
        self.resizable(False, False)

        # Center window
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._start_discovery()

    def _build_ui(self):
        """Build the wizard UI."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            main_frame, text="🔧 ESP32 Einrichtungsassistent", font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))

        # Progress indicator
        self.progress_var = tk.StringVar(value="Schritt 1 von 4: Gerät finden")
        ttk.Label(main_frame, textvariable=self.progress_var, font=("Arial", 10)).pack(pady=(0, 10))

        # Progress bar
        progress = ttk.Progressbar(main_frame, maximum=4, value=1)
        progress.pack(fill=tk.X, pady=(0, 15))

        # Step 1: Device Discovery
        self._create_discovery_section(main_frame)

        # Step 2: Firmware Flash (hidden initially)
        self.flash_frame = ttk.LabelFrame(
            main_frame, text="Schritt 2: MicroPython Firmware flashen", padding=10
        )
        self._create_flash_section(self.flash_frame)

        # Step 3: WiFi Configuration (hidden initially)
        self.wifi_frame = ttk.LabelFrame(
            main_frame, text="Schritt 3: WiFi Konfiguration", padding=10
        )
        self._create_wifi_section(self.wifi_frame)

        # Step 4: NeoPixel Configuration (hidden initially)
        self.np_frame = ttk.LabelFrame(
            main_frame, text="Schritt 4: NeoPixel Konfiguration", padding=10
        )
        self._create_np_section(self.np_frame)

        # Navigation buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        self.btn_back = ttk.Button(btn_frame, text="← Zurück", width=12, command=self._go_back)
        self.btn_back.pack(side=tk.LEFT)

        self.btn_next = ttk.Button(btn_frame, text="Weiter →", width=12, command=self._go_next)
        self.btn_next.pack(side=tk.RIGHT, padx=(5, 0))

        self.btn_finish = ttk.Button(
            btn_frame, text="✓ Fertig", width=12, command=self._finish, state="disabled"
        )
        self.btn_finish.pack(side=tk.RIGHT, padx=(5, 0))

        # State tracking
        self.current_step = 1
        self.selected_device = None

    def _create_discovery_section(self, parent):
        """Create device discovery section."""
        frame = ttk.LabelFrame(parent, text="Schritt 1: ESP32 Gerät finden", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Discovery button
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="🔍 Automatisch suchen", command=self._start_discovery).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(btn_frame, text="⌨️ Manuelles IP-Eingabe", command=self._manual_ip_input).pack(
            side=tk.LEFT
        )

        # Device list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.X)

        self.device_listbox = tk.Listbox(list_frame, height=5, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.device_listbox.yview)
        self.device_listbox.configure(yscrollcommand=scrollbar.set)

        self.device_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.device_listbox.bind("<<ListboxSelect>>", self._on_device_select)

        # Status label
        self.discovery_status = ttk.Label(
            frame, text='Klicken Sie auf "Suchen" um Geräte zu finden.', foreground="#888"
        )
        self.discovery_status.pack(pady=(5, 0))

    def _create_flash_section(self, parent):
        """Create firmware flash section."""
        parent.pack(fill=tk.X, pady=(0, 10))

        # Chip selection
        ttk.Label(parent, text="Chip-Typ:").pack(anchor=tk.W)
        self.chip_var = tk.StringVar(value="esp32s3")
        chip_frame = ttk.Frame(parent)
        chip_frame.pack(fill=tk.X, pady=(0, 10))

        for chip, text in [
            ("esp32s3", "ESP32-S3 (empfohlen)"),
            ("esp32", "ESP32 Classic"),
            ("esp32c3", "ESP32-C3"),
        ]:
            ttk.Radiobutton(chip_frame, text=text, variable=self.chip_var, value=chip).pack(
                anchor=tk.W
            )

        # Port selection
        ttk.Label(parent, text="Serial Port:").pack(anchor=tk.W)
        self.port_var = tk.StringVar()
        port_frame = ttk.Frame(parent)
        port_frame.pack(fill=tk.X, pady=(0, 10))

        self.port_combo = ttk.Combobox(
            port_frame, textvariable=self.port_var, state="readonly", width=40
        )
        self.port_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(port_frame, text="Ports aktualisieren", command=self._refresh_ports).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        # Firmware selection
        ttk.Label(parent, text="Firmware:").pack(anchor=tk.W)
        self.firmware_var = tk.StringVar()
        self.firmware_combo = ttk.Combobox(port_frame, state="readonly", width=30)
        self._update_firmware_options()

        # Flash button and status
        flash_btn_frame = ttk.Frame(parent)
        flash_btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.flash_btn = ttk.Button(
            flash_btn_frame, text="📡 Firmware flashen", command=self._flash_firmware
        )
        self.flash_btn.pack(side=tk.LEFT)

        self.flash_status = scrolledtext.ScrolledText(parent, height=4, font=("Courier", 9))
        self.flash_status.pack(fill=tk.X, pady=(5, 0))

    def _create_wifi_section(self, parent):
        """Create WiFi configuration section."""
        parent.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(parent, text="WiFi SSID:").pack(anchor=tk.W)
        self.ssid_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.ssid_var, width=40).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(parent, text="WiFi Passwort:").pack(anchor=tk.W)
        self.pw_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.pw_var, show="*", width=40).pack(
            fill=tk.X, pady=(0, 10)
        )

        self.wifi_status = ttk.Label(parent, text="", foreground="#888")
        self.wifi_status.pack(pady=(5, 0))

    def _create_np_section(self, parent):
        """Create NeoPixel configuration section."""
        parent.pack(fill=tk.X, pady=(10, 0))

        config_frame = ttk.Frame(parent)
        config_frame.pack(fill=tk.X)

        # Grid layout for config
        configs = [
            ("GPIO Pin:", "pixel_pin", 38),
            ("Anzahl LEDs:", "num_pixels", 64),
            ("Helligkeit (%):", "brightness", 80),
        ]

        self.np_configs = {}
        for label, key, default in configs:
            ttk.Label(config_frame, text=label).grid(
                row=len(configs), column=0, sticky=tk.W, pady=2
            )
            var = tk.IntVar(value=default)
            entry = ttk.Entry(config_frame, textvariable=var, width=10)
            entry.grid(row=len(configs), column=1, padx=(5, 10))
            self.np_configs[key] = var

    def _start_discovery(self):
        """Start device discovery."""
        self.device_listbox.delete(0, tk.END)
        self.discovery_status.config(text="Suche läuft...")

        # Run discovery in background thread
        def discover():
            devices = discover_neopulse_devices(timeout=3.0)
            self.after(0, lambda: self._on_discovery_complete(devices))

        import threading

        threading.Thread(target=discover, daemon=True).start()

    def _on_discovery_complete(self, devices):
        """Handle discovery results."""
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        if devices: 
            self.device_listbox.delete(0, tk.END)
            for dev in devices:
                ip = dev.get("ip", "unknown")
                state = dev.get("state", {})
                info = state.get("system", {})
                chip = info.get("chip", "ESP32")
                self.device_listbox.insert(tk.END, f"{ip} ({chip})")
            self.discovery_status.config(
                text=f"{len(devices)} Gerät(e) gefunden!", foreground="#4caf50"
            )
        else:
            self.discovery_status.config(
                text="Keine Geräte gefunden. Versuchen Sie manuelle Eingabe.", foreground="#f44336"
            )

    def _on_device_select(self, event):
        """Handle device selection."""
        selection = self.device_listbox.curselection()
        if selection:
            idx = selection[0]
            text = self.device_listbox.get(idx)
            ip = text.split(" ")[0]  # Extract IP
            self.selected_device = {"ip": ip, "text": text}

    def _manual_ip_input(self):
        """Open manual IP input dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("IP-Adresse eingeben")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="ESP32 IP-Adresse:").pack(pady=(10, 5))
        ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(dialog, textvariable=ip_var, width=30).pack(pady=5)

        def confirm():
            ip = ip_var.get()
            self.selected_device = {"ip": ip, "text": f"{ip} (manuell)"}
            self.device_listbox.delete(0, tk.END)
            self.device_listbox.insert(0, ip)
            dialog.destroy()

        ttk.Button(dialog, text="Verbinden", command=confirm).pack(pady=(10, 5))

    def _refresh_ports(self):
        """Refresh available serial ports."""
        ports = self.flash.detect_ports()
        self.port_combo["values"] = [f"{p['port']} - {p['description']}" for p in ports]
        if ports:
            self.port_var.set(f"{ports[0]['port']} - {ports[0]['description']}")

    def _update_firmware_options(self):
        """Update firmware dropdown options."""
        firmwares = self.flash.get_available_firmwares()
        self.firmware_combo["values"] = [f["name"] for f in firmwares]
        if firmwares:
            self.firmware_var.set(firmwares[0]["url"])

    def _go_next(self):
        """Go to next step."""
        if self.current_step == 1:
            if not self.selected_device:
                messagebox.showwarning("Warnung", "Bitte wählen Sie ein Gerät aus.")
                return
            self.flash_frame.pack(fill=tk.X, pady=(0, 10))
            self.progress_var.set("Schritt 2 von 4: Firmware flashen")
            self.current_step = 2
        elif self.current_step == 2:
            if not hasattr(self, "_flash_complete") or not self._flash_complete:
                messagebox.showwarning("Warnung", "Bitte flashen Sie zuerst die Firmware.")
                return
            self.wifi_frame.pack(fill=tk.X, pady=(0, 10))
            self.progress_var.set("Schritt 3 von 4: WiFi konfigurieren")
            self.current_step = 3
        elif self.current_step == 3:
            if not self.ssid_var.get():
                messagebox.showwarning("Warnung", "Bitte geben Sie eine WiFi SSID ein.")
                return
            self.np_frame.pack(fill=tk.X, pady=(10, 0))
            self.progress_var.set("Schritt 4 von 4: NeoPixel konfigurieren")
            self.current_step = 4
        elif self.current_step == 4:
            self._finish()

    def _go_back(self):
        """Go to previous step."""
        if self.current_step > 1:
            if self.current_step == 4:
                self.np_frame.pack_forget()
            elif self.current_step == 3:
                self.wifi_frame.pack_forget()
            elif self.current_step == 2:
                self.flash_frame.pack_forget()

            self.current_step -= 1
            self.progress_var.set(f"Schritt {self.current_step} von 4")

    def _flash_firmware(self):
        """Start firmware flashing."""
        port_text = self.port_var.get()
        if not port_text:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Serial Port.")
            return

        port = port_text.split(" - ")[0]
        chip = self.chip_var.get()

        # Disable button during flash
        self.flash_btn.config(state="disabled")
        self.flash_status.delete(1.0, tk.END)
        self.flash_status.insert(tk.END, "Flash wird vorbereitet...\n")

        def flash_thread():
            result = self.flash.flash_firmware(port, chip=chip)
            self.after(0, lambda: self._on_flash_complete(result))

        import threading

        threading.Thread(target=flash_thread, daemon=True).start()

    def _on_flash_complete(self, result):
        """Handle flash completion."""
        self.flash_btn.config(state="normal")

        msg = result.get("message", "")
        success = result.get("success", False)

        self.flash_status.insert(tk.END, f"\n{'✓' if success else '✗'} {msg}\n")

        if success:
            self._flash_complete = True
            self.flash_status.see(tk.END)
            messagebox.showinfo("Erfolg", "Firmware erfolgreich geflasht!")
            # Enable next step
            self.btn_next.config(state="normal")
        else:
            messagebox.showerror("Fehler", f"Flash fehlgeschlagen:\n{msg}")

    def _finish(self):
        """Complete the wizard."""
        config = {
            "ip": self.selected_device["ip"] if self.selected_device else "",
            "ssid": self.ssid_var.get() if hasattr(self, "ssid_var") else "",
            "password": self.pw_var.get() if hasattr(self, "pw_var") else "",
            "pixel_pin": self.np_configs.get("pixel_pin", tk.IntVar()).get()
            if hasattr(self, "np_configs")
            else 38,
            "num_pixels": self.np_configs.get("num_pixels", tk.IntVar()).get()
            if hasattr(self, "np_configs")
            else 64,
            "brightness": self.np_configs.get("brightness", tk.IntVar()).get()
            if hasattr(self, "np_configs")
            else 80,
        }

        self.destroy()
        if self.on_complete:
            self.on_complete(config)
