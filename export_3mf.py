#!/usr/bin/env python3
"""
Export decrypted Sketchfab models to 3MF format.

3MF (3D Manufacturing Format) is an XML-based format for 3D printing.
"""

import struct
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple, List
import numpy as np


class Model3MFExporter:
    """Export 3D models to 3MF format."""
    
    def __init__(self):
        self.vertices = []
        self.triangles = []
    
    def parse_binary_geometry(self, data: bytes) -> Tuple[np.ndarray, np.ndarray]:
        """
        Parse binary geometry data.
        
        Format:
        - Float32 array of vertices (X,Y,Z triplets)
        - Uint16 array of indices
        
        Args:
            data: Raw binary geometry data
            
        Returns:
            Tuple of (vertices, indices) as numpy arrays
        """
        # Read all as float32 first
        num_floats = len(data) // 4
        all_data = np.frombuffer(data, dtype=np.float32, count=num_floats)
        
        # Strategy: Find the split between vertices (floats) and indices
        # Vertices are typically in range -10000 to 10000
        # Indices when interpreted as floats will look weird
        
        # Look for the boundary: where values stop being reasonable vertex coords
        # and start looking like packed uint16 indices
        
        best_split = None
        best_score = -1
        
        # Try different split points (must be multiple of 3 for vertices)
        for split_idx in range(3, len(all_data) - 3, 3):
            vertices = all_data[:split_idx]
            
            # Check if vertices look reasonable
            if len(vertices) < 3:
                continue
            
            # Vertices should mostly be in reasonable range
            vertex_score = np.sum(np.abs(vertices) < 10000) / len(vertices)
            
            # Check if remaining data looks like indices when read as uint16
            idx_bytes = data[split_idx * 4:]
            if len(idx_bytes) < 2:
                continue
                
            indices = np.frombuffer(idx_bytes, dtype=np.uint16, count=len(idx_bytes)//2)
            
            # Indices should be small integers (< number of vertices)
            max_expected_idx = split_idx // 3  # Number of vertices
            if len(indices) > 0:
                idx_score = np.sum(indices < max_expected_idx * 2) / len(indices)
            else:
                idx_score = 0
            
            # Combined score
            score = (vertex_score + idx_score) / 2
            
            if score > best_score:
                best_score = score
                best_split = split_idx
        
        # Use the best split we found
        if best_split is not None and best_score > 0.7:
            vertices = all_data[:best_split].reshape(-1, 3)
            idx_bytes = data[best_split * 4:]
            indices = np.frombuffer(idx_bytes, dtype=np.uint16)
            return vertices, indices
        
        # Fallback: assume all data is vertices
        vertex_count = (len(all_data) // 3) * 3
        vertices = all_data[:vertex_count].reshape(-1, 3)
        indices = np.arange(len(vertices), dtype=np.uint16)
        
        return vertices, indices
    
    def load_from_binary(self, binary_path: str | Path):
        """Load geometry from decrypted binary file."""
        with open(binary_path, 'rb') as f:
            data = f.read()
        
        vertices, indices = self.parse_binary_geometry(data)
        
        # Filter out invalid vertices (NaN, inf, too large)
        valid_mask = np.all(np.isfinite(vertices), axis=1)
        valid_mask &= np.all(np.abs(vertices) < 1e6, axis=1)
        
        if np.sum(valid_mask) < len(vertices):
            print(f"Warning: Filtered out {len(vertices) - np.sum(valid_mask)} invalid vertices")
            
            # Create mapping from old to new indices
            old_to_new = np.full(len(vertices), -1, dtype=np.int32)
            old_to_new[valid_mask] = np.arange(np.sum(valid_mask))
            
            # Update vertices
            vertices = vertices[valid_mask]
            
            # Update indices
            valid_triangles = []
            for i in range(0, len(indices) - 2, 3):
                tri = indices[i:i+3]
                if np.all(tri < len(old_to_new)) and np.all(old_to_new[tri] >= 0):
                    valid_triangles.extend(old_to_new[tri])
            
            indices = np.array(valid_triangles, dtype=np.uint16)
        
        self.vertices = vertices.tolist()
        self.triangles = []
        
        # Convert indices to triangles
        for i in range(0, len(indices) - 2, 3):
            self.triangles.append([int(indices[i]), int(indices[i+1]), int(indices[i+2])])
        
        print(f"Loaded {len(self.vertices)} vertices, {len(self.triangles)} triangles")
        
        return self
    
    def create_3mf_xml(self) -> str:
        """Create the 3D model XML content for 3MF."""
        # Create XML structure
        model = ET.Element('model', {
            'unit': 'millimeter',
            'xml:lang': 'en-US',
            'xmlns': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
        })
        
        # Resources
        resources = ET.SubElement(model, 'resources')
        obj = ET.SubElement(resources, 'object', {
            'id': '1',
            'type': 'model'
        })
        
        # Mesh
        mesh = ET.SubElement(obj, 'mesh')
        
        # Vertices
        vertices_elem = ET.SubElement(mesh, 'vertices')
        for v in self.vertices:
            ET.SubElement(vertices_elem, 'vertex', {
                'x': f'{v[0]:.6f}',
                'y': f'{v[1]:.6f}',
                'z': f'{v[2]:.6f}'
            })
        
        # Triangles
        triangles_elem = ET.SubElement(mesh, 'triangles')
        for t in self.triangles:
            ET.SubElement(triangles_elem, 'triangle', {
                'v1': str(t[0]),
                'v2': str(t[1]),
                'v3': str(t[2])
            })
        
        # Build
        build = ET.SubElement(model, 'build')
        ET.SubElement(build, 'item', {'objectid': '1'})
        
        # Convert to string with XML declaration
        xml_str = ET.tostring(model, encoding='utf-8', method='xml')
        return b'<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    
    def export_3mf(self, output_path: str | Path):
        """
        Export to 3MF format.
        
        3MF is a ZIP archive containing:
        - [Content_Types].xml
        - 3D/3dmodel.model (the main 3D data)
        - _rels/.rels (relationships)
        """
        output_path = Path(output_path)
        
        # Create the 3MF package (ZIP file)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # [Content_Types].xml
            content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>'''
            zf.writestr('[Content_Types].xml', content_types)
            
            # _rels/.rels
            rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''
            zf.writestr('_rels/.rels', rels)
            
            # 3D/3dmodel.model
            model_xml = self.create_3mf_xml()
            zf.writestr('3D/3dmodel.model', model_xml)
        
        print(f"✓ Exported to {output_path}")
        return output_path


def main():
    """Main function."""
    import sys
    
    print("=" * 70)
    print("3MF EXPORTER")
    print("=" * 70)
    
    # Find decrypted file
    decrypted_file = Path("downloads/annihilator_2000_decrypted.bin")
    
    if not decrypted_file.exists():
        print(f"\n❌ Error: Decrypted file not found: {decrypted_file}")
        print("   Run demo_decryption.py first to decrypt the model")
        
        # Try test files instead
        test_files = list(Path("downloads").glob("test_*.binz"))
        if test_files:
            print(f"\nFound {len(test_files)} test file(s), using first one:")
            decrypted_file = test_files[0]
            print(f"  {decrypted_file.name}")
        else:
            return 1
    
    print(f"\nInput: {decrypted_file.name}")
    print(f"Size: {decrypted_file.stat().st_size:,} bytes")
    
    # Load and export
    try:
        exporter = Model3MFExporter()
        exporter.load_from_binary(decrypted_file)
        
        # Export to 3MF
        output_file = decrypted_file.with_suffix('.3mf')
        exporter.export_3mf(output_file)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Output: {output_file}")
        print(f"   Vertices: {len(exporter.vertices):,}")
        print(f"   Triangles: {len(exporter.triangles):,}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
