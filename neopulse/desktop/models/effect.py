# models/effect.py -- Effect data class and definitions
from dataclasses import dataclass, field
from typing import Any, Dict, List

EFFECT_TYPES = {
    "strobe": {
        "name": "Strobe",
        "description": "Flash light with configurable frequency and color",
        "params": [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.1,
                "max": 20.0,
                "default": 3.0,
                "label": "Frequency (Hz)",
            },
            {"name": "color", "type": "rgb", "default": [255, 255, 255], "label": "Color"},
        ],
    },
    "fire": {
        "name": "Fire",
        "description": "Fire/flame effect with configurable intensity",
        "params": [
            {
                "name": "intensity",
                "type": "float",
                "min": 0.1,
                "max": 1.0,
                "default": 1.0,
                "label": "Intensity",
            },
        ],
    },
    "emergency_us": {
        "name": "Emergency (US)",
        "description": "US emergency vehicle pattern (Red/Blue alternating)",
        "params": [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.5,
                "max": 10.0,
                "default": 2.0,
                "label": "Frequency (Hz)",
            },
            {"name": "color_red", "type": "rgb", "default": [255, 0, 0], "label": "Red Color"},
            {"name": "color_blue", "type": "rgb", "default": [0, 0, 255], "label": "Blue Color"},
        ],
    },
    "emergency_de": {
        "name": "Blaulicht (DE)",
        "description": "German emergency vehicle pattern (Blue flashing)",
        "params": [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.5,
                "max": 5.0,
                "default": 1.5,
                "label": "Frequency (Hz)",
            },
            {"name": "color_blue", "type": "rgb", "default": [0, 0, 255], "label": "Blue Color"},
        ],
    },
    "rainbow": {
        "name": "Rainbow",
        "description": "Rainbow wave effect across all pixels",
        "params": [
            {
                "name": "speed",
                "type": "float",
                "min": 0.1,
                "max": 5.0,
                "default": 1.0,
                "label": "Speed",
            },
        ],
    },
    "breathing": {
        "name": "Breathing",
        "description": "Smooth fade in/out effect",
        "params": [
            {
                "name": "frequency",
                "type": "float",
                "min": 0.1,
                "max": 3.0,
                "default": 0.5,
                "label": "Frequency (Hz)",
            },
            {"name": "color", "type": "rgb", "default": [255, 255, 255], "label": "Color"},
        ],
    },
}


@dataclass
class Effect:
    """An effect that can be applied between keyframes."""

    type: str = "strobe"
    params: Dict[str, Any] = field(default_factory=dict)
    duration: float = 5.0  # Duration in seconds

    def to_dict(self):
        return {
            "type": self.type,
            "params": self.params,
            "duration": self.duration,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            type=data.get("type", "strobe"),
            params=data.get("params", {}),
            duration=data.get("duration", 5.0),
        )

    def get_schema(self) -> List[Dict]:
        """Get the parameter schema for this effect."""
        effect_info = EFFECT_TYPES.get(self.type, {})
        return effect_info.get("params", [])

    def get_name(self) -> str:
        """Get the display name of this effect."""
        effect_info = EFFECT_TYPES.get(self.type, {})
        return effect_info.get("name", self.type)
