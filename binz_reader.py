"""
Sketchfab .binz File Reader

.binz files are zlib-compressed binary geometry data used by Sketchfab's viewer.
They contain vertex positions, normals, UVs, and indices for 3D meshes.

The format is typically:
1. Zlib-compressed data
2. Inside: raw binary arrays (Float32Array for vertices/normals, Uint16/32Array for indices)

This module provides utilities to:
- Decompress .binz files
- Parse the binary geometry data
- Extract mesh information

Note: The exact structure depends on the accompanying .osgjs JSON file which describes
the layout and offsets of the binary data.
"""

from __future__ import annotations
import zlib
import struct
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, BinaryIO
from pathlib import Path
import numpy as np


@dataclass
class GeometryBuffer:
    """Represents a typed array buffer from the binary data."""
    data: np.ndarray
    item_size: int  # e.g., 3 for vec3, 2 for vec2
    count: int  # number of elements
    byte_offset: int = 0
    byte_length: int = 0

    @property
    def stride(self) -> int:
        """Bytes per element."""
        return self.data.itemsize * self.item_size


@dataclass
class MeshGeometry:
    """Parsed mesh geometry from binary data."""
    vertices: Optional[GeometryBuffer] = None  # vec3 positions
    normals: Optional[GeometryBuffer] = None   # vec3 normals
    uvs: Optional[GeometryBuffer] = None       # vec2 texture coords
    indices: Optional[GeometryBuffer] = None   # triangle indices
    colors: Optional[GeometryBuffer] = None    # vertex colors
    tangents: Optional[GeometryBuffer] = None  # vec4 tangents

    @property
    def vertex_count(self) -> int:
        if self.vertices:
            return self.vertices.count
        return 0

    @property
    def triangle_count(self) -> int:
        if self.indices:
            return self.indices.count // 3
        return self.vertex_count // 3


