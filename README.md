# Sketchfab to STL Converter

Python tools for converting Sketchfab 3D models to STL format.

## Overview

This project implements a complete pipeline for converting compressed Sketchfab 3D models to STL (Stereolithography) format. The process involves:

1. **Fetching** - Download model files and compression keys from Sketchfab
2. **DITER Decoding** - Decompress `.binz` files using Sketchfab's DITER codec
3. **Parsing** - Parse the OSGJS scene format and extract triangle geometry
4. **Exporting** - Generate binary STL files with calculated surface normals

### Key Features

- Downloads models directly from Sketchfab URLs
- Handles DITER compression (proprietary LZ-based codec)
- Supports multiple DITER decoders (Node.js recommended, Python/C available)
- Mesh repair for 3D printing (makes models watertight)
- Export to STL or 3MF formats
- Command-line interface with extensive utilities
- Web scraping and API tools

## Project Structure

```
.
├── src/
│   ├── sketchfab_fetcher.py  # Fetch models from Sketchfab API
│   ├── model_decryptor.py    # AES-256-CBC decryption
│   ├── diter_decoder.py      # DITER decompression (Python)
│   ├── osgjs_decoder.py      # OSGJS scene format decoder
│   ├── binz_reader.py        # Binary geometry parser
│   ├── export_stl.py         # STL export with preview rendering
│   ├── export_3mf.py         # 3MF export
│   ├── cli.py                # Command-line interface
│   ├── sketchfab_gui.py      # GUI application
│   └── sketchfab_utils.py    # Utility functions
├── archive/diter/             # DITER decoder research & implementations
├── downloads/                 # Downloaded and exported models
├── docs/                      # Additional documentation
└── download_model.py          # Simple download & convert script
```

## Working Example

Successfully converted **Annihilator 2000** model:
- Model ID: `dea4f17e94974e1fa720cbadc531ed63`
- Input: DITER-compressed `.binz` files (582 KB + 67 KB)
- Output: `annihilator_2000_SUCCESS.stl` (4.7 MB)
- Result: 82,819 vertices, 97,674 triangles

The key discovery: `model_file.binz` requires DITER decoding, NOT AES decryption!

## Quick Start

### Installation

**Required Dependencies:**
```bash
pip install requests pycryptodome trimesh beautifulsoup4 networkx lxml
```

