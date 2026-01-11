#!/usr/bin/env python3
"""
Sketchfab Model Tools - Main entry point

Run with: python -m src
"""

import sys
from pathlib import Path

# Add parent directory to path to import cli
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import main

if __name__ == '__main__':
    main()