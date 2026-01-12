from pathlib import Path
import argparse
import shutil
from src.sketchfab_fetcher import SketchfabFetcher
from src.export_stl import ModelSTLExporter
from src.diter_decoder import decode_diter_file

def clean_downloads(output_dir: str = 'downloads') -> None:
    """Remove all downloaded files and temporary outputs."""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"✓ Directory {output_dir}/ does not exist, nothing to clean")
        return
    
    # Count files before deletion
    file_count = sum(1 for _ in output_path.rglob('*') if _.is_file())
    
    if file_count == 0:
        print(f"✓ Directory {output_dir}/ is already empty")
        return
    
    # Remove all files
    shutil.rmtree(output_path)
    output_path.mkdir(exist_ok=True)
    
    print(f"✓ Cleaned {file_count} files from {output_dir}/")
    print(f"  - Removed downloaded .binz files")
    print(f"  - Removed decoded .osgjs.json files")
    print(f"  - Removed params and thumbnails")
    print(f"  - Removed any cached outputs")

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
  
  # Clean all downloaded files
  python download_model.py --clean
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
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean downloaded files and temporary outputs'
    )
    
    args = parser.parse_args()
    
    # Handle clean command
    if args.clean:
        print("=" * 70)
        print("Cleaning Downloads")
        print("=" * 70)
        clean_downloads(args.output_dir)
        return 0

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
            binz_path = Path(downloaded['binz'])
            params_path = Path(downloaded['params'])
            osgjs_path = binz_path.with_suffix('.osgjs.json')
            
            # Look for WASM and key files
            wasm_path = Path(args.output_dir) / "diter_wasm_blob.wasm"
            key_source = Path(args.output_dir) / "diter_standalone_deob.js"
            if not key_source.exists():
                key_source = Path(args.output_dir) / "diter_standalone.js"
            
            # Download required JS bundles for Node decoder
            js_dir = Path("js_downloads/remote")
            js_dir.mkdir(parents=True, exist_ok=True)
            
            required_bundles = [
                "ec580af0b531503f94c740ca2873c32e-v2.js",
                "5bcaa88525fab96faffe19e1ce66716c-v2.js", 
                "7aa463e7a4f2c770ab2436d6def75af2-v2.js",
                "a25387388d9ea5501c87029166d396ac-v2.js",
            ]
            
            # Check if bundles exist in archive and copy them
            archive_js = Path("archive/diter/js_downloads/remote")
            if archive_js.exists():
                for bundle in required_bundles:
                    src = archive_js / bundle
                    dst = js_dir / bundle
                    if src.exists() and not dst.exists():
                        import shutil
                        shutil.copy(src, dst)
                print(f"\n📦 Copied JS bundles for Node.js decoder")
            
            # If WASM/key files don't exist, try to download them
            if not wasm_path.exists() or not key_source.exists():
                print("\n📥 Downloading DITER decoder files...")
                diter_files = fetcher.download_diter_files(model_id, args.output_dir)
                if diter_files.get('wasm'):
                    wasm_path = Path(diter_files['wasm'])
                if diter_files.get('key'):
                    key_source = Path(diter_files['key'])
            
            
            print(f"  Input: {binz_path.name}")
            print(f"  Params: {params_path.name}")
            print(f"  Output: {osgjs_path.name}")
            
            # Use Node.js decoder (much faster and more reliable than Python)
            import subprocess
            import shutil
            
            # Check if node is available
            node_path = shutil.which("node")
            if not node_path:
                print(f"\n❌ Error: Node.js not found")
                print(f"   Please install Node.js to use DITER decoder")
                print(f"   Or use the C decoder: cmake . && make")
                return 1
            
            # Copy decoder script from archive
            script_path = Path("scripts/diter_decode.js")
            if not script_path.exists():
                archive_script = Path("archive/diter/scripts/diter_decode.js")
                if archive_script.exists():
                    script_path.parent.mkdir(exist_ok=True)
                    shutil.copy(archive_script, script_path)
                    print(f"   ✓ Copied decoder script from archive")
                else:
                    print(f"\n❌ Error: DITER decoder script not found at {archive_script}")
                    return 1
            
            # Run Node.js decoder
            cmd = [
                node_path,
                str(script_path),
                "--binz", str(binz_path),
                "--params", str(params_path),
                "--out", str(osgjs_path),
            ]
            
            print(f"\n🔄 Running Node.js DITER decoder...")
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                if result.stdout:
                    print(result.stdout)
                
                if osgjs_path.exists():
                    decoded_size = osgjs_path.stat().st_size
                    print(f"\n✓ Decoded {decoded_size:,} bytes")
                    osgjs_files = [osgjs_path]
                else:
                    print(f"\n❌ Error: Decoder did not create output file")
                    return 1
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error: DITER decode failed")
                if e.stderr:
                    print(e.stderr)
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
            [downloaded['model_file']],
            params_path=downloaded.get('params')
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