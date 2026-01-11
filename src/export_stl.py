#!/usr/bin/env python3
"""
Export Sketchfab OSGJS geometry to STL format.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np

from .osgjs_decoder import decode_scene_to_triangles


class ModelSTLExporter:
    """Export OSGJS scene geometry to STL."""

    def __init__(self) -> None:
        self.triangles: List[np.ndarray] = []
        self.vertex_count: int = 0

    def load_from_osgjs(self, osgjs_path: str | Path, geometry_paths: Iterable[str | Path]) -> "ModelSTLExporter":
        file_map = {}
        for path in geometry_paths:
            path = Path(path)
            if path.exists():
                payload = path.read_bytes()
                file_map[path.name] = payload
                lower_name = path.name.lower()
                if "model_file_wireframe" in lower_name:
                    file_map["model_file_wireframe.binz"] = payload
                elif "model_file" in lower_name:
                    file_map["model_file.binz"] = payload
        self.triangles, self.vertex_count = decode_scene_to_triangles(osgjs_path, file_map)
        return self

    def export_stl(self, output_path: str | Path) -> Path:
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
