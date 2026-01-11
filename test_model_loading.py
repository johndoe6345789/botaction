#!/usr/bin/env python
"""
Simple test to verify model loading works
"""

from pathlib import Path
from model_viewer import ModelViewerWidget
from binz_reader import BinzReader

print("Testing model loading...")

# Find test models
downloads = Path("downloads")
test_files = list(downloads.glob("test_*.binz"))

if not test_files:
    print("No test files found!")
else:
    print(f"Found {len(test_files)} test file(s):")
    for f in test_files:
        print(f"  - {f.name}")

# Test loading
viewer = ModelViewerWidget()

for test_file in test_files:
    print(f"\nTesting: {test_file.name}")
    success = viewer.load_model(str(test_file))
    
    if success and viewer.geometry:
        print(f"  ✓ SUCCESS!")
        print(f"    Vertices: {viewer.geometry.vertex_count:,}")
        print(f"    Triangles: {viewer.geometry.triangle_count:,}")
        print(f"    Bounds: {viewer.model_center}")
        print(f"    Scale: {viewer.model_scale:.3f}")
    else:
        print(f"  ✗ FAILED")

print("\n✓ Test complete!")
