# models/scene.py -- Scene data class
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from .keyframe import Keyframe


@dataclass
class Scene:
    """A scene containing keyframes and animation settings."""

    id: str = field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:8]}")
    name: str = "Untitled Scene"
    keyframes: List[Keyframe] = field(default_factory=list)
    interpolation: str = "linear"  # Default interpolation mode
    loop_mode: str = "single"  # 'single', 'endless', 'pingpong'
    duration: float = 10.0  # Total duration in seconds
    brightness: int = 100  # 0-100%

    def add_keyframe(self, kf: Keyframe):
        """Add a keyframe and maintain time order."""
        self.keyframes.append(kf)
        self.keyframes.sort(key=lambda k: k.time)
        self._update_duration()

    def remove_keyframe(self, index: int):
        """Remove a keyframe by index."""
        if 0 <= index < len(self.keyframes):
            self.keyframes.pop(index)
            self._update_duration()

    def get_keyframe_at_time(self, time: float) -> Optional[Keyframe]:
        """Find the keyframe closest to the given time."""
        for kf in self.keyframes:
            if abs(kf.time - time) < 0.1:
                return kf
        return None

    def _update_duration(self):
        """Update duration based on last keyframe."""
        if self.keyframes:
            self.duration = max(self.duration, self.keyframes[-1].time + 2.0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "keyframes": [kf.to_dict() for kf in self.keyframes],
            "interpolation": self.interpolation,
            "loop_mode": self.loop_mode,
            "duration": self.duration,
            "brightness": self.brightness,
        }

    @classmethod
    def from_dict(cls, data):
        scene = cls(
            id=data.get("id", f"scene_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", "Untitled Scene"),
            interpolation=data.get("interpolation", "linear"),
            loop_mode=data.get("loop_mode", "single"),
            duration=data.get("duration", 10.0),
            brightness=data.get("brightness", 100),
        )
        scene.keyframes = [Keyframe.from_dict(kf) for kf in data.get("keyframes", [])]
        return scene

    def clone(self):
        scene = Scene(
            id=f"scene_{uuid.uuid4().hex[:8]}",
            name=f"{self.name} (Copy)",
            interpolation=self.interpolation,
            loop_mode=self.loop_mode,
            duration=self.duration,
            brightness=self.brightness,
        )
        scene.keyframes = [kf.clone() for kf in self.keyframes]
        return scene
