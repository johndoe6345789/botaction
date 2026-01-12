# Sketchfab to STL Converter

Python tools for converting Sketchfab 3D models to STL format.

## Overview

This project implements a complete pipeline for converting encrypted Sketchfab 3D models to STL (Stereolithography) format. The process involves:

1. **Fetching** - Download model files and encryption keys from Sketchfab
2. **Decrypting** - Decrypt `.binz` geometry files using AES-256-CBC
3. **Decoding** - Parse the OSGJS scene format and extract triangle geometry
4. **Exporting** - Generate binary STL files with calculated surface normals

## Project Structure

```
.
├── src/
│   ├── sketchfab_fetcher.py  # Fetch models from Sketchfab API
│   ├── model_decryptor.py    # AES-256-CBC decryption
│   ├── osgjs_decoder.py      # OSGJS scene format decoder
│   ├── binz_reader.py        # Binary geometry parser
│   ├── export_stl.py         # STL export with preview rendering
│   ├── cli.py                # Command-line interface
│   ├── sketchfab_gui.py      # GUI application
│   └── sketchfab_utils.py    # Utility functions
├── downloads/                 # Downloaded and exported models
├── docs/                      # Additional documentation
└── demos/                     # Demo scripts
```

## Quick Start

### Installation

```bash
pip install requests numpy pycryptodome matplotlib trimesh
```

### Convert a Sketchfab Model to STL

```bash
# Step 1: Fetch model files from Sketchfab
python -m src fetch "https://sketchfab.com/3d-models/model-name-abc123" --download

# Step 2: Export to STL
python -m src export \
    --osgjs downloads/model.osgjs.json \
    --geometry downloads/model_file.binz \
    --params downloads/model_params.json \
    --output model.stl

# Optional: Generate a preview image
python -m src export \
    --osgjs downloads/model.osgjs.json \
    --geometry downloads/model_file.binz \
    --params downloads/model_params.json \
    --output model.stl \
    --screenshot preview.png

# Recommended: Repair mesh for 3D printing (makes it watertight)
python -m src export \
    --osgjs downloads/model.osgjs.json \
    --geometry downloads/model_file.binz \
    --params downloads/model_params.json \
    --output model.stl \
    --repair --verbose
```

### GUI Application

```bash
python -m src.sketchfab_gui
```

## How It Works

The conversion pipeline has four stages:

### Stage 1: Fetching (sketchfab_fetcher.py)

Downloads model files from Sketchfab:

```python
from src.sketchfab_fetcher import SketchfabFetcher

fetcher = SketchfabFetcher()
result = fetcher.fetch_model("https://sketchfab.com/3d-models/model-name-abc123")
downloaded = fetcher.download_model_files(result['model_id'], output_dir='downloads')

# downloaded dict contains:
# 'binz': path to encrypted .binz file
# 'params': path to encryption params JSON
# 'model_file': path to model_file.binz
# 'wireframe': path to wireframe.binz (if available)
# 'thumbnail': path to thumbnail image
```

**What gets downloaded:**
- `.binz` files - Encrypted binary geometry
- `.osgjs.json` - Scene description (JSON)
- `_params.json` - Encryption parameters (Base64-encoded AES key + IV)
- `_metadata.json` - Model metadata from API

### Stage 2: Decryption (model_decryptor.py)

Decrypts the encrypted `.binz` files using AES-256-CBC:

```python
from src.model_decryptor import SketchfabDecryptor

decryptor = SketchfabDecryptor()
decrypted_data = decryptor.decrypt_and_decompress(
    'downloads/model_file.binz',
    encryption_params  # From _params.json
)
```

**Encryption details:**
- Algorithm: AES-256-CBC
- Key: Bytes 0-31 of Base64-decoded `b` parameter
- IV: Bytes 32-47 of Base64-decoded `b` parameter
- Padding: PKCS#7

### Stage 3: Decoding (osgjs_decoder.py)

Parses the OSGJS scene format to extract triangle geometry:

