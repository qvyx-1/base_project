# esp/__init__.py -- ESP32 communication module for NeoPulse Studio
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from desktop.esp.connection import ESPConnection
from desktop.esp.flasher import ESPFlasher

__all__ = ["ESPConnection", "ESPFlasher"]
