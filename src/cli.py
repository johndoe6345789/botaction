#!/usr/bin/env python3
"""
Sketchfab Model Tools CLI

A command-line interface for working with Sketchfab 3D models.
Supports fetching, decrypting, inspecting, and exporting models.
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .sketchfab_fetcher import SketchfabFetcher
from .model_decryptor import SketchfabDecryptor, decrypt_model
from .binz_reader import BinzReader


def cmd_fetch(args):
    """Fetch model information and download files."""
    print(f"Fetching model from: {args.url}")

    fetcher = SketchfabFetcher()
    result = fetcher.fetch_model(args.url)

    if result['error']:
        print(f"Error: {result['error']}")
        return 1

    # Print summary
    api_data = result.get('api_data', {})
    if api_data:
        print(f"\nModel: {api_data.get('name', 'Unknown')}")
        print(f"Author: {api_data.get('user', {}).get('username', 'Unknown')}")
        print(f"Views: {api_data.get('viewCount', 0):,}")
        print(f"Likes: {api_data.get('likeCount', 0):,}")

    # Download files if requested
    if args.download:
        print(f"\nDownloading files to: {args.output_dir}")
        downloaded = fetcher.download_model_files(
            result['model_id'],
            output_dir=args.output_dir
        )
        print(f"Downloaded: {len(downloaded)} files")
        for name, path in downloaded.items():
            print(f"  {name}: {path}")

    # Save metadata
    if args.save_meta:
        meta_file = Path(args.output_dir) / f"{result['model_id']}_metadata.json"
        with open(meta_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Metadata saved to: {meta_file}")

    return 0


def cmd_decrypt(args):
    """Decrypt an encrypted .binz file."""
    binz_path = Path(args.binz_file)
    params_path = Path(args.params_file) if args.params_file else None

    if not binz_path.exists():
        print(f"Error: .binz file not found: {binz_path}")
        return 1

    if params_path and not params_path.exists():
        print(f"Error: params file not found: {params_path}")
        return 1

    print(f"Decrypting: {binz_path.name}")

    try:
        if params_path:
            # Use the convenience function
            decrypted_data = decrypt_model(binz_path, params_path)
        else:
            # Manual decryption with key
            if not args.key:
                print("Error: Must provide --key or --params-file")
                return 1

            try:
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import unpad
            except ImportError:
                print("Error: PyCryptodome required for manual key decryption")
                return 1

            decryptor = SketchfabDecryptor()
            key, iv = decryptor.decode_encryption_params(args.key)

            # Read and decrypt
            with open(binz_path, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt AES-256-CBC
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

            # Try to decompress if it looks compressed
            import zlib
            if len(decrypted_data) >= 2 and decrypted_data[0] == 0x78 and decrypted_data[1] in (0x01, 0x9C, 0xDA):
                try:
                    decrypted_data = zlib.decompress(decrypted_data)
                except:
                    pass  # Not compressed, use as-is

        # Save decrypted file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        print(f"Decrypted {len(decrypted_data):,} bytes")
        print(f"Saved to: {output_path}")

        # Inspect if requested
        if args.inspect:
            reader = BinzReader()
            info = reader.inspect(decrypted_data)
            print("\nDecrypted data inspection:")
            for key, value in info.items():
                print(f"  {key}: {value}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_inspect(args):
    """Inspect a .binz file."""
    binz_path = Path(args.binz_file)

    if not binz_path.exists():
        print(f"Error: File not found: {binz_path}")
        return 1

    print(f"Inspecting: {binz_path.name}")
    print(f"Size: {binz_path.stat().st_size:,} bytes")

    try:
        reader = BinzReader()
        data = reader.read_file(binz_path)
        print(f"Decompressed size: {len(data):,} bytes")

        info = reader.inspect(data)
        print("\nData structure:")
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Try to load params and parse geometry
        params_path = binz_path.with_suffix('.binz').parent / f"{binz_path.stem}_params.json"
        if params_path.exists():
            print(f"\nFound params file: {params_path.name}")
            with open(params_path, 'r') as f:
                params = json.load(f)

            print("Attempting to parse geometry...")
            geometry = reader.parse_geometry_from_params(data, params)

            if geometry.vertices:
                print(f"✓ Found vertices: {geometry.vertex_count:,}")
            if geometry.normals:
                print(f"✓ Found normals: {geometry.normal_count:,}")
            if geometry.uvs:
                print(f"✓ Found UVs: {geometry.uv_count:,}")
            if geometry.indices:
                print(f"✓ Found indices: {geometry.index_count:,}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_export(args):
    """Export decrypted model to 3MF format."""
    try:
        from .export_3mf import Model3MFExporter
    except ImportError:
        print("Error: Could not import 3MF exporter")
        return 1

    binz_path = Path(args.binz_file)
    output_path = Path(args.output)

    if not binz_path.exists():
        print(f"Error: .binz file not found: {binz_path}")
        return 1

    print(f"Exporting {binz_path.name} to 3MF...")

    try:
        exporter = Model3MFExporter()
        exporter.load_from_binary(binz_path)
        exporter.export_3mf(output_path)

        print(f"✓ Exported to: {output_path}")
        print(f"  Vertices: {len(exporter.vertices):,}")
        print(f"  Triangles: {len(exporter.triangles):,}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_info(args):
    """Show information about available commands."""
    print("Sketchfab Model Tools CLI")
    print("=" * 40)
    print()
    print("Available commands:")
    print("  fetch    - Fetch model info and download files from Sketchfab")
    print("  decrypt  - Decrypt an encrypted .binz file")
    print("  inspect  - Inspect a .binz file structure")
    print("  export   - Export decrypted model to 3MF format")
    print("  info     - Show this help information")
    print()
    print("Use 'sketchfab-cli <command> --help' for command-specific help.")


def main():
    parser = argparse.ArgumentParser(
        description="Sketchfab Model Tools CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch model from Sketchfab')
    fetch_parser.add_argument('url', help='Sketchfab model URL')
    fetch_parser.add_argument('--download', action='store_true',
                             help='Download model files')
    fetch_parser.add_argument('--output-dir', default='downloads',
                             help='Output directory for downloads (default: downloads)')
    fetch_parser.add_argument('--save-meta', action='store_true',
                             help='Save metadata to JSON file')
    fetch_parser.set_defaults(func=cmd_fetch)

    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt .binz file')
    decrypt_parser.add_argument('binz_file', help='Path to .binz file')
    decrypt_parser.add_argument('--params-file',
                               help='Path to params JSON file (alternative to --key)')
    decrypt_parser.add_argument('--key', help='Base64-encoded encryption key')
    decrypt_parser.add_argument('--output', required=True,
                               help='Output path for decrypted file')
    decrypt_parser.add_argument('--inspect', action='store_true',
                               help='Inspect decrypted data after decryption')
    decrypt_parser.set_defaults(func=cmd_decrypt)

    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect .binz file')
    inspect_parser.add_argument('binz_file', help='Path to .binz file')
    inspect_parser.set_defaults(func=cmd_inspect)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export to 3MF format')
    export_parser.add_argument('binz_file', help='Path to decrypted .binz file')
    export_parser.add_argument('--output', required=True,
                              help='Output .3mf file path')
    export_parser.set_defaults(func=cmd_export)

    # Info command
    info_parser = subparsers.add_parser('info', help='Show information')
    info_parser.set_defaults(func=cmd_info)

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Run the command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())