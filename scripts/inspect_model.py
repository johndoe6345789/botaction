#!/usr/bin/env python
"""
Quick test to examine the .binz file structure
"""

import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.binz_reader import BinzReader
import json

# Load the binz file
binz_path = Path("downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.binz")
params_path = Path("downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json")

reader = BinzReader()

print("Reading .binz file...")
data = reader.read_file(binz_path)
print(f"Decompressed size: {len(data):,} bytes")

# Inspect the data
print("\nInspecting data structure...")
info = reader.inspect(data)
for key, value in info.items():
    print(f"  {key}: {value}")

# Load params
print("\nParams file:")
with open(params_path, 'r') as f:
    params = json.load(f)
    print(json.dumps(params, indent=2))

print("\nNote: The model appears to be encrypted (d: true in params)")
print("The 'b' field contains base64-encoded encryption key material")
print("Decryption would require implementing AES decryption")
