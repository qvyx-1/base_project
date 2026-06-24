# animation_engine.py -- Keyframe-based animation engine for NeoPulse
import asyncio
import math
import time


class AnimationEngine:
    """Manages keyframe-based animations with interpolation."""

    def __init__(self, driver):
        self.driver = driver
        self.current_scene = None
        self.start_time = 0
        self.running = False
        self._task = None

    async def play_scene(self, scene):
        """Play a scene definition. Blocks until scene completes or is stopped."""
        self.current_scene = scene
        self.start_time = time.ticks_ms()
        self.running = True

        duration = scene.get("duration", 10.0) * 1000  # Convert to ms

        while self.running:
            elapsed = time.ticks_diff(time.ticks_ms(), self.start_time)

            # Handle loop modes
            loop_mode = scene.get("loop_mode", "single")
            if loop_mode == "endless":
                elapsed = elapsed % duration
            elif loop_mode == "pingpong":
                cycle = elapsed % (duration * 2)
                if cycle > duration:
                    cycle = duration - (cycle - duration)
                elapsed = cycle

            if elapsed >= duration:
                if loop_mode == "single":
                    break
                else:
                    self.start_time = time.ticks_ms()
                    continue

            # Calculate colors from keyframes
            colors = self._get_frame_colors(scene, elapsed / 1000.0)

            # Apply brightness
            brightness = scene.get("brightness", 100) / 100.0
            if brightness < 1.0:
                colors = [
                    (int(c[0] * brightness), int(c[1] * brightness), int(c[2] * brightness))
                    for c in colors
                ]

            self.driver.set_all_colors(colors)
            self.driver.write()

            await asyncio.sleep(0.016)  # ~60 FPS

    def stop(self):
        """Stop the current animation."""
        self.running = False

    def _get_frame_colors(self, scene, elapsed_time):
        """Calculate colors at a given time from keyframes."""
        keyframes = scene.get("keyframes", [])

        if not keyframes:
            return [(0, 0, 0)] * self.driver.num_pixels

        # Before first keyframe
        if elapsed_time <= keyframes[0]["time"]:
            return list(keyframes[0]["colors"])

        # After last keyframe
        if elapsed_time >= keyframes[-1]["time"]:
            return list(keyframes[-1]["colors"])

        # Find surrounding keyframes
        for i in range(len(keyframes) - 1):
            kf_start = keyframes[i]
            kf_end = keyframes[i + 1]

            if kf_start["time"] <= elapsed_time <= kf_end["time"]:
                duration = kf_end["time"] - kf_start["time"]
                t = (elapsed_time - kf_start["time"]) / max(0.001, duration)

                # Apply interpolation mode
                interp = scene.get("interpolation", "linear")
                if interp == "sine":
                    t = math.sin(t * math.pi / 2)
                elif interp == "step":
                    t = 1.0 if t > 0.5 else 0.0
                elif interp == "ease_in_out":
                    t = self._ease_in_out(t)

                # Interpolate each pixel
                colors = []
                for j in range(self.driver.num_pixels):
                    c1 = kf_start["colors"][j] if j < len(kf_start["colors"]) else (0, 0, 0)
                    c2 = kf_end["colors"][j] if j < len(kf_end["colors"]) else (0, 0, 0)
                    colors.append(self._interpolate_color(c1, c2, t))

                return colors

        return [(0, 0, 0)] * self.driver.num_pixels

    @staticmethod
    def _interpolate_color(c1, c2, t):
        """Interpolate between two RGB colors."""
        t = max(0, min(1, t))
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    @staticmethod
    def _ease_in_out(t):
        """Ease in-out function: smooth S-curve."""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - math.pow(-2 * t + 2, 2) / 2

    @staticmethod
    def generate_gradient_colors(num_pixels, c1, c2):
        """Generate a list of gradient colors."""
        colors = []
        for i in range(num_pixels):
            t = i / max(1, num_pixels - 1)
            colors.append(AnimationEngine._interpolate_color(c1, c2, t))
        return colors
