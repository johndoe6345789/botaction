from pathlib import Path
from src.sketchfab_fetcher import SketchfabFetcher
from src.export_stl import ModelSTLExporter

print("=" * 70)
print("Sketchfab Model Downloader & Converter")
print("=" * 70)

# 1. Fetch
fetcher = SketchfabFetcher()
result = fetcher.fetch_model("https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63")
downloaded = fetcher.download_model_files(result['model_id'], 'downloads')

print("\n" + "=" * 70)
print("Files Downloaded")
print("=" * 70)
for key, path in downloaded.items():
    print(f"  {key}: {Path(path).name}")

# 2. Decrypt the .binz file using DITER if needed
model_id = result['model_id']
osgjs_files = list(Path('downloads').glob(f'{model_id}*.osgjs.json'))

if osgjs_files:
    # Check if it's valid JSON
    osgjs_path = osgjs_files[0]
    try:
        import json
        with open(osgjs_path, 'r') as f:
            json.load(f)
        print(f"\n✓ Found valid OSGJS file: {osgjs_path.name}")
    except:
        print(f"\n⚠ OSGJS file exists but is corrupted, re-decoding...")
        osgjs_files = []

if not osgjs_files and downloaded.get('binz') and downloaded.get('params'):
    print("\n" + "=" * 70)
    print("DITER Decryption Needed")
    print("=" * 70)
    print("The .osgjs.json file needs to be decrypted from the .binz file.")
    print("\nNote: Python DITER decoder (pywasm) is very slow.")
    print("Consider using the C decoder or Node.js version for faster processing.")
    print("\nFor now, skipping decryption. The model may already be available")
    print("as a 3MF or STL file in the downloads folder.")
    
    # Check for existing export
    existing_3mf = list(Path('downloads').glob('*.3mf'))
    existing_stl = list(Path('downloads').glob('*.stl'))
    if existing_3mf:
        print(f"\n✓ Found existing 3MF export: {existing_3mf[0].name}")
    if existing_stl:
        print(f"\n✓ Found existing STL export: {existing_stl[0].name}")
    
    exit(0)
elif not osgjs_files:
    print("\n❌ Error: No OSGJS file found")
    exit(1)

# 3. Export to STL
print("\n" + "=" * 70)
print("Exporting to STL")
print("=" * 70)

if 'model_file' in downloaded:
    print(f"OSGJS: {osgjs_path.name}")
    print(f"Geometry: {Path(downloaded['model_file']).name}")
    
    exporter = ModelSTLExporter()
    exporter.load_from_osgjs(
        str(osgjs_path),
        [downloaded['model_file']]
    )
    exporter.export_stl('output.stl')
    
    print(f"\n✓ Success! Exported to: output.stl")
    print(f"  Vertices: {exporter.vertex_count:,}")
    print(f"  Triangles: {len(exporter.triangles):,}")
else:
    print("❌ Error: model_file.binz not found")
    exit(1)