class BinzReader:
    """
    Reader for Sketchfab .binz compressed binary geometry files.

    Usage:
        reader = BinzReader()

        # Read and decompress
        data = reader.read_file("model.binz")

        # Or decompress raw bytes
        data = reader.decompress(compressed_bytes)

        # Parse with layout info from .osgjs
        geometry = reader.parse_geometry(data, layout)
    """

    def __init__(self):
        self._cache: Dict[str, bytes] = {}

    def read_file(self, path: str | Path) -> bytes:
        """
        Read and decompress a .binz file.

        Args:
            path: Path to the .binz file

        Returns:
            Decompressed binary data
        """
        path = Path(path)

        if str(path) in self._cache:
            return self._cache[str(path)]

        with open(path, 'rb') as f:
            compressed = f.read()

        decompressed = self.decompress(compressed)
        self._cache[str(path)] = decompressed
        return decompressed

    def decompress(self, data: bytes) -> bytes:
        """
        Decompress zlib-compressed data.

        Handles both raw deflate and zlib-wrapped data.

        Args:
            data: Compressed bytes

        Returns:
            Decompressed bytes
        """
        try:
            # Try zlib format first (has header)
            return zlib.decompress(data)
        except zlib.error:
            try:
                # Try raw deflate (no header)
                return zlib.decompress(data, -zlib.MAX_WBITS)
            except zlib.error:
                # Try gzip format
                return zlib.decompress(data, zlib.MAX_WBITS | 16)

    def read_float32_array(
        self,
        data: bytes,
        offset: int = 0,
        count: Optional[int] = None
    ) -> np.ndarray:
        """
        Read Float32Array from binary data.

        Args:
            data: Binary data
            offset: Byte offset to start reading
            count: Number of floats to read (None = all remaining)

        Returns:
            numpy array of float32
        """
        if count is None:
            count = (len(data) - offset) // 4

        return np.frombuffer(
            data,
            dtype=np.float32,
            count=count,
            offset=offset
        )

    def read_uint16_array(
        self,
        data: bytes,
        offset: int = 0,
        count: Optional[int] = None
    ) -> np.ndarray:
        """Read Uint16Array from binary data."""
        if count is None:
            count = (len(data) - offset) // 2

        return np.frombuffer(
            data,
            dtype=np.uint16,
            count=count,
            offset=offset
        )

    def read_uint32_array(
        self,
        data: bytes,
        offset: int = 0,
        count: Optional[int] = None
    ) -> np.ndarray:
        """Read Uint32Array from binary data."""
        if count is None:
            count = (len(data) - offset) // 4

        return np.frombuffer(
            data,
            dtype=np.uint32,
            count=count,
            offset=offset
        )

    def read_int8_array(
        self,
        data: bytes,
        offset: int = 0,
        count: Optional[int] = None
    ) -> np.ndarray:
        """Read Int8Array from binary data."""
        if count is None:
            count = len(data) - offset

        return np.frombuffer(
            data,
            dtype=np.int8,
            count=count,
            offset=offset
        )

    def parse_buffer(
        self,
        data: bytes,
        dtype: str,
        byte_offset: int,
        byte_length: int,
        item_size: int = 1
    ) -> GeometryBuffer:
        """
        Parse a typed array buffer from binary data.

        Args:
            data: Binary data
            dtype: Data type ('float32', 'uint16', 'uint32', 'int8')
            byte_offset: Offset in bytes
            byte_length: Length in bytes
            item_size: Components per element (e.g., 3 for vec3)

        Returns:
            GeometryBuffer with parsed data
        """
        dtype_map = {
            'float32': np.float32,
            'uint16': np.uint16,
            'uint32': np.uint32,
            'int8': np.int8,
            'uint8': np.uint8,
        }

        np_dtype = dtype_map.get(dtype, np.float32)
        element_size = np.dtype(np_dtype).itemsize
        count = byte_length // element_size

        arr = np.frombuffer(
            data,
            dtype=np_dtype,
            count=count,
            offset=byte_offset
        )

        return GeometryBuffer(
            data=arr,
            item_size=item_size,
            count=count // item_size,
            byte_offset=byte_offset,
            byte_length=byte_length
        )

    def parse_geometry(
        self,
        data: bytes,
        layout: Dict[str, Any]
    ) -> MeshGeometry:
        """
        Parse mesh geometry using layout info from .osgjs file.

        The layout dict should contain buffer descriptions with:
        - type: 'ARRAY_BUFFER' or 'ELEMENT_ARRAY_BUFFER'
        - byteOffset: offset in binary file
        - byteLength: length of buffer
        - componentType: GL type (5126=float, 5123=ushort, etc.)
        - itemSize: components per vertex (3 for position, 2 for uv)

        Args:
            data: Decompressed binary data
            layout: Layout description from .osgjs

        Returns:
            MeshGeometry with parsed buffers
        """
        geometry = MeshGeometry()

        # GL type constants
        GL_BYTE = 5120
        GL_UNSIGNED_BYTE = 5121
        GL_SHORT = 5122
        GL_UNSIGNED_SHORT = 5123
        GL_INT = 5124
        GL_UNSIGNED_INT = 5125
        GL_FLOAT = 5126

        gl_to_dtype = {
            GL_BYTE: 'int8',
            GL_UNSIGNED_BYTE: 'uint8',
            GL_SHORT: 'int16',
            GL_UNSIGNED_SHORT: 'uint16',
            GL_INT: 'int32',
            GL_UNSIGNED_INT: 'uint32',
            GL_FLOAT: 'float32',
        }

        def parse_attribute(attr_info: Dict) -> Optional[GeometryBuffer]:
            if not attr_info:
                return None

            dtype = gl_to_dtype.get(attr_info.get('componentType', GL_FLOAT), 'float32')
            return self.parse_buffer(
                data,
                dtype=dtype,
                byte_offset=attr_info.get('byteOffset', 0),
                byte_length=attr_info.get('byteLength', 0),
                item_size=attr_info.get('itemSize', 1)
            )

        # Parse vertex attributes
        if 'Vertex' in layout:
            geometry.vertices = parse_attribute(layout['Vertex'])
        elif 'position' in layout:
            geometry.vertices = parse_attribute(layout['position'])

        if 'Normal' in layout:
            geometry.normals = parse_attribute(layout['Normal'])
        elif 'normal' in layout:
            geometry.normals = parse_attribute(layout['normal'])

        if 'TexCoord0' in layout:
            geometry.uvs = parse_attribute(layout['TexCoord0'])
        elif 'uv' in layout:
            geometry.uvs = parse_attribute(layout['uv'])

        if 'Color' in layout:
            geometry.colors = parse_attribute(layout['Color'])

        if 'Tangent' in layout:
            geometry.tangents = parse_attribute(layout['Tangent'])

        # Parse indices
        if 'indices' in layout:
            geometry.indices = parse_attribute(layout['indices'])
        elif 'DrawElementsUShort' in layout:
            geometry.indices = parse_attribute(layout['DrawElementsUShort'])
        elif 'DrawElementsUInt' in layout:
            geometry.indices = parse_attribute(layout['DrawElementsUInt'])

        return geometry

    def inspect(self, data: bytes, max_preview: int = 100) -> Dict[str, Any]:
        """
        Inspect binary data and return basic info.

        Useful for understanding unknown binary formats.

        Args:
            data: Binary data to inspect
            max_preview: Max bytes to show in preview

        Returns:
            Dict with inspection results
        """
        info = {
            'size_bytes': len(data),
            'size_kb': len(data) / 1024,
            'size_mb': len(data) / (1024 * 1024),
        }

        # Check for magic bytes / signatures
        if len(data) >= 4:
            info['first_4_bytes_hex'] = data[:4].hex()
            info['first_4_bytes_raw'] = list(data[:4])

            # Try to interpret as different types
            try:
                info['as_uint32_le'] = struct.unpack('<I', data[:4])[0]
                info['as_float32_le'] = struct.unpack('<f', data[:4])[0]
            except struct.error:
                pass

        # Count potential floats
        if len(data) >= 4:
            float_count = len(data) // 4
            info['potential_float32_count'] = float_count
            info['potential_vec3_count'] = float_count // 3

            # Sample first few floats
            try:
                sample_floats = self.read_float32_array(data, 0, min(12, float_count))
                info['sample_floats'] = sample_floats.tolist()
            except Exception:
                pass

        # Hex preview
        preview_bytes = data[:max_preview]
        info['hex_preview'] = preview_bytes.hex()

        return info

    def clear_cache(self):
        """Clear the file cache."""
        self._cache.clear()

    def parse_geometry_from_params(
        self,
        data: bytes,
        params: List[Dict[str, Any]]
    ) -> MeshGeometry:
        """
        Parse geometry from .binz data using params array from Sketchfab.

        Args:
            data: Decompressed binary data
            params: Parameters array from embed config

        Returns:
            MeshGeometry with parsed buffers
        """
        geometry = MeshGeometry()

        # The params array typically contains buffer definitions
        # Each param describes a buffer with type, offset, and format info
        for param in params:
            if not isinstance(param, dict):
                continue

            # Look for buffer type indicators
            buffer_type = param.get('type', '')
            semantic = param.get('semantic', '')
            
            # Map common semantics to geometry attributes
            if 'POSITION' in semantic or 'Vertex' in semantic:
                geometry.vertices = self._parse_param_buffer(data, param, 3)
            elif 'NORMAL' in semantic or 'Normal' in semantic:
                geometry.normals = self._parse_param_buffer(data, param, 3)
            elif 'TEXCOORD' in semantic or 'TexCoord' in semantic:
                geometry.uvs = self._parse_param_buffer(data, param, 2)
            elif 'indices' in semantic.lower() or buffer_type == 'ELEMENT_ARRAY_BUFFER':
                # Indices are typically 1D
                geometry.indices = self._parse_param_buffer(data, param, 1)

        return geometry

    def _parse_param_buffer(
        self,
        data: bytes,
        param: Dict[str, Any],
        item_size: int
    ) -> Optional[GeometryBuffer]:
        """Parse a single buffer from param definition."""
        try:
            byte_offset = param.get('byteOffset', 0)
            byte_length = param.get('byteLength', 0)
            component_type = param.get('componentType', 5126)  # Default to FLOAT

            # GL type constants
            GL_FLOAT = 5126
            GL_UNSIGNED_SHORT = 5123
            GL_UNSIGNED_INT = 5125

            dtype_map = {
                GL_FLOAT: 'float32',
                GL_UNSIGNED_SHORT: 'uint16',
                GL_UNSIGNED_INT: 'uint32',
            }

            dtype = dtype_map.get(component_type, 'float32')

            return self.parse_buffer(
                data,
                dtype=dtype,
                byte_offset=byte_offset,
                byte_length=byte_length,
                item_size=item_size
            )
        except Exception as e:
            print(f"Error parsing param buffer: {e}")
            return None


