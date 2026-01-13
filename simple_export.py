"""Simple export script to convert existing OSGJS to STL"""
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.export_stl import ModelSTLExporter

# Find the files
osgjs_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.osgjs.json')
model_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_model_file.binz')
params_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json')

if not osgjs_file.exists():
    print(f"Error: OSGJS file not found: {osgjs_file}")
    sys.exit(1)

if not model_file.exists():
    print(f"Error: Model file not found: {model_file}")
    sys.exit(1)

print(f"✓ Found OSGJS file: {osgjs_file.name}")
print(f"✓ Found model file: {model_file.name}")
print(f"✓ Found params file: {params_file.name}")

print("\nLoading geometry...", flush=True)
exporter = ModelSTLExporter()
print("  Created exporter", flush=True)
print(f"  Loading OSGJS from {osgjs_file.name}", flush=True)
exporter.load_from_osgjs(
    str(osgjs_file),
    [str(model_file)],
    params_path=str(params_file)
)
print("  Finished loading geometry", flush=True)

print(f"  Loaded {exporter.vertex_count:,} vertices")
print(f"  Loaded {len(exporter.triangles):,} triangles")

output = Path('output.stl')
print(f"\nExporting to {output}...")
exporter.export_stl(str(output), repair=True, verbose=True)

print(f"\n✓ Success! Exported to: {output}")
print(f"  File size: {output.stat().st_size:,} bytes")
