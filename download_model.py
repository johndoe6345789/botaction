from pathlib import Path
import json
from src.sketchfab_fetcher import SketchfabFetcher
from src.model_decryptor import SketchfabDecryptor
from src.export_stl import ModelSTLExporter

# 1. Fetch
fetcher = SketchfabFetcher()
result = fetcher.fetch_model("https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63")
downloaded = fetcher.download_model_files(result['model_id'], 'downloads')

# 2. Decrypt the .binz file to create .osgjs.json
if 'binz' in downloaded and 'params' in downloaded:
    decryptor = SketchfabDecryptor()
    
    # Read params
    with open(downloaded['params'], 'r') as f:
        params = json.load(f)
    
    # Decrypt and decompress
    decrypted_data = decryptor.decrypt_and_decompress(downloaded['binz'], params)
    
    # Save as .osgjs.json
    osgjs_path = Path(downloaded['binz']).with_suffix('.osgjs.json')
    with open(osgjs_path, 'wb') as f:
        f.write(decrypted_data)
    print(f"Decrypted: {osgjs_path}")
    
    # 3. Export to STL
    exporter = ModelSTLExporter()
    exporter.load_from_osgjs(
        str(osgjs_path),
        [downloaded['model_file']]
    )
    exporter.export_stl('output.stl')
    print(f"Exported: output.stl")
else:
    print("Error: Required files not downloaded")
