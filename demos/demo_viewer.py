#!/usr/bin/env python
"""
Demo: Load and display a 3D model programmatically
"""

import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

from src.model_viewer import ModelViewerPanel


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Model Viewer Demo")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Instructions
        info = QLabel(
            "<h3>3D Model Viewer Demo</h3>"
            "<p><b>Controls:</b></p>"
            "<ul>"
            "<li>Left Click + Drag: Rotate model</li>"
            "<li>Mouse Wheel: Zoom in/out</li>"
            "<li>Load Model: Load .binz file from downloads/</li>"
            "<li>Toggle Wireframe: Switch rendering mode</li>"
            "<li>Reset View: Return to default camera position</li>"
            "</ul>"
        )
        info.setStyleSheet("background-color: #2a2a2a; padding: 10px; border-radius: 4px;")
        layout.addWidget(info)
        
        # Viewer
        self.viewer = ModelViewerPanel()
        layout.addWidget(self.viewer)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("3D Model Viewer Demo")
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
