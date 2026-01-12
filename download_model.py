from src.sketchfab_fetcher import SketchfabFetcher
from src.model_decryptor import SketchfabDecryptor
from src.export_stl import ModelSTLExporter

# 1. Fetch
fetcher = SketchfabFetcher()
result = fetcher.fetch_model("https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63")
fetcher.download_model_files(result['model_id'], 'downloads')

# 2. Decrypt + Decode + Export
exporter = ModelSTLExporter()
exporter.load_from_osgjs(
    f'downloads/{result["model_id"]}.osgjs.json',
    [f'downloads/{result["model_id"]}_model_file.binz']
)
exporter.export_stl('output.stl')
