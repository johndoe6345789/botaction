# Sketchfab Utilities

Python tools for working with Sketchfab 3D models and their file formats.

## Files

| File | Description |
|------|-------------|
| `sketchfab_gui.py` | PyQt6 GUI application for fetching and analyzing models |
| `sketchfab_fetcher.py` | Fetch model metadata, file URLs, and download assets from Sketchfab |
| `binz_reader.py` | Parse and analyze `.binz` binary geometry files |
| `sketchfab_utils.py` | Ported utilities from Sketchfab's JS codebase (color conversion, etc.) |

## Installation

```bash
pip install requests numpy pycryptodome PyQt6
```

## GUI Application

Launch the graphical interface:

```bash
python sketchfab_gui.py
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
from sketchfab_fetcher import SketchfabFetcher

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
python sketchfab_fetcher.py
```

This will fetch the example model and save:
- `model_data.json` - Full API response and metadata
- `downloads/*.binz` - Encrypted model geometry
- `downloads/*_params.json` - Encryption parameters
- `downloads/*_thumbnail.jpeg` - Model preview image

### Analyze a .binz File

```python
from binz_reader import BinzReader, inspect_binz

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
from sketchfab_utils import linear_to_srgb, srgb_to_linear

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