def auto_detect_geometry(data: bytes) -> Optional[MeshGeometry]:
    """
    Attempt to auto-detect and parse geometry from binary data.

    This is a heuristic approach when no layout info is available.
    Assumes common patterns:
    - Float32 vertex positions
    - Float32 normals
    - Uint16 or Uint32 indices

    Args:
        data: Decompressed binary data

    Returns:
        MeshGeometry if detection succeeds, None otherwise
    """
    reader = BinzReader()

    # Try to interpret as float32 array
    floats = reader.read_float32_array(data)

    if len(floats) == 0:
        return None

    # Assume vec3 positions
    if len(floats) % 3 != 0:
        return None

    vertex_count = len(floats) // 3

    geometry = MeshGeometry()
    geometry.vertices = GeometryBuffer(
        data=floats,
        item_size=3,
        count=vertex_count,
        byte_offset=0,
        byte_length=len(floats) * 4
    )

    return geometry


def read_osgjs_scene(osgjs_path: str | Path) -> Dict[str, Any]:
    """
    Read and parse an .osgjs scene file.

    The .osgjs file is a JSON file describing the scene graph
    and referencing binary geometry files.

    Args:
        osgjs_path: Path to .osgjs file

    Returns:
        Parsed JSON scene data
    """
    with open(osgjs_path, 'r') as f:
        return json.load(f)


