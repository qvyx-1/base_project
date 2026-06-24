"""Timeline widget for NeoPulse Studio."""

import tkinter as tk


class TimelineWidget(tk.Canvas):
    """Interactive timeline editor for keyframe-based animations."""

    def __init__(self, parent, width=800, height=200, **kwargs):
        super().__init__(parent, width=width, height=height, bg="#0a0a14", **kwargs)
        self.width = width
        self.height = height
        self.zoom = 50  # pixels per second
        self.offset_x = 50
        self.dragging = None
        self.scenes = []
        self.current_scene = None

        # Mouse events
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Double-Button-1>", self.on_double_click)

    def set_scenes(self, scenes):
        """Set the list of scenes to display."""
        self.scenes = scenes
        self.draw()

    def set_current_scene(self, scene):
        """Set the currently active scene."""
        self.current_scene = scene
        self.draw()

    def draw(self):
        """Redraw the timeline."""
        self.delete("all")

        # Background
        self.create_rectangle(0, 0, self.width, self.height, fill="#0a0a14")

        if not self.scenes:
            self.create_text(
                self.width / 2,
                self.height / 2,
                text="Keine Szenen vorhanden",
                fill="#333",
                font=("Arial", 12),
            )
            return

        # Draw time ruler
        total_duration = max((s.get("duration", 10) for s in self.scenes), default=10)

        self.create_line(
            self.offset_x, self.height - 30, self.width - 10, self.height - 30, fill="#444"
        )

        for t in range(0, int(total_duration) + 1):
            x = self.offset_x + t * self.zoom
            if x > self.width:
                break
            self.create_line(x, self.height - 30, x, self.height - 20, fill="#555")
            self.create_text(x, self.height - 12, text=f"{t}s", fill="#888", font=("Arial", 9))

        # Draw scenes as colored bars
        y_start = 20
        bar_height = 35

        for idx, scene in enumerate(self.scenes):
            x = (
                self.offset_x + (scene.get("start_time", idx * 10) / 10) * self.zoom
                if "start_time" in scene
                else self.offset_x + idx * 200
            )
            w = max(50, scene.get("duration", 10) * self.zoom)

            # Scene background
            color = self._scene_to_color(scene)
            self.create_rectangle(
                x,
                y_start,
                x + w,
                y_start + bar_height,
                fill=color,
                outline="#7c6ff5" if idx == self._get_current_idx() else "#333",
                width=2,
            )

            # Scene name
            self.create_text(
                x + w / 2,
                y_start + bar_height / 2,
                text=scene.get("name", f"Szene {idx + 1}"),
                fill="white",
                font=("Arial", 9, "bold"),
            )

            # Duration label
            self.create_text(
                x + w / 2,
                y_start + bar_height + 10,
                text=f"{scene.get('duration', 10):.1f}s",
                fill="#aaa",
                font=("Arial", 8),
            )

        # Draw keyframes for current scene
        if self.current_scene and self.current_scene.get("keyframes"):
            kf_y = y_start + bar_height + 30
            for kf in self.current_scene["keyframes"]:
                x = self.offset_x + kf["time"] * self.zoom
                color_hex = (
                    "#{:02x}{:02x}{:02x}".format(*kf["colors"][0]) if kf.get("colors") else "#fff"
                )

                # Diamond marker
                self.create_polygon(
                    x,
                    kf_y - 8,
                    x + 6,
                    kf_y,
                    x,
                    kf_y + 8,
                    x - 6,
                    kf_y,
                    fill=color_hex,
                    outline="white",
                    width=1,
                )

                # Time label
                self.create_text(
                    x, kf_y + 14, text=f"{kf['time']:.1f}s", fill="#ff0", font=("Arial", 8)
                )

        # Playhead if playing
        if getattr(self, "playing", False) and self.current_scene:
            play_x = self.offset_x + self.current_scene.get("play_time", 0) * self.zoom
            self.create_line(play_x, 0, play_x, self.height, fill="#ff0", width=2, dash=(4, 4))

    def _scene_to_color(self, scene):
        """Convert a scene to a background color."""
        if scene.get("keyframes"):
            first_kf = scene["keyframes"][0]
            if first_kf.get("colors"):
                r, g, b = first_kf["colors"][0]
                brightness = 0.15 + (r + g + b) / (255 * 3) * 0.15
                return f"#{int(30 * brightness):02x}{int(30 * brightness):02x}{int(60 * brightness):02x}"
        return "#1a1a3e"

    def _get_current_idx(self):
        """Get index of current scene."""
        for idx, s in enumerate(self.scenes):
            if s is self.current_scene or s.get("id") == self.current_scene.get("id"):
                return idx
        return -1

    def on_click(self, event):
        """Handle mouse click on timeline."""
        # Check if clicking on a scene
        y_start = 20
        bar_height = 35

        for idx, scene in enumerate(self.scenes):
            x = self.offset_x + idx * 200
            w = max(50, scene.get("duration", 10) * self.zoom)

            if x <= event.x <= x + w and y_start <= event.y <= y_start + bar_height:
                self.current_scene = scene
                self.dragging = "scene"
                return

        # Check if clicking on time ruler
        if event.y > self.height - 35:
            time = (event.x - self.offset_x) / self.zoom
            if time >= 0:
                self.dragging = "time"

    def on_drag(self, event):
        """Handle mouse drag."""
        if self.dragging == "scene":
            pass  # Could implement scene reordering

    def on_release(self, event):
        """Handle mouse release."""
        self.dragging = None

    def on_double_click(self, event):
        """Handle double click - add keyframe at time."""
        if event.y > self.height - 35:
            time = (event.x - self.offset_x) / self.zoom
            if time >= 0 and self.current_scene:
                return {
                    "action": "add_keyframe",
                    "time": round(time, 2),
                    "x": event.x,
                    "y": event.y,
                }
        return None

    def get_time_at_x(self, x):
        """Convert pixel X coordinate to time."""
        return max(0, (x - self.offset_x) / self.zoom)

    def start_preview(self):
        """Start timeline preview animation."""
        self.playing = True
        self._animate()

    def stop_preview(self):
        """Stop timeline preview."""
        self.playing = False
        self.draw()

    def _animate(self):
        """Animate the playhead."""
        if not getattr(self, "playing", False):
            return

        if self.current_scene:
            play_time = self.current_scene.get("play_time", 0) + 0.016
            duration = self.current_scene.get("duration", 10)

            # Loop handling
            loop_mode = self.current_scene.get("loop_mode", "single")
            if loop_mode == "endless":
                play_time = play_time % duration
            elif loop_mode == "pingpong":
                cycle = play_time % (duration * 2)
                if cycle > duration:
                    cycle = duration - (cycle - duration)
                play_time = cycle

            self.current_scene["play_time"] = play_time

        self.draw()
        self.after(16, self._animate)
