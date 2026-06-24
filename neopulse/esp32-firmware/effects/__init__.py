# effects/__init__.py -- Effect registry for NeoPulse
from .breathing import BreathingEffect
from .emergency_de import EmergencyDEEffect
from .emergency_us import EmergencyUSEffect
from .fire import FireEffect
from .rainbow import RainbowEffect
from .strobe import StrobeEffect

# Registry of all available effects
EFFECTS = {
    "strobe": StrobeEffect,
    "fire": FireEffect,
    "emergency_us": EmergencyUSEffect,
    "emergency_de": EmergencyDEEffect,
    "rainbow": RainbowEffect,
    "breathing": BreathingEffect,
}


def get_effect(name):
    """Get an effect class by name."""
    cls = EFFECTS.get(name)
    if cls is None:
        raise ValueError(f"Unknown effect: {name}. Available: {list(EFFECTS.keys())}")
    return cls


def list_effects():
    """List all available effects with descriptions."""
    return {
        "strobe": {
            "name": "Strobe",
            "description": "Flash light with configurable frequency and color",
            "params": ["frequency", "color"],
        },
        "fire": {
            "name": "Fire",
            "description": "Fire/flame effect with configurable intensity",
            "params": ["intensity"],
        },
        "emergency_us": {
            "name": "Emergency (US)",
            "description": "US emergency vehicle pattern (Red/Blue alternating)",
            "params": ["frequency"],
        },
        "emergency_de": {
            "name": "Blaulicht (DE)",
            "description": "German emergency vehicle pattern (Blue flashing)",
            "params": ["frequency"],
        },
        "rainbow": {
            "name": "Rainbow",
            "description": "Rainbow wave effect across all pixels",
            "params": ["speed"],
        },
        "breathing": {
            "name": "Breathing",
            "description": "Smooth fade in/out effect",
            "params": ["frequency", "color"],
        },
    }
