# Sketchfab Utilities

✅ **Successfully reverse-engineered and decrypted Sketchfab model encryption!**

Python tools for working with Sketchfab 3D models and their file formats.

## 🎉 Major Achievement

**Decryption Working!** Successfully implemented AES-256-CBC decryption for Sketchfab's encrypted `.binz` files.

- ✅ Full decryption implementation
- ✅ Working demo with Annihilator 2000 model  
- ✅ Raw geometry data extraction
- 📚 Complete documentation in [docs/SOLUTION_SUMMARY.md](docs/SOLUTION_SUMMARY.md)

## Project Structure

```
.
├── src/              # Main source code
│   ├── binz_reader.py         # Parse .binz binary files
│   ├── model_decryptor.py     # Decrypt Sketchfab models
│   ├── model_viewer.py        # 3D viewer (PyQt6 + OpenGL)
│   ├── sketchfab_fetcher.py   # Fetch from Sketchfab API
│   ├── sketchfab_gui.py       # GUI application
│   └── sketchfab_utils.py     # Utility functions
├── tests/            # Test scripts
├── demos/            # Demo scripts
├── scripts/          # Utility scripts
├── docs/             # Documentation
├── data/             # Data files
└── downloads/        # Downloaded models
```

## Quick Start

```bash
# Install dependencies
pip install requests numpy pycryptodome PyQt6

# Launch GUI application
python -m src.sketchfab_gui

# Or run demos
python demos/demo_decryption.py
```

## GUI Application

Launch the graphical interface:

```bash
python -m src.sketchfab_gui
```

Features:
- Enter any Sketchfab model URL to fetch metadata
- View model info: name, author, views, likes, face/vertex count
- See encryption details and key material
- Browse file URLs and sizes
- Download model files and thumbnails
- Dark theme UI

## Usage

### Fetch a Model

```python
from src.sketchfab_fetcher import SketchfabFetcher

fetcher = SketchfabFetcher()

# Fetch model data
result = fetcher.fetch_model("https://sketchfab.com/3d-models/model-name-abc123...")

# Get model info
print(result['api_data']['name'])
print(result['api_data']['user']['username'])

# Download files
downloaded = fetcher.download_model_files(result['model_id'], output_dir='downloads')
```

### Command Line

```bash
python -m src.sketchfab_fetcher
```

This will fetch the example model and save:
- `model_data.json` - Full API response and metadata
- `downloads/*.binz` - Encrypted model geometry
- `downloads/*_params.json` - Encryption parameters
- `downloads/*_thumbnail.jpeg` - Model preview image

### Analyze a .binz File

```python
from src.binz_reader import BinzReader, inspect_binz

# Inspect file structure
info = inspect_binz('model.binz')
print(info['size_bytes'])
print(info['sample_floats'])

# Read with layout from .osgjs
reader = BinzReader()
data = reader.read_file('model.binz')
geometry = reader.parse_geometry(data, layout)
```

### Color Space Conversion

```python
from src.sketchfab_utils import linear_to_srgb, srgb_to_linear

# Convert linear color to sRGB
srgb_value = linear_to_srgb(0.5)

# Convert RGB tuple
r, g, b = linear_to_srgb_rgb(0.2, 0.4, 0.6)
```

## Sketchfab File Format

### .binz Files

Sketchfab stores 3D model geometry in encrypted `.binz` files:

| Property | Description |
|----------|-------------|
| Format | AES-encrypted binary data |
| Compression | May be zlib-compressed after decryption |
| Contents | Vertex positions, normals, UVs, indices |

### Encryption

Models are protected with encryption:

```
File Config (from API):
├── osgjsUrl: URL to the .binz file
├── modelSize: Uncompressed geometry size
├── osgjsSize: Scene description size
└── p[]: Encryption parameters
    ├── v: Version (usually 1)
    ├── d: true = encrypted
    └── b: Base64 key material
        ├── bytes 0-31: AES-256 key
        ├── bytes 32-47: IV/nonce
        └── bytes 48+: Additional params
```

### .osgjs Files

Scene description files (JSON) that define:
- Scene graph hierarchy
- Material definitions
- Buffer layouts and offsets
- Texture references

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /i/models/{id}` | Internal model config with file URLs |
| `GET /v3/models/{id}` | Public API model metadata |
| `GET /models/{id}/embed` | Embed page with viewer config |

## Limitations

- Model geometry files are encrypted
- Decryption requires reverse-engineering the osgjs viewer
- Some models are not downloadable per author settings
- API rate limits may apply

## License

For educational and research purposes only. Respect content creators' rights.
