# models/show.py -- Show data class (collection of scenes)
import uuid
from dataclasses import dataclass, field
from typing import List

from .scene import Scene


@dataclass
class Show:
    """A show containing multiple scenes."""

    id: str = field(default_factory=lambda: f"show_{uuid.uuid4().hex[:8]}")
    name: str = "Untitled Show"
    scenes: List[Scene] = field(default_factory=list)
    loop_mode: str = "endless"  # 'single', 'endless', 'pingpong'

    def add_scene(self, scene: Scene):
        """Add a scene to the show."""
        self.scenes.append(scene)

    def remove_scene(self, index: int):
        """Remove a scene by index."""
        if 0 <= index < len(self.scenes):
            self.scenes.pop(index)

    def get_total_duration(self) -> float:
        """Calculate total duration of all scenes."""
        return sum(s.duration for s in self.scenes)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "scenes": [
                {
                    "scene_id": s.id,
                    "transition": getattr(s, "transition", "instant"),
                    "duration": getattr(s, "transition_duration", 0),
                }
                for s in self.scenes
            ],
            "full_scenes": [s.to_dict() for s in self.scenes],
            "loop_mode": self.loop_mode,
        }

    @classmethod
    def from_dict(cls, data):
        show = cls(
            id=data.get("id", f"show_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", "Untitled Show"),
            loop_mode=data.get("loop_mode", "endless"),
        )
        show.scenes = [Scene.from_dict(s) for s in data.get("full_scenes", [])]
        return show

    def clone(self):
        show = Show(
            id=f"show_{uuid.uuid4().hex[:8]}",
            name=f"{self.name} (Copy)",
            loop_mode=self.loop_mode,
        )
        show.scenes = [s.clone() for s in self.scenes]
        return show

    def to_project_file(self):
        """Export as a .npulse project file."""
        return {
            "format": "neopulse-v1",
            "version": "1.0",
            "show": self.to_dict(),
        }

    @classmethod
    def from_project_file(cls, data):
        """Import from a .npulse project file."""
        if data.get("format") != "neopulse-v1":
            raise ValueError("Unsupported project file format")
        return cls.from_dict(data["show"])