def extract_buffer_info(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract buffer information from an .osgjs scene.

    Args:
        scene: Parsed .osgjs scene data

    Returns:
        List of buffer descriptions
    """
    buffers = []

    def traverse(obj, path=""):
        if isinstance(obj, dict):
            # Look for buffer-like objects
            if 'File' in obj or 'Array' in obj:
                buffers.append({
                    'path': path,
                    'info': obj
                })

            for key, value in obj.items():
                traverse(value, f"{path}/{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                traverse(item, f"{path}[{i}]")

    traverse(scene)
    return buffers


# Convenience functions
def read_binz(path: str | Path) -> bytes:
    """Read and decompress a .binz file."""
    return BinzReader().read_file(path)


def decompress_binz(data: bytes) -> bytes:
    """Decompress .binz data."""
    return BinzReader().decompress(data)


def inspect_binz(path: str | Path) -> Dict[str, Any]:
    """Inspect a .binz file and return info."""
    reader = BinzReader()
    data = reader.read_file(path)
    return reader.inspect(data)


__all__ = [
    'BinzReader',
    'GeometryBuffer',
    'MeshGeometry',
    'auto_detect_geometry',
    'read_osgjs_scene',
    'extract_buffer_info',
    'read_binz',
    'decompress_binz',
    'inspect_binz',
]