**For DITER Decoding (choose one):**
- **Node.js** (recommended): Install [Node.js](https://nodejs.org/)
- **Python** (slow): `pip install pywasm`
- **C** (fast): Build from source (requires cmake and LLVM)

### Simple Download & Convert

Use the included `download_model.py` script:

```bash
# Download model files
python download_model.py

# Decode scene description (DITER)
node scripts/diter_decode.js \
    --binz downloads/[model_id]_[file_uid].binz \
    --params downloads/[model_id]_[file_uid]_params.json \
    --out downloads/[model_id]_[file_uid].osgjs.json

# Decode geometry file (DITER)
node scripts/diter_decode.js \
    --binz downloads/[model_id]_model_file.binz \
    --params downloads/[model_id]_[file_uid]_params.json \
    --out model_file_decoded.bin

# Export to STL (Python)
python -c "
from pathlib import Path
from src.export_stl import ModelSTLExporter
from src.osgjs_decoder import decode_scene_to_triangles

data = Path('model_file_decoded.bin').read_bytes()
file_map = {'model_file.binz': data}
osgjs_path = Path('downloads/[model_id]_[file_uid].osgjs.json')

triangles, vertex_count = decode_scene_to_triangles(osgjs_path, file_map)
exporter = ModelSTLExporter()
exporter.triangles = triangles
exporter.vertex_count = vertex_count
exporter.export_stl('output.stl', repair=False)
print(f'Exported {vertex_count:,} vertices, {len(triangles):,} triangles')
"
```

### Using the CLI

```bash
# Download model files
python cli.py fetch "https://sketchfab.com/3d-models/model-name-abc123" --download

# Scrape model page for information
python cli.py scrape "https://sketchfab.com/3d-models/model-name-abc123" --save-html page.html

# Get model statistics
python cli.py stats abc123

# Search for models
python cli.py search "robot" --max-results 10

# View all available commands
python cli.py --help
```

### CLI Tools

The project includes a comprehensive CLI with 40+ commands:

```bash
# View all available commands
python cli.py --help

# Search for models
python cli.py search "robot" --max-results 10

# Get model information
python cli.py info dea4f17e94974e1fa720cbadc531ed63

# Scrape model page
python cli.py scrape "https://sketchfab.com/3d-models/..." --save-html page.html

# Parse Sketchfab URLs
python cli.py parse-url "https://sketchfab.com/3d-models/model-name-abc123"

# Get thumbnail URLs
python cli.py thumbnail abc123

# Display license information
python cli.py licenses

# And many more utilities...
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
# 'binz': path to DITER-compressed .binz file (scene description)
# 'params': path to compression params JSON
# 'model_file': path to model_file.binz (geometry buffers)
# 'wireframe': path to wireframe.binz (if available)
# 'thumbnail': path to thumbnail image
```

**What gets downloaded:**
- Main `.binz` file - DITER-compressed scene description
- `model_file.binz` - DITER-compressed geometry buffers
- `_params.json` - Compression parameters (Base64-encoded DITER keys)
- `_metadata.json` - Model metadata from API

### Stage 2: DITER Decoding

**CRITICAL:** Both the main `.binz` file AND `model_file.binz` require DITER decoding!

The `params.json` file with `"d": true` indicates DITER compression, not AES encryption.

**Decode scene description:**
```bash
node scripts/diter_decode.js \
    --binz downloads/model_id_file_uid.binz \
    --params downloads/model_id_file_uid_params.json \
    --out downloads/model_id_file_uid.osgjs.json
```

**Decode geometry buffers:**
```bash
node scripts/diter_decode.js \
    --binz downloads/model_id_model_file.binz \
    --params downloads/model_id_file_uid_params.json \
    --out model_file_decoded.bin
```

**DITER Details:**
- Proprietary LZ-based compression codec by Sketchfab
- Uses WebAssembly for decompression
- ~253 KB WASM binary with obfuscated function names (Rick Roll themed!)
- Requires both WASM module and decryption keys
- Node.js decoder is fastest and most reliable

### Stage 3: Parsing (osgjs_decoder.py)

Parses the OSGJS scene format to extract triangle geometry:

```python
from pathlib import Path
from src.osgjs_decoder import decode_scene_to_triangles

# Load DITER-decoded geometry
geometry_data = Path('model_file_decoded.bin').read_bytes()

# file_map uses just the base filename as the key
file_map = {'model_file.binz': geometry_data}

triangles, vertex_count = decode_scene_to_triangles(
    'downloads/model_id_file_uid.osgjs.json',
    file_map
)
```

**OSGJS format:**
- Scene graph hierarchy with transformation matrices
- Geometry nodes containing vertex positions, normals, UVs, and indices
- Data encoding: delta encoding, varint encoding, implicit headers
- Primitive modes: TRIANGLES or TRIANGLE_STRIP
- References geometry buffers by filename (e.g., "model_file.binz")

### Stage 4: STL Export (export_stl.py)

Converts triangles to binary STL format:

```python
from pathlib import Path
from src.export_stl import ModelSTLExporter
from src.osgjs_decoder import decode_scene_to_triangles

# Load decoded geometry
geometry_data = Path('model_file_decoded.bin').read_bytes()
file_map = {'model_file.binz': geometry_data}

# Decode triangles
triangles, vertex_count = decode_scene_to_triangles(
    'downloads/model.osgjs.json',
    file_map
)

# Export
exporter = ModelSTLExporter()
exporter.triangles = triangles
exporter.vertex_count = vertex_count
exporter.export_stl('output.stl', repair=False)
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
| `.binz` | DITER-compressed | Proprietary LZ-based compression of scene/geometry data |
| `model_file.binz` | DITER-compressed geometry | Raw vertex buffers (positions, normals, UVs, indices) |
| `.osgjs.json` | Scene description | JSON with scene graph, materials, buffer references |
| `_params.json` | Compression keys | Base64-encoded DITER decryption parameters |
| `.stl` | Output mesh | Binary STL with triangles and normals |

### DITER Decoding

Sketchfab uses **DITER**, a proprietary LZ-based compression codec (NOT AES encryption).

**Important:** Both the main `.binz` file AND `model_file.binz` require DITER decoding!

**Decoding Options:**

1. **Node.js** (recommended): `node scripts/diter_decode.js`
   - Requires: Node.js installed
   - Performance: Fast, reliable
   - Best for: All use cases
   - Usage:
     ```bash
     node scripts/diter_decode.js \
         --binz input.binz \
         --params params.json \
         --out output.bin
     ```

2. **Python** (slow): `from src.diter_decoder import decode_diter_file`
   - Requires: `pip install pywasm`
   - Performance: Very slow (5-10+ minutes for large models)
   - Best for: Understanding the algorithm

3. **C** (fast): Compile from `archive/diter/src/diter_decode_c.cc`
   - Requires: cmake, LLVM
   - Performance: ~100x faster than Python
   - Best for: Production environments

**DITER Architecture:**
- WebAssembly-based decompressor (~253 KB)
- Obfuscated function names (Rick Astley lyrics in Base64!)
- LZ77-style dictionary compression + Huffman coding
- Decryption keys embedded in JavaScript bundles

## Python API

### Full Pipeline Example

```python
import subprocess
from pathlib import Path
from src.sketchfab_fetcher import SketchfabFetcher
from src.export_stl import ModelSTLExporter
from src.osgjs_decoder import decode_scene_to_triangles

# 1. Fetch model files
fetcher = SketchfabFetcher()
result = fetcher.fetch_model("https://sketchfab.com/3d-models/...")
downloaded = fetcher.download_model_files(result['model_id'], 'downloads')

print(f"Downloaded files: {list(downloaded.keys())}")

# 2. DITER decode the scene description (main .binz → .osgjs.json)
model_id = result['model_id']
osgjs_files = list(Path('downloads').glob(f'{model_id}*.osgjs.json'))

if not osgjs_files:
    # Use Node.js decoder (fastest, most reliable)
    binz_path = Path(downloaded['binz'])
    params_path = Path(downloaded['params'])
    osgjs_path = binz_path.with_suffix('.osgjs.json')

    subprocess.run([
        'node', 'scripts/diter_decode.js',
        '--binz', str(binz_path),
        '--params', str(params_path),
        '--out', str(osgjs_path)
    ], check=True)
    print(f"Decoded scene to {osgjs_path}")
else:
    osgjs_path = osgjs_files[0]

# 3. DITER decode the geometry file (model_file.binz → decoded.bin)
if 'model_file' in downloaded:
    model_file_path = Path(downloaded['model_file'])
    decoded_geom = Path('model_file_decoded.bin')

    subprocess.run([
        'node', 'scripts/diter_decode.js',
        '--binz', str(model_file_path),
        '--params', str(params_path),
        '--out', str(decoded_geom)
    ], check=True)
    print(f"Decoded geometry to {decoded_geom}")

    # 4. Parse and export to STL
    geometry_data = decoded_geom.read_bytes()
    file_map = {'model_file.binz': geometry_data}

    triangles, vertex_count = decode_scene_to_triangles(osgjs_path, file_map)

    exporter = ModelSTLExporter()
    exporter.triangles = triangles
    exporter.vertex_count = vertex_count
    exporter.export_stl('output.stl', repair=False)

    print(f"✓ Exported {vertex_count:,} vertices, {len(triangles):,} triangles")
```

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /v3/models/{id}` | Public model metadata |
| `GET /i/models/{id}` | Internal config with file URLs and encryption params |
| `GET /models/{id}/embed` | Embed page with viewer configuration |

## Troubleshooting

### "ValueError: Varint decode error"
- **Cause:** Trying to decrypt `model_file.binz` with AES instead of DITER decoding
- **Solution:** Use DITER decoder on `model_file.binz`, not AES decryption
- Both the main `.binz` AND `model_file.binz` require DITER decoding!

### "File size not aligned to 16 bytes"
- **Cause:** Old code attempted AES decryption on DITER-compressed files
- **Solution:** This is expected - files are DITER-compressed, not AES-encrypted
- Ignore this warning if using the Node.js decoder

### "ModuleNotFoundError: No module named 'X'"
- **Cause:** Missing Python dependencies
- **Solution:** Install all required packages:
  ```bash
  pip install requests pycryptodome trimesh beautifulsoup4 networkx lxml
  ```

### "Node.js decoder produces no output"
- **Cause:** Missing or corrupted DITER keys
- **Solution:** Ensure `scripts/diter_decode.js` exists and Node.js is installed
- Check that params.json is valid JSON

### "AttributeError: 'Trimesh' object has no attribute 'remove_degenerate_faces'"
- **Cause:** Trimesh API version mismatch
- **Solution:** Use `repair=False` when exporting, or update trimesh

## Limitations

- Some models have download restrictions set by authors
- API rate limits may apply for authenticated endpoints
- DITER decoding requires Node.js (or slow Python alternative)
- Complex models with multiple geometry files may require manual handling
- Mesh repair functionality may have API compatibility issues

## License

For educational and research purposes only. Respect content creators' rights and Sketchfab's terms of service.
