#!/usr/bin/env python3
"""NeoPulse Studio — ESP32 NeoPixel Controller & Show Editor."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.app import main

if __name__ == "__main__":
    main()
