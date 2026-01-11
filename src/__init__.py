"""
Sketchfab Model Fetcher and Viewer - Source Package

Main modules:
- binz_reader: Parse and read .binz 3D model files
- model_decryptor: Decrypt encrypted Sketchfab models
- model_viewer: 3D model viewer using PyQt6 and OpenGL
- sketchfab_fetcher: Fetch models from Sketchfab API
- sketchfab_gui: GUI application
- sketchfab_utils: Utility functions
- cli: Command-line interface
- export_3mf: Export models to 3MF format
"""

__version__ = "1.0.0"

# Main classes for easy importing
from .sketchfab_fetcher import SketchfabFetcher
from .model_decryptor import SketchfabDecryptor, decrypt_model
from .binz_reader import BinzReader
from .export_3mf import Model3MFExporter

__all__ = [
    'SketchfabFetcher',
    'SketchfabDecryptor', 
    'decrypt_model',
    'BinzReader',
    'Model3MFExporter',
    '__version__'
]
