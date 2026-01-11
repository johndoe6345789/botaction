#!/usr/bin/env python
"""
Test script for the 3D model viewer
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from model_viewer import ModelViewerPanel


def main():
    app = QApplication(sys.argv)
    
    # Create viewer
    viewer = ModelViewerPanel()
    viewer.setWindowTitle("3D Model Viewer Test")
    viewer.resize(800, 600)
    viewer.show()
    
    # Auto-load model if available
    viewer.load_model_from_downloads()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
