"""Show Editor window for NeoPulse Studio."""
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

_DESKTOP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(_DESKTOP)
for _p in [_ROOT, _DESKTOP]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from desktop.models.scene import Scene
from desktop.models.show import Show
from desktop.widgets.pixel_preview import PixelPreviewWidget
from desktop.widgets.scene_tree import SceneTreeWidget
from desktop.widgets.timeline import TimelineWidget


class ShowEditorWindow(tk.Toplevel):
    """Main show editor window with timeline, pixel preview, and scene management."""

    def __init__(self, parent, show=None):
        super().__init__(parent)
        self.show = show or Show()
        self.current_scene_idx = -1

        self.title(f"NeoPulse — Show Editor: {self.show.name}")
        self.geometry("1200x700")

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._load_show()

    def _build_ui(self):
        """Build the editor UI layout."""
        # Main container with paned window
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Left panel (scenes list + controls)
        left_frame = ttk.Frame(main_pane, width=250)
        main_pane.add(left_frame, weight=1)

        # Right panel (timeline + preview)
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)

        self._build_left_panel(left_frame)
        self._build_right_panel(right_frame)

    def _build_left_panel(self, parent):
        """Build left panel with scene tree and controls."""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="+ Szene", command=self._add_scene).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="▶ Play", command=self._play_show).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 Speichern", command=self._save_show).pack(side=tk.LEFT, padx=2)

        # Scene tree
        scene_frame = ttk.LabelFrame(parent, text="Szenen", padding=5)
        scene_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.scene_tree = SceneTreeWidget(scene_frame, on_scene_select=self._on_scene_select)
        self.scene_tree.pack(fill=tk.BOTH, expand=True)

        # Scene properties
        props_frame = ttk.LabelFrame(parent, text="Eigenschaften", padding=5)
        props_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(props_frame, text="Name:").pack(anchor=tk.W)
        self.scene_name_var = tk.StringVar()
        ttk.Entry(props_frame, textvariable=self.scene_name_var).pack(fill=tk.X, pady=(0, 5))

        ttk.Label(props_frame, text="Dauer (s):").pack(anchor=tk.W)
        self.duration_var = tk.DoubleVar(value=10.0)
        ttk.Spinbox(props_frame, from_=1, to=60, increment=0.5, textvariable=self.duration_var, width=10).pack(anchor=tk.W, pady=(0, 5))

        ttk.Label(props_frame, text="Interpolation:").pack(anchor=tk.W)
        self.interp_var = tk.StringVar(value="linear")
        ttk.Combobox(props_frame, textvariable=self.interp_var,
                    values=["linear", "sine", "step", "ease_in_out"], width=8).pack(anchor=tk.W, pady=(0, 5))

        ttk.Label(props_frame, text="Loop:").pack(anchor=tk.W)
        self.loop_var = tk.StringVar(value="single")
        ttk.Combobox(props_frame, textvariable=self.loop_var,
                    values=["single", "endless", "pingpong"], width=8).pack(anchor=tk.W)

    def _build_right_panel(self, parent):
        """Build right panel with timeline and pixel preview."""
        # Timeline
        timeline_frame = ttk.LabelFrame(parent, text="Timeline", padding=5)
        timeline_frame.pack(fill=tk.X, padx=5, pady=5)

        self.timeline = TimelineWidget(timeline_frame, width=800, height=150)
        self.timeline.pack(fill=tk.X)

        # Pixel preview
        preview_frame = ttk.LabelFrame(parent, text="Pixel-Vorschau", padding=5)
        preview_frame.pack(fill=tk.X, padx=5, pady=5)

        self.pixel_preview = PixelPreviewWidget(preview_frame, num_pixels=64)
        self.pixel_preview.pack(fill=tk.X)

    def _load_show(self):
        """Load the show data into the UI."""
        # Convert show scenes to dict format for tree
        scenes_data = []
        for scene in self.show.scenes:
            scenes_data.append({
                "id": scene.id,
                "name": scene.name,
                "duration": scene.duration,
                "keyframes": scene.keyframes,
                "interpolation": scene.interpolation,
                "loop_mode": scene.loop_mode,
            })

        self.scene_tree.set_scenes(scenes_data)

    def _add_scene(self):
        """Add a new scene to the show."""
        scene = Scene(
            name=f"Szene {len(self.show.scenes) + 1}",
            duration=10.0,
            interpolation="linear",
            loop_mode="single",
        )

        self.show.add_scene(scene)

        # Update tree
        scenes_data = []
        for s in self.show.scenes:
            scenes_data.append({
                "id": s.id,
                "name": s.name,
                "duration": s.duration,
                "keyframes": s.keyframes,
                "interpolation": s.interpolation,
                "loop_mode": s.loop_mode,
            })

        self.scene_tree.set_scenes(scenes_data)
        self.current_scene_idx = len(self.show.scenes) - 1

    def _on_scene_select(self, idx, scene_data, edit=False):
        """Handle scene selection."""
        if scene_data:
            self.current_scene_idx = idx
            self.scene_name_var.set(scene_data.get("name", ""))
            self.duration_var.set(scene_data.get("duration", 10.0))
            self.interp_var.set(scene_data.get("interpolation", "linear"))
            self.loop_var.set(scene_data.get("loop_mode", "single"))

            # Update timeline
            if scene_data.get("keyframes"):
                self.timeline.set_current_scene(scene_data)
                self.timeline.draw()

    def _play_show(self):
        """Start playing the show."""
        if not self.show.scenes:
            messagebox.showwarning("Warnung", "Keine Szenen vorhanden.")
            return

        # Update pixel preview with animation
        self._animate_preview()

    def _animate_preview(self):
        """Animate the pixel preview."""
        if not hasattr(self, "_animating") or not self._animating:
            return

        elapsed = getattr(self, "_anim_elapsed", 0) + 0.016

        # Get current scene colors
        if self.current_scene_idx >= 0 and self.show.scenes:
            scene = self.show.scenes[self.current_scene_idx]
            colors = self._get_scene_colors(scene, elapsed)
            self.pixel_preview.update_colors(colors)

        self._anim_elapsed = elapsed

        # Loop handling
        if self.current_scene_idx >= 0 and self.show.scenes:
            scene = self.show.scenes[self.current_scene_idx]
            loop_mode = getattr(scene, "loop_mode", "single")

            if loop_mode == "endless" and elapsed >= scene.duration:
                self._anim_elapsed = 0
            elif loop_mode == "pingpong":
                cycle = elapsed % (scene.duration * 2)
                if cycle > scene.duration:
                    self._anim_elapsed = scene.duration - (cycle - scene.duration)

        self.after(16, self._animate_preview)

    def _get_scene_colors(self, scene, time):
        """Get pixel colors for a scene at a given time."""
        keyframes = scene.keyframes if hasattr(scene, "keyframes") else []

        if not keyframes:
            return [(0, 0, 0)] * getattr(scene, "num_pixels", 64)

        # Find surrounding keyframes
        for i in range(len(keyframes) - 1):
            if keyframes[i].time <= time <= keyframes[i + 1].time:
                dur = keyframes[i + 1].time - keyframes[i].time
                t = (time - keyframes[i].time) / max(0.001, dur)

                # Apply interpolation
                interp = getattr(scene, "interpolation", "linear")
                if interp == "sine":
                    import math
                    t = math.sin(t * math.pi / 2)
                elif interp == "step":
                    t = 1.0 if t > 0.5 else 0.0
                elif interp == "ease_in_out":
                    t = 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

                # Interpolate colors
                num_pixels = getattr(scene, "num_pixels", 64)
                colors = []
                for j in range(num_pixels):
                    c1 = keyframes[i].colors[j] if j < len(keyframes[i].colors) else (0, 0, 0)
                    c2 = keyframes[i + 1].colors[j] if j < len(keyframes[i + 1].colors) else (0, 0, 0)
                    colors.append((
                        int(c1[0] + (c2[0] - c1[0]) * t),
                        int(c1[1] + (c2[1] - c1[1]) * t),
                        int(c1[2] + (c2[2] - c1[2]) * t),
                    ))
                return colors

        # After last keyframe
        last_kf = keyframes[-1]
        num_pixels = getattr(scene, "num_pixels", 64)
        return [last_kf.colors[j] if j < len(last_kf.colors) else (0, 0, 0) for j in range(num_pixels)]

    def _save_show(self):
        """Save the show to file."""
        # Update scene data from UI
        if self.current_scene_idx >= 0 and self.show.scenes:
            scene = self.show.scenes[self.current_scene_idx]
            scene.name = self.scene_name_var.get()
            scene.duration = self.duration_var.get()
            scene.interpolation = self.interp_var.get()
            scene.loop_mode = self.loop_var.get()

        # Save to JSON file
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Show speichern"
        )

        if filepath:
            show_data = self.show.to_dict()
            import json
            with open(filepath, "w") as f:
                json.dump(show_data, f, indent=2)

            messagebox.showinfo("Erfolg", f"Show gespeichert als:\n{filepath}")

    def start_preview(self):
        """Start the preview animation."""
        self._animating = True
        self._anim_elapsed = 0
        self._animate_preview()

    def stop_preview(self):
        """Stop the preview animation."""
        self._animating = False
