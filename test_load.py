"""Test loading with debug output"""
import sys
import io
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.model_decryptor import SketchfabDecryptor

# Find the files
osgjs_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.osgjs.json')
model_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_model_file.binz')
params_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json')

print(f"Building file_map...", flush=True)

# Replicate the logic from export_stl.py
file_map = {}
geometry_paths = [model_file]

for path in geometry_paths:
    path = Path(path)
    if not path.exists():
        continue

    # Check for pre-decoded version first
    decoded_path = path.parent / path.name.replace('.binz', '_decoded.binz')
    if decoded_path.exists():
        print(f"  Using pre-decoded file: {decoded_path.name}", flush=True)
        payload = decoded_path.read_bytes()
    else:
        # Try to decrypt if params are available
        print(f"  Reading encrypted file: {path.name}", flush=True)
        payload = path.read_bytes()
        if params_file and Path(params_file).exists():
            try:
                with open(params_file) as f:
                    params = json.load(f)
                if params and isinstance(params, list) and params[0].get('d', False):
                    # File is encrypted, decrypt it
                    print(f"  Decrypting...", flush=True)
                    decryptor = SketchfabDecryptor()
                    payload = decryptor.decrypt_file(path, params)
                    print(f"  Decrypted: {len(payload):,} bytes", flush=True)
            except Exception as e:
                print(f"Warning: Could not decrypt {path.name}: {e}", flush=True)

    file_map[path.name] = payload
    lower_name = path.name.lower()
    if "model_file_wireframe" in lower_name:
        file_map["model_file_wireframe.binz"] = payload
    elif "model_file" in lower_name:
        file_map["model_file.binz"] = payload

print(f"\nFile map keys: {list(file_map.keys())}", flush=True)
for key, data in file_map.items():
    print(f"  {key}: {len(data):,} bytes", flush=True)

print(f"\nLoading OSGJS and decoding triangles...", flush=True)
from src.osgjs_decoder import decode_scene_to_triangles

triangles, vertex_count = decode_scene_to_triangles(osgjs_file, file_map)
print(f"\n✓ Success!", flush=True)
print(f"  Vertices: {vertex_count:,}", flush=True)
print(f"  Triangles: {len(triangles):,}", flush=True)
