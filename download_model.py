from pathlib import Path
import argparse
from src.sketchfab_fetcher import SketchfabFetcher
from src.export_stl import ModelSTLExporter

def main():
    parser = argparse.ArgumentParser(
        description='Download and convert Sketchfab models to STL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and check for existing files
  python download_model.py
  
  # Download and decode with Python DITER (slow)
  python download_model.py --decode-diter
  
  # Specify a custom model URL
  python download_model.py --url https://sketchfab.com/3d-models/...
  
  # Decode and export with repair
  python download_model.py --decode-diter --repair
        """
    )
    
    parser.add_argument(
        '--url',
        default='https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63',
        help='Sketchfab model URL (default: Annihilator 2000)'
    )
    parser.add_argument(
        '--decode-diter',
        action='store_true',
        help='Force DITER decoding using Python/pywasm (slow, 5-10+ minutes)'
    )
    parser.add_argument(
        '--output',
        default='output.stl',
        help='Output STL file path (default: output.stl)'
    )
    parser.add_argument(
        '--repair',
        action='store_true',
        help='Repair mesh to make it watertight (requires trimesh)'
    )
    parser.add_argument(
        '--output-dir',
        default='downloads',
        help='Directory for downloaded files (default: downloads)'
    )
    
    args = parser.parse_args()

    print("=" * 70)
    print("Sketchfab Model Downloader & Converter")
    print("=" * 70)

    # 1. Fetch
    fetcher = SketchfabFetcher()
    result = fetcher.fetch_model(args.url)
    downloaded = fetcher.download_model_files(result['model_id'], args.output_dir)

    print("\n" + "=" * 70)
    print("Files Downloaded")
    print("=" * 70)
    for key, path in downloaded.items():
        print(f"  {key}: {Path(path).name}")

    # 2. Decrypt the .binz file using DITER if needed
    model_id = result['model_id']
    osgjs_files = list(Path(args.output_dir).glob(f'{model_id}*.osgjs.json'))

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
        
        if args.decode_diter:
            print("\n🔄 Attempting DITER decoding (this may take several minutes)...")
            try:
                from src.diter_decoder import decode_diter_file
                
                binz_path = Path(downloaded['binz'])
                params_path = Path(downloaded['params'])
                osgjs_path = binz_path.with_suffix('.osgjs.json')
                
                # Look for WASM and key files
                wasm_path = Path(args.output_dir) / "diter_wasm_blob.wasm"
                key_source = Path(args.output_dir) / "diter_standalone_deob.js"
                if not key_source.exists():
                    key_source = Path(args.output_dir) / "diter_standalone.js"
                
                print(f"  Input: {binz_path.name}")
                print(f"  Params: {params_path.name}")
                print(f"  Output: {osgjs_path.name}")
                
                if not wasm_path.exists():
                    print(f"\n❌ Error: {wasm_path} not found")
                    print(f"   Copy from: archive/diter/downloads/diter_wasm_blob.wasm")
                    return 1
                
                if not key_source.exists():
                    print(f"\n❌ Error: {key_source} not found")
                    print(f"   Copy from: archive/diter/downloads/diter_standalone_deob.js")
                    return 1
                
                decoded_size = decode_diter_file(
                    binz_path,
                    params_path,
                    osgjs_path,
                    wasm_path=wasm_path,
                    key_source=key_source,
                )
                
                print(f"\n✓ Decoded {decoded_size:,} bytes")
                osgjs_files = [osgjs_path]
            except ImportError:
                print("\n❌ Error: pywasm not installed")
                print("   Install with: pip install pywasm")
                return 1
            except Exception as e:
                print(f"\n❌ DITER decoding failed: {e}")
                import traceback
                traceback.print_exc()
                return 1
        else:
            print("\n⚠ Python DITER decoder (pywasm) is very slow (5-10+ minutes).")
            print("  For faster decoding, use one of these options:")
            print("\n  Option 1: Run with --decode-diter flag to use Python decoder")
            print(f"    python download_model.py --decode-diter")
            print("\n  Option 2: Use the C decoder (much faster)")
            print(f"    # Build C decoder first: cmake . && make")
            print(f"    # Then it's used automatically by the CLI")
            print("\n  Option 3: The model may already be exported")
            
            # Check for existing export
            existing_3mf = list(Path(args.output_dir).glob('*.3mf'))
            existing_stl = list(Path(args.output_dir).glob('*.stl'))
            if existing_3mf:
                print(f"\n  ✓ Found existing 3MF export: {existing_3mf[0].name}")
            if existing_stl:
                print(f"\n  ✓ Found existing STL export: {existing_stl[0].name}")
            
            return 0
    elif not osgjs_files:
        print("\n❌ Error: No OSGJS file found")
        return 1

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
        exporter.export_stl(args.output, repair=args.repair, verbose=args.repair)
        
        print(f"\n✓ Success! Exported to: {args.output}")
        print(f"  Vertices: {exporter.vertex_count:,}")
        print(f"  Triangles: {len(exporter.triangles):,}")
        if args.repair:
            print(f"  Mesh repaired for 3D printing")
        return 0
    else:
        print("❌ Error: model_file.binz not found")
        return 1


if __name__ == '__main__':
    exit(main())