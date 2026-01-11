#!/usr/bin/env python
"""
Create a test 3D model for the viewer

Generates simple geometric shapes that can be loaded by the viewer.
"""

import numpy as np
from pathlib import Path
import struct


def create_cube_geometry():
    """Create a simple cube mesh."""
    # Cube vertices (8 corners)
    vertices = np.array([
        # Front face
        [-1, -1,  1],  # 0
        [ 1, -1,  1],  # 1
        [ 1,  1,  1],  # 2
        [-1,  1,  1],  # 3
        # Back face
        [-1, -1, -1],  # 4
        [ 1, -1, -1],  # 5
        [ 1,  1, -1],  # 6
        [-1,  1, -1],  # 7
    ], dtype=np.float32)
    
    # Triangle indices (12 triangles = 36 indices)
    indices = np.array([
        # Front
        0, 1, 2,  0, 2, 3,
        # Back
        5, 4, 7,  5, 7, 6,
        # Top
        3, 2, 6,  3, 6, 7,
        # Bottom
        4, 5, 1,  4, 1, 0,
        # Right
        1, 5, 6,  1, 6, 2,
        # Left
        4, 0, 3,  4, 3, 7,
    ], dtype=np.uint16)
    
    return vertices, indices


def create_sphere_geometry(radius=1.0, segments=20, rings=20):
    """Create a UV sphere mesh."""
    vertices = []
    indices = []
    
    # Generate vertices
    for i in range(rings + 1):
        v = i / rings
        phi = v * np.pi
        
        for j in range(segments + 1):
            u = j / segments
            theta = u * 2 * np.pi
            
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.cos(phi)
            z = radius * np.sin(phi) * np.sin(theta)
            
            vertices.append([x, y, z])
    
    vertices = np.array(vertices, dtype=np.float32)
    
    # Generate indices
    for i in range(rings):
        for j in range(segments):
            first = i * (segments + 1) + j
            second = first + segments + 1
            
            # First triangle
            indices.extend([first, second, first + 1])
            # Second triangle
            indices.extend([second, second + 1, first + 1])
    
    indices = np.array(indices, dtype=np.uint16)
    
    return vertices, indices


def create_torus_geometry(major_radius=1.0, minor_radius=0.3, segments=30, sides=20):
    """Create a torus (donut) mesh."""
    vertices = []
    indices = []
    
    for i in range(segments):
        u = (i / segments) * 2 * np.pi
        
        for j in range(sides):
            v = (j / sides) * 2 * np.pi
            
            x = (major_radius + minor_radius * np.cos(v)) * np.cos(u)
            y = minor_radius * np.sin(v)
            z = (major_radius + minor_radius * np.cos(v)) * np.sin(u)
            
            vertices.append([x, y, z])
    
    vertices = np.array(vertices, dtype=np.float32)
    
    # Generate indices
    for i in range(segments):
        for j in range(sides):
            first = i * sides + j
            second = ((i + 1) % segments) * sides + j
            
            # First triangle
            indices.extend([
                first,
                second,
                ((i + 1) % segments) * sides + ((j + 1) % sides)
            ])
            # Second triangle
            indices.extend([
                first,
                ((i + 1) % segments) * sides + ((j + 1) % sides),
                i * sides + ((j + 1) % sides)
            ])
    
    indices = np.array(indices, dtype=np.uint16)
    
    return vertices, indices


def save_test_model(vertices, indices, filename):
    """Save geometry to a binary file that the viewer can load."""
    output_dir = Path("downloads")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'wb') as f:
        # Write vertices
        f.write(vertices.tobytes())
        # Write indices  
        f.write(indices.tobytes())
    
    print(f"Saved test model: {filepath}")
    print(f"  Vertices: {len(vertices)} ({len(vertices) * 3 * 4} bytes)")
    print(f"  Indices: {len(indices)} ({len(indices) * 2} bytes)")
    print(f"  Triangles: {len(indices) // 3}")
    
    return filepath


def main():
    print("Creating test 3D models...")
    print()
    
    # Create cube
    print("1. Cube")
    v, i = create_cube_geometry()
    save_test_model(v, i, "test_cube.binz")
    print()
    
    # Create sphere
    print("2. Sphere")
    v, i = create_sphere_geometry(radius=1.0, segments=30, rings=30)
    save_test_model(v, i, "test_sphere.binz")
    print()
    
    # Create torus
    print("3. Torus")
    v, i = create_torus_geometry(major_radius=1.0, minor_radius=0.3, segments=40, sides=20)
    save_test_model(v, i, "test_torus.binz")
    print()
    
    print("✓ Test models created!")
    print("\nYou can now load these in the 3D viewer:")
    print("  1. Run: python sketchfab_gui.py")
    print("  2. Go to the '3D Viewer' tab")
    print("  3. Click 'Load Model'")


if __name__ == "__main__":
    main()