```python
from src.osgjs_decoder import decode_scene_to_triangles

# file_map uses just the base filename as the key
triangles, vertex_count = decode_scene_to_triangles(
    'downloads/model_id_file_uid.osgjs.json',
    {'model_file.binz': decrypted_geometry_data}
)
```

**OSGJS format:**
- Scene graph hierarchy with transformation matrices
- Geometry nodes containing vertex positions, normals, UVs, and indices
- Compression: delta encoding, varint encoding, implicit headers
- Primitive modes: TRIANGLES or TRIANGLE_STRIP

### Stage 4: STL Export (export_stl.py)

Converts triangles to binary STL format:

```python
from src.export_stl import ModelSTLExporter

exporter = ModelSTLExporter()
exporter.load_from_osgjs(
    'downloads/model_id_file_uid.osgjs.json',
    ['downloads/model_id_model_file.binz']
)
exporter.export_stl('output.stl')
exporter.render_preview('preview.png')  # Optional
```

**STL format:**
- 80-byte ASCII header
- 4-byte triangle count (little-endian uint32)
- For each triangle: normal vector (3 floats) + 3 vertices (9 floats) + attribute (2 bytes)

### Stage 5: Mesh Repair (optional)

The raw exported mesh may have artifacts or not be watertight (required for 3D printing). Use the `--repair` flag or call the repair method directly:

```python
from src.export_stl import ModelSTLExporter

exporter = ModelSTLExporter()
exporter.load_from_osgjs('model.osgjs.json', ['model_file.binz'])
exporter.repair(verbose=True)  # Fix mesh issues
exporter.export_stl('output.stl')

# Or combine in one call:
exporter.export_stl('output.stl', repair=True, verbose=True)
```

**Repair operations (using trimesh):**
- Merge duplicate vertices
- Remove degenerate/duplicate faces
- Fix face winding (consistent normals)
- Fill holes to make watertight
- Remove infinite values

## File Formats

| Format | Description | Contents |
|--------|-------------|----------|
| `.binz` | Encrypted geometry | AES-256-CBC encrypted binary vertex/index data |
| `.osgjs` | Scene description | JSON with scene graph, materials, buffer layouts |
| `_params.json` | Encryption keys | Base64-encoded AES key (32 bytes) + IV (16 bytes) |
| `.stl` | Output mesh | Binary STL with triangles and normals |

## Python API

### Full Pipeline Example

```python
from pathlib import Path
import json
from src.sketchfab_fetcher import SketchfabFetcher
from src.model_decryptor import SketchfabDecryptor
from src.export_stl import ModelSTLExporter

# 1. Fetch
fetcher = SketchfabFetcher()
result = fetcher.fetch_model("https://sketchfab.com/3d-models/...")
downloaded = fetcher.download_model_files(result['model_id'], 'downloads')

# 2. Decrypt the .binz file to create .osgjs.json
if 'binz' in downloaded and 'params' in downloaded:
    decryptor = SketchfabDecryptor()
    
    # Read params
    with open(downloaded['params'], 'r') as f:
        params = json.load(f)
    
    # Decrypt
    decrypted_data = decryptor.decrypt_file(downloaded['binz'], params)
    
    # Save as .osgjs.json
    osgjs_path = Path(downloaded['binz']).with_suffix('.osgjs.json')
    with open(osgjs_path, 'wb') as f:
        f.write(decrypted_data)
    
    # 3. Export to STL
    exporter = ModelSTLExporter()
    exporter.load_from_osgjs(
        str(osgjs_path),
        [downloaded['model_file']]
    )
    exporter.export_stl('output.stl')
```

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /v3/models/{id}` | Public model metadata |
| `GET /i/models/{id}` | Internal config with file URLs and encryption params |
| `GET /models/{id}/embed` | Embed page with viewer configuration |

## Limitations

- Some models have download restrictions set by authors
- API rate limits may apply
- Complex models with multiple geometry files may require manual handling

## License

For educational and research purposes only. Respect content creators' rights and Sketchfab's terms of service.
