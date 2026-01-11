#!/usr/bin/env python
"""
Test decryption without decompression
"""

from pathlib import Path
from src.model_decryptor import SketchfabDecryptor
from src.binz_reader import BinzReader
import json

binz_path = Path("downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.binz")
params_path = Path("downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json")

print("Testing decryption...")

try:
    decryptor = SketchfabDecryptor()
    
    with open(params_path, 'r') as f:
        params = json.load(f)
    
    # Just decrypt, don't decompress
    decrypted = decryptor.decrypt_file(binz_path, params)
    
    print(f"✓ Decryption successful!")
    print(f"  Decrypted size: {len(decrypted):,} bytes")
    print(f"  First 32 bytes (hex): {decrypted[:32].hex()}")
    print(f"  First 32 bytes (ascii, printable only): {''.join(chr(b) if 32 <= b < 127 else '.' for b in decrypted[:32])}")
    
    # Check if it's zlib compressed
    print(f"\nChecking for zlib header...")
    if len(decrypted) >= 2:
        # zlib header: first byte should be 0x78
        if decrypted[0] == 0x78 and decrypted[1] in [0x01, 0x5e, 0x9c, 0xda]:
            print("  ✓ Found zlib header!")
        else:
            print(f"  ✗ No zlib header (found: {decrypted[0]:02x} {decrypted[1]:02x})")
            print("  File might be raw binary data")
    
    # Try to parse as raw geometry
    print("\nTrying to parse as raw geometry...")
    reader = BinzReader()
    
    # Check if it looks like float data
    if len(decrypted) >= 48:
        sample = reader.read_float32_array(decrypted, 0, 12)
        print(f"  First 12 values as float32:")
        for i, val in enumerate(sample):
            print(f"    [{i}]: {val:.6f}")
        
        # Check if values look reasonable for 3D coordinates
        print(f"\n  Value range: [{sample.min():.3f}, {sample.max():.3f}]")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
