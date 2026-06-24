# NeoPulse Studio — Hauptanwendung
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.esp.connection import ESPConnection
from desktop.windows.live_control import LiveControlWindow
from desktop.windows.project_manager import ProjectManagerWindow
from desktop.windows.setup_wizard import SetupWizardWindow
from desktop.windows.show_editor import ShowEditorWindow


class NeoPulseApp:
    """Main application class for NeoPulse Studio."""

    def __init__(self, root):
        self.root = root
        self.root.title("NeoPulse Studio — NeoPixel Controller")
        self.root.geometry("1000x650")

        # Current state
        self.esp = None
        self.current_show = None

        self._build_ui()

    def _build_ui(self):
        """Build the main application UI."""
        # Menu bar
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Neues Projekt", command=self._new_project)
        file_menu.add_command(label="Öffnen...", command=self._open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)

        # ESP menu
        esp_menu = tk.Menu(menubar, tearoff=0)
        esp_menu.add_command(label="ESP32 Einrichten", command=self._setup_esp)
        esp_menu.add_command(label="Live Steuerung", command=self._live_control)
        esp_menu.add_separator()
        esp_menu.add_command(label="Verbinden...", command=self._connect_esp)
        menubar.add_cascade(label="ESP32", menu=esp_menu)

        # Editor menu
        editor_menu = tk.Menu(menubar, tearoff=0)
        editor_menu.add_command(label="Show Editor", command=self._open_editor)
        editor_menu.add_command(label="Emulator öffnen", command=self._open_emulator)
        menubar.add_cascade(label="Editor", menu=editor_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Dokumentation", command=self._show_docs)
        help_menu.add_command(label="Über NeoPulse", command=self._show_about)
        menubar.add_cascade(label="Hilfe", menu=help_menu)

        self.root.config(menu=menubar)

        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Welcome screen
        welcome_frame = ttk.Frame(main_frame)
        welcome_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            welcome_frame,
            text="🎨 NeoPulse Studio",
            font=("Arial", 24, "bold"),
            foreground="#7c6ff5",
        ).pack(pady=(40, 10))

        ttk.Label(
            welcome_frame,
            text="ESP32 NeoPixel Controller & Show Editor",
            font=("Arial", 12),
            foreground="#888",
        ).pack(pady=(0, 30))

        # Quick action buttons
        btn_frame = ttk.Frame(welcome_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="🔧 ESP32 Einrichten", width=25, command=self._setup_esp).pack(
            pady=5
        )

        ttk.Button(btn_frame, text="🎬 Show Editor", width=25, command=self._open_editor).pack(
            pady=5
        )

        ttk.Button(btn_frame, text="📡 Live Steuerung", width=25, command=self._live_control).pack(
            pady=5
        )

        ttk.Button(btn_frame, text="🎮 Emulator", width=25, command=self._open_emulator).pack(
            pady=5
        )

        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Bereit")
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
            fill=tk.X
        )

    def _setup_esp(self):
        """Open the ESP32 setup wizard."""
        SetupWizardWindow(self.root, on_complete=self._on_setup_complete)

    def _on_setup_complete(self, config):
        """Handle setup wizard completion."""
        self.esp = ESPConnection(config["ip"], port=80)
        self.status_var.set(f"ESP32 eingerichtet: {config['ip']}")
        messagebox.showinfo("Erfolg", "ESP32 erfolgreich eingerichtet!")

    def _connect_esp(self):
        """Connect to an existing ESP32."""
        dialog = tk.Toplevel(self.root)
        dialog.title("ESP32 verbinden")
        dialog.geometry("350x150")

        ttk.Label(dialog, text="IP-Adresse:").pack(pady=(10, 5))
        ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(dialog, textvariable=ip_var).pack(padx=20, pady=5)

        def confirm():
            self.esp = ESPConnection(ip_var.get())
            if self.esp.ping():
                state = self.esp.get_state()
                self.status_var.set(f"Verbunden: {ip_var.get()}")
                messagebox.showinfo("Erfolg", f"Verbunden mit {ip_var.get()}!")
                dialog.destroy()
            else:
                messagebox.showerror("Fehler", "Verbindung fehlgeschlagen.")

        ttk.Button(dialog, text="Verbinden", command=confirm).pack(pady=(10, 5))

    def _open_editor(self):
        """Open the show editor."""
        ShowEditorWindow(self.root)

    def _live_control(self):
        """Open live control window."""
        if not self.esp:
            messagebox.showwarning("Warnung", "Bitte verbinden Sie zuerst einen ESP32.")
            return

        LiveControlWindow(self.root, esp_connection=self.esp)

    def _open_emulator(self):
        """Open the browser emulator."""
        import os
        import webbrowser

        emulator_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "emulator", "index.html"
        )

        if os.path.exists(emulator_path):
            url = f"file://{os.path.abspath(emulator_path)}"
            webbrowser.open(url)
        else:
            messagebox.showinfo("Info", f"Emulator:\n\nÖffnen Sie im Browser:\n{emulator_path}")

    def _new_project(self):
        """Create a new project."""
        ProjectManagerWindow(self.root)

    def _open_project(self):
        """Open an existing project."""
        from tkinter import filedialog

        filepath = filedialog.askopenfilename(
            title="Projekt öffnen",
            filetypes=[("NeoPulse Projekte", "*.npulse"), ("JSON Dateien", "*.json")],
        )

        if filepath:
            try:
                with open(filepath, "r") as f:
                    import json

                    data = json.load(f)

                self.status_var.set(f"Projekt geöffnet: {filepath}")
                messagebox.showinfo("Erfolg", f'Projekt "{data.get("name", "")}" geladen.')
            except Exception as e:
                messagebox.showerror("Fehler", f"Projekt laden fehlgeschlagen:\n{e}")

    def _show_docs(self):
        """Show documentation."""
        import webbrowser

        docs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README.md"
        )

        if os.path.exists(docs_path):
            # Open in browser as markdown is not natively displayed
            webbrowser.open("file://" + os.path.abspath(docs_path))
        else:
            messagebox.showinfo("Dokumentation", "Siehe README.md im Projektverzeichnis.")

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "Über NeoPulse Studio",
            "NeoPulse Studio v1.0\n\n"
            "ESP32 NeoPixel Controller & Show Editor\n\n"
            "Features:\n"
            "- MicroPython Firmware flashen\n"
            "- Keyframe-basierte Show-Erstellung\n"
            "- Parametrierbare Effekte (Strobe, Fire, Emergency...)\n"
            "- Live-Steuerung über HTTP API\n"
            "- Browser-basierter Emulator/Simulator\n\n"
            "Für ESP32-S3 mit MicroPython und WS2812/NeoPixel LEDs.",
        )


def main():
    """Entry point for NeoPulse Studio."""
    root = tk.Tk()

    # Set window icon if available
    try:
        root.iconbitmap(default="/usr/share/icons/hicolor/48x48/apps/application-x-executable.png")
    except:
        pass

    app = NeoPulseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
