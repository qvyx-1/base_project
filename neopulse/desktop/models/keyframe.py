# models/keyframe.py -- Keyframe data class
from dataclasses import dataclass, field
from typing import List


@dataclass
class Keyframe:
    """A single keyframe with time and pixel colors."""

    time: float = 0.0  # Time in seconds from scene start
    colors: List[tuple] = field(default_factory=list)  # RGB tuples for each pixel
    interpolation: str = "linear"  # 'linear', 'sine', 'step', 'ease_in_out'

    def to_dict(self):
        return {
            "time": self.time,
            "colors": self.colors,
            "interpolation": self.interpolation,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            time=data.get("time", 0.0),
            colors=data.get("colors", []),
            interpolation=data.get("interpolation", "linear"),
        )

    def clone(self):
        return Keyframe(
            time=self.time,
            colors=[tuple(c) for c in self.colors],
            interpolation=self.interpolation,
        )
