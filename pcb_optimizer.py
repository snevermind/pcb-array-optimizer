#!/usr/bin/env python3
"""
PCB Array Optimizer - Application Launcher
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.main import main

if __name__ == "__main__":
    main()
