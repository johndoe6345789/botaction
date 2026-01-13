"""Debug export to identify where the issue occurs"""
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
model_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_model_file.binz')
params_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json')

print(f"Model file size (encrypted): {model_file.stat().st_size:,} bytes")

# Load and decrypt
with open(params_file) as f:
    params = json.load(f)

print(f"Params: {params}")
print(f"Is encrypted: {params[0].get('d', False)}")

print("\nDecrypting...")
decryptor = SketchfabDecryptor()
decrypted = decryptor.decrypt_file(model_file, params)
print(f"Decrypted size: {len(decrypted):,} bytes")

# Save decrypted for inspection
decrypted_path = model_file.parent / (model_file.stem + '_decrypted.binz')
decrypted_path.write_bytes(decrypted)
print(f"Saved decrypted to: {decrypted_path}")

# Now try to load the OSGJS and parse
osgjs_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.osgjs.json')
with open(osgjs_file) as f:
    osgjs_data = json.load(f)

# Find first geometry with vertex data
def find_first_vertex_attr(obj, depth=0):
    if depth > 50 or not isinstance(obj, dict):
        return None
    if 'osg.Geometry' in obj:
        geom = obj['osg.Geometry']
        va = geom.get('VertexAttributeList', {}).get('Vertex')
        if va:
            return va
    for v in obj.values():
        if isinstance(v, dict):
            r = find_first_vertex_attr(v, depth+1)
            if r:
                return r
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    r = find_first_vertex_attr(item, depth+1)
                    if r:
                        return r
    return None

vertex_attr = find_first_vertex_attr(osgjs_data)
if vertex_attr and 'Array' in vertex_attr:
    arr_type = list(vertex_attr['Array'].keys())[0]
    arr_data = vertex_attr['Array'][arr_type]
    print(f"\nVertex Array Info:")
    print(f"  Type: {arr_type}")
    print(f"  File: {arr_data.get('File')}")
    print(f"  Offset: {arr_data.get('Offset'):,}")
    print(f"  Size: {arr_data.get('Size'):,}")
    print(f"  ItemSize: {vertex_attr.get('ItemSize')}")
    print(f"  Encoding: {arr_data.get('Encoding')}")

    offset = arr_data.get('Offset', 0)
    size = arr_data.get('Size', 0)
    item_size = vertex_attr.get('ItemSize', 3)

    print(f"\nBuffer requirements:")
    print(f"  Offset + (Size * ItemSize): {offset} + ({size} * {item_size}) = {offset + (size * item_size):,}")
    print(f"  Decrypted buffer size: {len(decrypted):,}")
    print(f"  Will it fit: {offset + (size * item_size) <= len(decrypted)}")
