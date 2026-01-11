"""
Decode Sketchfab OSGJS scene + geometry (.binz) into mesh triangles.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

import numpy as np


ATTRIBUTE_BITS = {
    "Vertex": 1,
    "Normal": 2,
    "TexCoord": 4,
    "Color": 8,
    "Triangle": 16,
    "Tangent": 32,
}

MODE_SCALE_OFFSET = 1
MODE_PREDICT = 2

TRI_MODE_DELTA = 1
TRI_MODE_TRANSFORM = 2
TRI_MODE_IMPLICIT = 4

IMPLICIT_HEADER_PRIMITIVE_LENGTH = 0
IMPLICIT_HEADER_MASK_LENGTH = 1
IMPLICIT_HEADER_EXPECTED_INDEX = 2
IMPLICIT_HEADER_LENGTH = 3

DTYPE_MAP = {
    "Int8Array": np.int8,
    "Uint8Array": np.uint8,
    "Int16Array": np.int16,
    "Uint16Array": np.uint16,
    "Int32Array": np.int32,
    "Uint32Array": np.uint32,
    "Float32Array": np.float32,
    "Float64Array": np.float64,
}


def _to_uint32(value: int) -> int:
    return value & 0xFFFFFFFF


def _to_int32(value: int) -> int:
    value &= 0xFFFFFFFF
    if value & 0x80000000:
        return value - 0x100000000
    return value


def _parse_number(value: Any) -> Any:
    if isinstance(value, (int, float)):
        return value
    if value is None:
        return value
    text = str(value).strip()
    if text == "":
        return value
    if text.lstrip("-").isdigit():
        try:
            return int(text)
        except ValueError:
            return value
    try:
        return float(text)
    except ValueError:
        return value


def parse_user_data(container: Dict[str, Any]) -> Dict[str, Any]:
    values = container.get("Values", []) if container else []
    user_data: Dict[str, Any] = {}
    for entry in values:
        name = entry.get("Name")
        if not name:
            continue
        user_data[name] = _parse_number(entry.get("Value"))
    return user_data


def load_scene(path: str | Path) -> Dict[str, Any]:
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="ignore")
    return json.loads(text)


def iter_geometry_nodes(node: Dict[str, Any], parent_matrix: np.ndarray | None = None) -> Iterator[Tuple[Dict[str, Any], np.ndarray]]:
    if parent_matrix is None:
        parent_matrix = np.identity(4, dtype=np.float32)
    if not isinstance(node, dict):
        return

    if "osg.Geometry" in node:
        yield node["osg.Geometry"], parent_matrix

    if "osg.MatrixTransform" in node:
        mt = node["osg.MatrixTransform"]
        matrix_values = mt.get("Matrix") or [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ]
        local = np.array(matrix_values, dtype=np.float32).reshape((4, 4), order="F")
        next_matrix = parent_matrix @ local
        for child in mt.get("Children", []):
            yield from iter_geometry_nodes(child, next_matrix)

    if "osg.Node" in node:
        for child in node["osg.Node"].get("Children", []):
            yield from iter_geometry_nodes(child, parent_matrix)

    for child in node.get("Children", []):
        yield from iter_geometry_nodes(child, parent_matrix)


def _extract_array_block(attr: Dict[str, Any]) -> Tuple[str, Dict[str, Any]] | None:
    array_block = attr.get("Array", {}) if attr else {}
    if not array_block:
        return None
    type_name = next(iter(array_block.keys()))
    return type_name, array_block[type_name]


def _decode_varint(data: bytes, count: int, dtype_name: str) -> List[int]:
    signed = not dtype_name.startswith("U")
    out = [0] * count
    pos = 0
    for idx in range(count):
        value = 0
        shift = 0
        while True:
            byte = data[pos]
            pos += 1
            value |= ((byte & 0x7F) << (shift & 31)) & 0xFFFFFFFF
            value &= 0xFFFFFFFF
            if (byte & 0x80) == 0:
                break
            shift += 7
        out[idx] = value
    if signed:
        for idx, value in enumerate(out):
            value = _to_int32(value)
            out[idx] = (value >> 1) ^ (-(value & 1))
    else:
        for idx, value in enumerate(out):
            out[idx] = _to_uint32(value)
    return out


def decode_array(attr: Dict[str, Any], item_size: int, file_map: Dict[str, bytes]) -> List[int] | np.ndarray:
    extracted = _extract_array_block(attr)
    if not extracted:
        return []
    type_name, info = extracted
    file_name = info.get("File")
    if not file_name or file_name not in file_map:
        return []
    data = file_map[file_name]
    offset = int(info.get("Offset", 0) or 0)
    size = int(info.get("Size", 0) or 0)
    count = size * item_size
    encoding = info.get("Encoding")
    if encoding == "varint":
        return _decode_varint(data[offset:], count, type_name)
    dtype = DTYPE_MAP.get(type_name, np.float32)
    return np.frombuffer(data, dtype=dtype, count=count, offset=offset)


def _delta_decode(values: List[int], start: int = 0) -> List[int]:
    if not values:
        return values
    if start >= len(values):
        return values
    running = _to_uint32(values[start])
    for idx in range(start + 1, len(values)):
        value = _to_int32(values[idx])
        running = running + ((value >> 1) ^ (-(value & 1)))
        values[idx] = running
    return values


def _implicit_header(values: List[int], out: List[int], start: int, use_constant: bool, truncate_uint16: bool) -> List[int]:
    expected = values[IMPLICIT_HEADER_EXPECTED_INDEX]
    mask_length = values[IMPLICIT_HEADER_MASK_LENGTH]
    mask_start = IMPLICIT_HEADER_LENGTH
    mask_end = mask_start + mask_length
    masks = values[mask_start:mask_end]
    missing = 32 * mask_length - len(out)
    index = start
    for block_index, mask in enumerate(masks):
        mask = _to_uint32(mask)
        bit_start = missing if block_index == mask_length - 1 else 0
        for bit in range(bit_start, 32):
            out_index = 32 * block_index + bit
            if mask & (0x80000000 >> (bit & 31)):
                value = values[index] if index < len(values) else 0
                if out_index < len(out):
                    out[out_index] = value & 0xFFFF if truncate_uint16 else value
                index += 1
            else:
                if out_index < len(out):
                    out[out_index] = expected & 0xFFFF if truncate_uint16 else expected
                if not use_constant:
                    expected += 1
    return out


def _index_transform(values: List[int], state: List[int], truncate_uint16: bool) -> List[int]:
    expected = state[0]
    for idx, value in enumerate(values):
        decoded = expected - value
        values[idx] = decoded & 0xFFFF if truncate_uint16 else decoded
        if expected <= decoded:
            expected = decoded + 1
    state[0] = expected
    return values


def decode_indices(
    indices_attr: Dict[str, Any],
    file_map: Dict[str, bytes],
    user_data: Dict[str, Any],
    mode: str,
    state: List[int],
) -> List[int]:
    item_size = int(indices_attr.get("ItemSize", 1) or 1)
    raw = decode_array(indices_attr, item_size, file_map)
    values = raw.tolist() if isinstance(raw, np.ndarray) else list(raw)
    attributes = int(user_data.get("attributes", 0) or 0)
    if not (attributes & ATTRIBUTE_BITS["Triangle"]):
        return values
    if mode not in ("TRIANGLE_STRIP", "TRIANGLES"):
        return values
    triangle_mode = int(user_data.get("triangle_mode", 0) or 0)
    is_strip = mode == "TRIANGLE_STRIP"
    output = values
    start = 0
    truncate_uint16 = False
    if triangle_mode & TRI_MODE_IMPLICIT and is_strip:
        primitive_len = values[IMPLICIT_HEADER_PRIMITIVE_LENGTH]
        output = [0] * primitive_len
        start = IMPLICIT_HEADER_LENGTH + values[IMPLICIT_HEADER_MASK_LENGTH]
        truncate_uint16 = True
    if triangle_mode & TRI_MODE_DELTA:
        _delta_decode(values, start)
    if triangle_mode & TRI_MODE_IMPLICIT and is_strip:
        _implicit_header(values, output, start, bool(triangle_mode & TRI_MODE_TRANSFORM), truncate_uint16)
    if triangle_mode & TRI_MODE_TRANSFORM:
        _index_transform(output, state, truncate_uint16)
    return output


def _predict_attribute(values: List[int], item_size: int, indices: List[int]) -> List[int]:
    if not values or not indices:
        return values
    vertex_count = len(values) // item_size
    if vertex_count == 0:
        return values
    visited = [0] * vertex_count
    for idx in range(min(3, len(indices))):
        i = indices[idx]
        if 0 <= i < vertex_count:
            visited[i] = 1
    for idx in range(2, len(indices) - 1):
        a = idx - 2
        i0 = indices[a]
        i1 = indices[a + 1]
        i2 = indices[a + 2]
        i3 = indices[a + 3]
        if i3 < 0 or i3 >= vertex_count:
            continue
        if visited[i3]:
            continue
        visited[i3] = 1
        if (
            i0 < 0
            or i0 >= vertex_count
            or i1 < 0
            or i1 >= vertex_count
            or i2 < 0
            or i2 >= vertex_count
        ):
            continue
        base0 = i0 * item_size
        base1 = i1 * item_size
        base2 = i2 * item_size
        base3 = i3 * item_size
        for comp in range(item_size):
            values[base3 + comp] = (
                values[base3 + comp]
                + values[base1 + comp]
                + values[base2 + comp]
                - values[base0 + comp]
            )
    return values


def _apply_scale_offset(values: List[int], base: List[float], scale: List[float], item_size: int) -> np.ndarray:
    out = np.empty(len(values), dtype=np.float32)
    count = len(values) // item_size if item_size else 0
    for idx in range(count):
        offset = idx * item_size
        for comp in range(item_size):
            out[offset + comp] = base[comp] + values[offset + comp] * scale[comp]
    return out


def decode_vertices(
    vertex_attr: Dict[str, Any],
    file_map: Dict[str, bytes],
    user_data: Dict[str, Any],
    indices: List[int] | None,
) -> np.ndarray:
    item_size = int(vertex_attr.get("ItemSize", 3) or 3)
    raw = decode_array(vertex_attr, item_size, file_map)
    if isinstance(raw, np.ndarray):
        values = raw.astype(np.float32)
        return values.reshape((-1, item_size))

    values = list(raw)
    mode = int(user_data.get("vertex_mode", 0) or 0)
    if mode & MODE_PREDICT and indices:
        _predict_attribute(values, item_size, indices)

    prefix = "vtx_"
    if mode & MODE_SCALE_OFFSET and f"{prefix}bbl_x" in user_data:
        base = [
            float(user_data.get(f"{prefix}bbl_x", 0.0)),
            float(user_data.get(f"{prefix}bbl_y", 0.0)),
            float(user_data.get(f"{prefix}bbl_z", 0.0)),
        ]
        scale = [
            float(user_data.get(f"{prefix}h_x", 1.0)),
            float(user_data.get(f"{prefix}h_y", 1.0)),
            float(user_data.get(f"{prefix}h_z", 1.0)),
        ]
        decoded = _apply_scale_offset(values, base, scale, item_size)
    else:
        decoded = np.array(values, dtype=np.float32)
    return decoded.reshape((-1, item_size))


def apply_transform(vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    if vertices.size == 0:
        return vertices
    hom = np.column_stack([vertices, np.ones(len(vertices), dtype=np.float32)])
    transformed = (matrix @ hom.T).T
    return transformed[:, :3]


def build_triangles(vertices: np.ndarray, indices: List[int], mode: str) -> List[np.ndarray]:
    triangles: List[np.ndarray] = []
    vertex_count = len(vertices)
    if mode == "TRIANGLE_STRIP":
        for i in range(len(indices) - 2):
            a, b, c = indices[i], indices[i + 1], indices[i + 2]
            if (
                a < 0
                or b < 0
                or c < 0
                or a >= vertex_count
                or b >= vertex_count
                or c >= vertex_count
            ):
                continue
            if a == b or b == c or a == c:
                continue
            if i % 2 == 0:
                tri = (a, b, c)
            else:
                tri = (b, a, c)
            triangles.append(vertices[list(tri)])
    else:
        for i in range(0, len(indices) - 2, 3):
            a, b, c = indices[i], indices[i + 1], indices[i + 2]
            if (
                a < 0
                or b < 0
                or c < 0
                or a >= vertex_count
                or b >= vertex_count
                or c >= vertex_count
            ):
                continue
            if a == b or b == c or a == c:
                continue
            triangles.append(vertices[[a, b, c]])
    return triangles


def decode_scene_to_triangles(
    osgjs_path: str | Path,
    file_map: Dict[str, bytes],
    include_wireframe: bool = False,
) -> Tuple[List[np.ndarray], int]:
    scene = load_scene(osgjs_path)
    triangles: List[np.ndarray] = []
    vertex_count = 0

    for geometry, matrix in iter_geometry_nodes(scene.get("osg.Node", scene)):
        user_data = parse_user_data(geometry.get("UserDataContainer", {}))
        vertex_attr = geometry.get("VertexAttributeList", {}).get("Vertex")
        if not vertex_attr:
            continue
        array_block = _extract_array_block(vertex_attr)
        if not array_block:
            continue
        _, array_info = array_block
        file_name = array_info.get("File", "")
        if not include_wireframe and "wireframe" in file_name:
            continue

        primitive_sets = geometry.get("PrimitiveSetList", [])
        index_state = [0]
        decoded_sets: List[Tuple[List[int], str]] = []
        predictor_indices: List[int] | None = None
        for primitive in primitive_sets:
            if "DrawElementsUInt" in primitive:
                prim_data = primitive["DrawElementsUInt"]
            elif "DrawElementsUShort" in primitive:
                prim_data = primitive["DrawElementsUShort"]
            else:
                continue
            indices_attr = prim_data.get("Indices")
            if not indices_attr:
                continue
            mode = prim_data.get("Mode", "TRIANGLES")
            decoded = decode_indices(indices_attr, file_map, user_data, mode, index_state)
            decoded_sets.append((decoded, mode))
            if mode == "TRIANGLE_STRIP":
                predictor_indices = decoded

        if not decoded_sets:
            continue

        vertices = decode_vertices(vertex_attr, file_map, user_data, predictor_indices)
        vertex_count += len(vertices)
        vertices = apply_transform(vertices, matrix)
        for decoded, mode in decoded_sets:
            triangles.extend(build_triangles(vertices, decoded, mode))

    return triangles, vertex_count
