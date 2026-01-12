#!/usr/bin/env python3
"""
Export Sketchfab OSGJS geometry to STL format with optional mesh repair.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Iterable, List, Tuple, Optional

import numpy as np

from .osgjs_decoder import decode_scene_to_triangles


def repair_mesh(triangles: List[np.ndarray], verbose: bool = False) -> List[np.ndarray]:
    """
    Repair a triangle mesh to make it watertight and printable.

    Uses trimesh library to:
    - Merge duplicate vertices
    - Remove degenerate triangles
    - Fill holes
    - Fix winding order (normals)
    - Remove unreferenced vertices

    Args:
        triangles: List of triangles, each as (3, 3) numpy array of vertices
        verbose: Print repair statistics

    Returns:
        Repaired list of triangles
    """
    try:
        import trimesh
    except ImportError:
        raise ImportError("trimesh is required for mesh repair. Install with: pip install trimesh")

    if not triangles:
        return triangles

    # Convert triangle list to vertices and faces arrays
    tri_array = np.array(triangles, dtype=np.float64)
    num_triangles = tri_array.shape[0]

    # Reshape to (N*3, 3) vertices
    vertices = tri_array.reshape(-1, 3)
    # Create faces as indices into vertices: [[0,1,2], [3,4,5], ...]
    faces = np.arange(num_triangles * 3).reshape(-1, 3)

    # Create trimesh object
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

    if verbose:
        print(f"Before repair: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        print(f"  Watertight: {mesh.is_watertight}")
        print(f"  Volume: {mesh.volume if mesh.is_watertight else 'N/A (not watertight)'}")

    # Merge duplicate vertices (within tolerance)
    mesh.merge_vertices()

    # Remove degenerate faces (zero area)
    mesh.remove_degenerate_faces()

    # Remove duplicate faces
    mesh.remove_duplicate_faces()

    # Remove unreferenced vertices
    mesh.remove_unreferenced_vertices()

    # Remove infinite values
    mesh.remove_infinite_values()

    # Fix face winding to be consistent
    trimesh.repair.fix_winding(mesh)

    # Fix inverted faces (normals pointing inward)
    trimesh.repair.fix_inversion(mesh)

    # Fill holes to make watertight
    trimesh.repair.fill_holes(mesh)

    if verbose:
        print(f"After repair: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        print(f"  Watertight: {mesh.is_watertight}")
        if mesh.is_watertight:
            print(f"  Volume: {mesh.volume:.2f}")

    # Convert back to triangle list
    repaired_triangles = []
    for face in mesh.faces:
        v0 = mesh.vertices[face[0]].astype(np.float32)
        v1 = mesh.vertices[face[1]].astype(np.float32)
        v2 = mesh.vertices[face[2]].astype(np.float32)
        repaired_triangles.append(np.array([v0, v1, v2]))

    return repaired_triangles


class ModelSTLExporter:
    """Export OSGJS scene geometry to STL."""

    def __init__(self) -> None:
        self.triangles: List[np.ndarray] = []
        self.vertex_count: int = 0

    def load_from_osgjs(self, osgjs_path: str | Path, geometry_paths: Iterable[str | Path], params_path: str | Path | None = None) -> "ModelSTLExporter":
        from .model_decryptor import SketchfabDecryptor
        import json
        
        file_map = {}
        for path in geometry_paths:
            path = Path(path)
            if not path.exists():
                continue
                
            # Check for pre-decoded version first
            decoded_path = path.parent / path.name.replace('.binz', '_decoded.binz')
            if decoded_path.exists():
                payload = decoded_path.read_bytes()
            else:
                # Try to decrypt if params are available
                payload = path.read_bytes()
                if params_path and Path(params_path).exists():
                    try:
                        with open(params_path) as f:
                            params = json.load(f)
                        if params and isinstance(params, list) and params[0].get('d', False):
                            # File is encrypted, decrypt it
                            decryptor = SketchfabDecryptor()
                            payload = decryptor.decrypt_file(path, params)
                    except Exception as e:
                        print(f"Warning: Could not decrypt {path.name}: {e}")
            
            file_map[path.name] = payload
            lower_name = path.name.lower()
            if "model_file_wireframe" in lower_name:
                file_map["model_file_wireframe.binz"] = payload
            elif "model_file" in lower_name:
                file_map["model_file.binz"] = payload
        self.triangles, self.vertex_count = decode_scene_to_triangles(osgjs_path, file_map)
        return self

    def repair(self, verbose: bool = False) -> "ModelSTLExporter":
        """
        Repair the mesh to make it watertight and printable.

        Args:
            verbose: Print repair statistics

        Returns:
            self for method chaining
        """
        self.triangles = repair_mesh(self.triangles, verbose=verbose)
        return self

    def export_stl(self, output_path: str | Path, repair: bool = True, verbose: bool = True) -> Path:
        """
        Export triangles to binary STL format.

        Args:
            output_path: Path to write STL file
            repair: If True, repair mesh before export (requires trimesh)
            verbose: Print repair statistics if repair=True

        Returns:
            Path to written file
        """
        if repair:
            self.repair(verbose=verbose)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            header = b"Sketchfab STL Export".ljust(80, b"\0")
            f.write(header)
            f.write(struct.pack("<I", len(self.triangles)))
            for tri in self.triangles:
                v0, v1, v2 = tri
                normal = np.cross(v1 - v0, v2 - v0)
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normal = normal / norm
                else:
                    normal = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                f.write(
                    struct.pack(
                        "<12fH",
                        float(normal[0]),
                        float(normal[1]),
                        float(normal[2]),
                        float(v0[0]),
                        float(v0[1]),
                        float(v0[2]),
                        float(v1[0]),
                        float(v1[1]),
                        float(v1[2]),
                        float(v2[0]),
                        float(v2[1]),
                        float(v2[2]),
                        0,
                    )
                )
        return output_path

    def render_preview(
        self,
        output_path: str | Path,
        width: int = 1024,
        height: int = 1024,
        max_triangles: int = 20000,
    ) -> Path:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.triangles:
            raise ValueError("No triangles available for preview rendering.")

        tri_array = np.array(self.triangles, dtype=np.float32)
        finite_mask = np.isfinite(tri_array).all(axis=(1, 2))
        if not finite_mask.all():
            tri_array = tri_array[finite_mask]
        if tri_array.size == 0:
            raise ValueError("No finite triangles available for preview rendering.")

        if tri_array.shape[0] >= 1000:
            v0 = tri_array[:, 0, :]
            v1 = tri_array[:, 1, :]
            v2 = tri_array[:, 2, :]
            edge_lengths = np.stack(
                [
                    np.linalg.norm(v1 - v0, axis=1),
                    np.linalg.norm(v2 - v1, axis=1),
                    np.linalg.norm(v0 - v2, axis=1),
                ],
                axis=1,
            )
            max_edge = edge_lengths.max(axis=1)
            median_edge = float(np.median(max_edge))
            if median_edge > 0:
                edge_mask = max_edge <= (median_edge * 20.0)
                filtered = tri_array[edge_mask]
                if filtered.shape[0] >= max(1000, tri_array.shape[0] // 10):
                    tri_array = filtered

        if max_triangles and tri_array.shape[0] > max_triangles:
            step = max(1, tri_array.shape[0] // max_triangles)
            tri_array = tri_array[::step]

        points = tri_array.reshape(-1, 3)
        min_pt = points.min(axis=0)
        max_pt = points.max(axis=0)
        pct_min = np.percentile(points, 1, axis=0)
        pct_max = np.percentile(points, 99, axis=0)
        full_range = max_pt - min_pt
        pct_range = pct_max - pct_min
        if np.all(pct_range > 0) and np.any(full_range > (pct_range * 4.0)):
            min_pt = pct_min
            max_pt = pct_max
        center = (min_pt + max_pt) * 0.5

        fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        ax.set_axis_off()

        collection = Poly3DCollection(tri_array, facecolor="#b0b0b0", edgecolor="#2c2c2c", linewidths=0.2)
        collection.set_alpha(1.0)
        ax.add_collection3d(collection)

        max_range = float((max_pt - min_pt).max())
        if max_range == 0:
            max_range = 1.0
        half = max_range * 0.6
        ax.set_xlim(center[0] - half, center[0] + half)
        ax.set_ylim(center[1] - half, center[1] + half)
        ax.set_zlim(center[2] - half, center[2] + half)
        ax.view_init(elev=22, azim=40)
        try:
            ax.set_box_aspect((1, 1, 1))
        except AttributeError:
            pass

        fig.tight_layout(pad=0)
        fig.savefig(output_path, dpi=100, transparent=False)
        plt.close(fig)
        return output_path
