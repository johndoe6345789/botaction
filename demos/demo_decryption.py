#!/usr/bin/env python3
"""
Demonstration of Sketchfab Model Decryption

This script demonstrates how to decrypt the Annihilator 2000 model
from Sketchfab using the discovered encryption scheme.

Model: https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63
"""

import json
import sys
import struct
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_decryptor import SketchfabDecryptor


def analyze_binary_data(data: bytes):
    """Analyze the decrypted binary data."""
    print("\n" + "=" * 70)
    print("BINARY DATA ANALYSIS")
    print("=" * 70)
    
    print(f"\nTotal size: {len(data):,} bytes")
    print(f"As 32-bit floats: {len(data) // 4:,} floats")
    print(f"As 32-bit integers: {len(data) // 4:,} integers")
    
    # Try to interpret as floats
    try:
        num_floats = len(data) // 4
        floats = struct.unpack(f'{num_floats}f', data)
        
        # Statistics
        valid_floats = [f for f in floats if not (f != f or abs(f) > 1e10)]  # Filter NaN and huge values
        if valid_floats:
            print(f"\nFloat statistics (excluding NaN/huge):")
            print(f"  Valid floats: {len(valid_floats):,}")
            print(f"  Min: {min(valid_floats):.6f}")
            print(f"  Max: {max(valid_floats):.6f}")
            print(f"  Average: {sum(valid_floats)/len(valid_floats):.6f}")
        
        # First few floats
        print(f"\nFirst 32 floats:")
        for i in range(0, min(32, len(floats)), 4):
            values = floats[i:i+4]
            print(f"  [{i:3d}-{i+3:3d}]: {' '.join(f'{v:10.4f}' for v in values)}")
        
        # Look for potential vec3 patterns (groups of 3 similar-magnitude floats)
        print(f"\nPotential vertex positions (vec3 pattern):")
        for i in range(0, min(48, len(floats)), 3):
            x, y, z = floats[i:i+3]
            if all(-100 < v < 100 for v in [x, y, z]):  # Reasonable vertex range
                print(f"  Vertex {i//3:3d}: ({x:8.3f}, {y:8.3f}, {z:8.3f})")
        
    except struct.error as e:
        print(f"Error unpacking as floats: {e}")


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("SKETCHFAB MODEL DECRYPTION DEMONSTRATION")
    print("=" * 70)
    print("\nModel: Annihilator 2000")
    print("URL: https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63")
    print("=" * 70)
    
    # File paths
    model_dir = Path(__file__).parent / "downloads"
    binz_file = model_dir / "dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.binz"
    params_file = model_dir / "dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json"
    
    # Check files exist
    if not binz_file.exists():
        print(f"\n❌ Error: Encrypted model file not found: {binz_file}")
        print("   Please download the model first using sketchfab_fetcher.py")
        return 1
    
    if not params_file.exists():
        print(f"\n❌ Error: Parameters file not found: {params_file}")
        print("   Please download the model first using sketchfab_fetcher.py")
        return 1
    
    print(f"\n✓ Found encrypted model file: {binz_file.name}")
    print(f"  Size: {binz_file.stat().st_size:,} bytes")
    
    print(f"\n✓ Found parameters file: {params_file.name}")
    
    # Load parameters
    print("\n" + "-" * 70)
    print("LOADING ENCRYPTION PARAMETERS")
    print("-" * 70)
    
    with open(params_file, 'r') as f:
        params = json.load(f)
    
    param = params[0]
    print(f"\nParameter version: {param.get('v', 'unknown')}")
    print(f"Encrypted flag: {param.get('d', False)}")
    print(f"Base64 params length: {len(param.get('b', ''))} characters")
    
    # Initialize decryptor
    print("\n" + "-" * 70)
    print("DECRYPTING MODEL")
    print("-" * 70)
    
    decryptor = SketchfabDecryptor()
    
    # Decode encryption parameters
    import base64
    key, iv = decryptor.decode_encryption_params(param['b'])
    
    print(f"\nAES-256-CBC Parameters:")
    print(f"  Key length: {len(key)} bytes (256 bits)")
    print(f"  Key (hex): {key[:16].hex()}... (first 16 bytes)")
    print(f"  IV length: {len(iv)} bytes (128 bits)")
    print(f"  IV (hex): {iv.hex()}")
    
    # Decrypt
    try:
        print("\nDecrypting...")
        data = decryptor.decrypt_and_decompress(str(binz_file), params)
        
        print(f"\n✅ SUCCESS! Decrypted {len(data):,} bytes of geometry data")
        
        # Show first bytes
        print(f"\nFirst 64 bytes (hex):")
        hex_data = data[:64].hex()
        for i in range(0, len(hex_data), 64):
            print(f"  {hex_data[i:i+64]}")
        
        # Analyze the data
        analyze_binary_data(data)
        
        # Save decrypted data
        output_file = model_dir / "annihilator_2000_decrypted.bin"
        with open(output_file, 'wb') as f:
            f.write(data)
        print(f"\n✓ Saved decrypted data to: {output_file.name}")
        
        print("\n" + "=" * 70)
        print("DECRYPTION COMPLETE!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Parse the .osgjs metadata file to understand geometry layout")
        print("  2. Extract vertex positions, normals, UVs, and indices")
        print("  3. Reconstruct the 3D mesh")
        print("  4. Export to standard format (OBJ, glTF, etc.)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during decryption: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
