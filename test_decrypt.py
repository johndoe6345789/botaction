#!/usr/bin/env python
"""
Test decryption of the model file
"""

from pathlib import Path
from model_decryptor import decrypt_model
from binz_reader import BinzReader
import json

binz_path = Path("downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.binz")
params_path = Path("downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json")

print("Loading encrypted model...")
print(f"File: {binz_path.name}")
print(f"Size: {binz_path.stat().st_size:,} bytes")

try:
    data = decrypt_model(binz_path, params_path)
    print(f"\n✓ Successfully decrypted and decompressed!")
    print(f"  Decompressed size: {len(data):,} bytes")
    
    # Inspect the data
    reader = BinzReader()
    info = reader.inspect(data, max_preview=200)
    
    print("\nData inspection:")
    print(f"  Potential floats: {info.get('potential_float32_count', 0):,}")
    print(f"  Potential vec3 count: {info.get('potential_vec3_count', 0):,}")
    
    if 'sample_floats' in info:
        print(f"\n  First 12 floats:")
        for i, val in enumerate(info['sample_floats']):
            print(f"    [{i}]: {val:.6f}")
    
    # Try to parse geometry
    print("\nAttempting to parse geometry...")
    with open(params_path, 'r') as f:
        params = json.load(f)
    
    geometry = reader.parse_geometry_from_params(data, params)
    
    if geometry.vertices:
        print(f"✓ Found vertices: {geometry.vertex_count:,}")
    if geometry.normals:
        print(f"✓ Found normals: {geometry.normals.count:,}")
    if geometry.uvs:
        print(f"✓ Found UVs: {geometry.uvs.count:,}")
    if geometry.indices:
        print(f"✓ Found indices: {geometry.indices.count:,}")
        print(f"  Triangle count: {geometry.triangle_count:,}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
