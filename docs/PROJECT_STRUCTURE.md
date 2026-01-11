# Project Structure

This document describes the organization of the Sketchfab Utilities repository.

## Directory Layout

```
botaction/
├── src/                    # Main source code
│   ├── __init__.py        # Package initialization
│   ├── binz_reader.py     # Parse and read .binz binary 3D model files
│   ├── model_decryptor.py # Decrypt encrypted Sketchfab models (AES-256-CBC)
│   ├── model_viewer.py    # 3D model viewer using PyQt6 and OpenGL
│   ├── sketchfab_fetcher.py  # Fetch models from Sketchfab API
│   ├── sketchfab_gui.py   # Main GUI application
│   └── sketchfab_utils.py # Utility functions (color conversion, etc.)
│
├── tests/                  # Test scripts
│   ├── create_test_models.py   # Generate test 3D models
│   ├── test_decrypt.py         # Test decryption functionality
│   ├── test_decrypt2.py        # Additional decryption tests
│   ├── test_model_loading.py   # Test model loading
│   └── test_viewer.py          # Test 3D viewer
│
├── demos/                  # Demonstration scripts
│   ├── demo_decryption.py # Demonstrate model decryption
│   └── demo_viewer.py     # Demonstrate 3D viewer
│
├── scripts/                # Utility scripts
│   ├── export_3mf.py      # Export models to 3MF format
│   └── inspect_model.py   # Inspect .binz file structure
│
├── docs/                   # Documentation
│   ├── DECRYPTION_ANALYSIS.md  # Analysis of encryption scheme
│   ├── QUICK_REFERENCE.md      # Quick reference guide
│   ├── SOLUTION_SUMMARY.md     # Summary of decryption solution
│   ├── VIEWER_COMPLETE.md      # 3D viewer documentation
│   ├── VIEWER_GUIDE.md         # Guide for using the viewer
│   └── VIEWER_STATUS.md        # Status of viewer implementation
│
├── data/                   # Data files
│   ├── downloaded_model.binz   # Downloaded model data
│   ├── model_file.binz         # Model file
│   ├── model_data.json         # Model metadata
│   └── embed_page.html         # HTML embed page
│
├── downloads/              # Downloaded models and assets
│   ├── *.binz             # Model geometry files
│   ├── *_params.json      # Encryption parameters
│   ├── *.3mf              # Exported 3MF files
│   └── *_thumbnail.jpeg   # Model thumbnails
│
├── README.md              # Main project README
├── url.txt                # Reference URLs
└── repomix-output-jsfiles.zip.xml  # Archive reference
```

## Usage Patterns

### Running the GUI Application

```bash
# From project root
python -m src.sketchfab_gui
```

### Running Tests

```bash
# Run all tests
python tests/test_model_loading.py
python tests/test_decrypt.py
python tests/test_viewer.py
```

### Running Demos

```bash
# Demonstrate decryption
python demos/demo_decryption.py

# Demonstrate 3D viewer
python demos/demo_viewer.py
```

### Using as a Module

```python
# Import from src package
from src.binz_reader import BinzReader
from src.model_decryptor import SketchfabDecryptor
from src.sketchfab_fetcher import SketchfabFetcher
```

## Import Conventions

- **Source files in `src/`**: Use relative imports (e.g., `from .binz_reader import ...`)
- **Test/demo files**: Use absolute imports with parent path added (e.g., `from src.binz_reader import ...`)
- **Scripts**: Use absolute imports with parent path added

## Key Files

| File | Purpose |
|------|---------|
| [src/sketchfab_gui.py](src/sketchfab_gui.py) | Main GUI application - start here |
| [src/binz_reader.py](src/binz_reader.py) | Core binary parsing logic |
| [src/model_decryptor.py](src/model_decryptor.py) | Encryption/decryption implementation |
| [docs/SOLUTION_SUMMARY.md](docs/SOLUTION_SUMMARY.md) | Complete decryption documentation |
| [README.md](README.md) | Project overview and quick start |

## Development Notes

- Source code is organized in the `src/` package
- Tests are isolated in `tests/` directory
- Documentation is centralized in `docs/`
- All downloaded/generated files go to `downloads/`
- Sample data files are in `data/`

## Dependencies

```bash
pip install requests numpy pycryptodome PyQt6 PyOpenGL
```

See [README.md](README.md) for full installation and usage instructions.
