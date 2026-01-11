#!/usr/bin/env python3
"""
Execute a simplified n8n-style workflow for the DITER decode pipeline.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import ctypes
import shutil


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def _needs_rebuild(output: Path, inputs: list[Path]) -> bool:
    if not output.exists():
        return True
    out_mtime = _mtime(output)
    return any(_mtime(path) > out_mtime for path in inputs if path.exists())


def _resolve_cc() -> str | None:
    for name in ("cc", "gcc", "clang"):
        found = shutil.which(name)
        if found:
            return found
    return None


def build_engine_lib() -> Path:
    root = Path(__file__).resolve().parents[1]
    build_dir = root / "build" / "diter_engine"
    build_dir.mkdir(parents=True, exist_ok=True)

    src_dir = root / "src"
    sources = [
        src_dir / "diter_engine.c",
        src_dir / "diter_core.c",
        src_dir / "diter_rt.c",
    ]

    if sys.platform.startswith("linux"):
        lib_name = "libditer.so"
    elif sys.platform == "darwin":
        lib_name = "libditer.dylib"
    else:
        lib_name = "diter.dll"
    output = build_dir / lib_name

    if not _needs_rebuild(output, sources):
        return output

    cc = _resolve_cc()
    if not cc:
        raise RuntimeError("C compiler not found (need cc/gcc/clang).")

    cmd = [
        cc,
        "-O2",
        "-std=c11",
        "-shared",
        "-fPIC",
        "-I",
        str(src_dir),
        "-o",
        str(output),
    ] + [str(src) for src in sources]
    subprocess.run(cmd, check=True)
    return output


class DiterEngine:
    def __init__(self) -> None:
        lib_path = build_engine_lib()
        self.lib = ctypes.CDLL(str(lib_path))
        self.lib.diter_engine_create.restype = ctypes.c_void_p
        self.lib.diter_engine_destroy.argtypes = [ctypes.c_void_p]
        self.lib.diter_engine_init.argtypes = [ctypes.c_void_p]
        self.lib.diter_engine_set_key_hex.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.diter_engine_write_dict.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        self.lib.diter_engine_write_dict.restype = ctypes.c_int
        self.lib.diter_engine_write_chunk.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        self.lib.diter_engine_write_chunk.restype = ctypes.c_int
        self.lib.diter_engine_pump.argtypes = [ctypes.c_void_p]
        self.lib.diter_engine_pump.restype = ctypes.c_int
        self.lib.diter_engine_output.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.lib.diter_engine_output.restype = ctypes.POINTER(ctypes.c_uint8)
        self.lib.diter_engine_output_advance.argtypes = [ctypes.c_void_p]

        self.handle = self.lib.diter_engine_create()
        if not self.handle:
            raise RuntimeError("Failed to initialize DITER engine.")

    def close(self) -> None:
        if self.handle:
            self.lib.diter_engine_destroy(self.handle)
            self.handle = None

    def __enter__(self) -> "DiterEngine":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def init(self) -> None:
        self.lib.diter_engine_init(self.handle)

    def set_key_hex(self, key_hex: str) -> None:
        self.lib.diter_engine_set_key_hex(self.handle, key_hex.encode("ascii"))

    def write_dict(self, data: bytes) -> None:
        buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        if not self.lib.diter_engine_write_dict(self.handle, buf, len(data)):
            raise RuntimeError("Dictionary pointer out of bounds.")

    def write_chunk(self, data: bytes) -> None:
        buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        if not self.lib.diter_engine_write_chunk(self.handle, buf, len(data)):
            raise RuntimeError("Chunk pointer out of bounds.")

    def pump(self) -> int:
        return int(self.lib.diter_engine_pump(self.handle))

    def output(self) -> bytes:
        out_len = ctypes.c_uint32(0)
        out_ptr = self.lib.diter_engine_output(self.handle, ctypes.byref(out_len))
        if out_len.value == 0 or not out_ptr:
            return b""
        return ctypes.string_at(out_ptr, out_len.value)

    def output_advance(self) -> None:
        self.lib.diter_engine_output_advance(self.handle)


def clean_base64(text: str) -> str:
    return "".join(ch for ch in text if ch.isalnum() or ch in "+/=")


def parse_params_text(text: str) -> tuple[str | None, bool]:
    try:
        payload = json.loads(text)
        if isinstance(payload, list) and payload:
            payload = payload[0]
        if isinstance(payload, dict):
            return payload.get("b"), bool(payload.get("d"))
    except json.JSONDecodeError:
        pass

    b_match = re.search(r"\"b\"\\s*:\\s*\"([^\"]+)\"", text)
    d_match = re.search(r"\"d\"\\s*:\\s*(true|false|1|0)", text, re.IGNORECASE)
    b_val = b_match.group(1) if b_match else None
    d_val = False
    if d_match:
        d_val = d_match.group(1).lower() in ("true", "1")
    return b_val, d_val


def extract_key_hex(text: str) -> str | None:
    mod_match = re.search(r"module\\.exports\\s*=\\s*['\"]([^'\"]+)['\"]", text)
    if mod_match:
        cleaned = re.sub(r"[^0-9a-fA-F]", "", mod_match.group(1)).lower()
        return cleaned[:40] if len(cleaned) >= 40 else None
    run_match = re.search(r"[0-9a-fA-F]{40,}", text)
    if run_match:
        return run_match.group(0)[:40].lower()
    return None


def clean_key_hex(key_hex: str) -> str:
    cleaned = re.sub(r"[^0-9a-fA-F]", "", key_hex).lower()
    cleaned = (cleaned + ("0" * 40))[:40]
    return cleaned


def resolve_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str) and value.startswith("@"):
        return context.get(value[1:])
    if isinstance(value, dict):
        return {k: resolve_value(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_value(v, context) for v in value]
    return value


def apply_outputs(result: dict[str, Any], outputs: dict[str, str] | None, context: dict[str, Any]) -> None:
    if outputs:
        for key, name in outputs.items():
            if key in result:
                context[name] = result[key]
        return
    context.update(result)


def action_read_text(params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    path = resolve_value(params.get("path"), context)
    optional = bool(params.get("optional", False))
    if not path:
        if optional:
            return {}
        raise RuntimeError("read_text missing path")
    data = Path(path).read_text(encoding="utf-8")
    return {"text": data}


def action_read_bytes(params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    path = resolve_value(params.get("path"), context)
    optional = bool(params.get("optional", False))
    if not path:
        if optional:
            return {}
        raise RuntimeError("read_bytes missing path")
    data = Path(path).read_bytes()
    return {"bytes": data}


def action_parse_params(params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    text = resolve_value(params.get("text"), context)
    if not text:
        raise RuntimeError("parse_params missing text")
    dict_b64, needs_key = parse_params_text(text)
    return {"dict_b64": dict_b64, "needs_key": needs_key}


def action_decode_dict(params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    dict_b64 = resolve_value(params.get("dict_b64"), context)
    if not dict_b64:
        raise RuntimeError("decode_dict missing base64 content")
    cleaned = clean_base64(dict_b64)
    data = base64.b64decode(cleaned)
    return {"dict_bytes": data}


def action_extract_key_hex(params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    text = resolve_value(params.get("text"), context)
    if not text:
        return {"key_hex": None}
    return {"key_hex": extract_key_hex(text)}


def action_select_key(params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    key_hex = resolve_value(params.get("key_hex"), context)
    fallback = resolve_value(params.get("fallback_key_hex"), context)
    selected = key_hex or fallback
    return {"key_hex": selected}


def action_engine_decode(params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    binz_bytes = resolve_value(params.get("binz_bytes"), context)
    dict_bytes = resolve_value(params.get("dict_bytes"), context)
    needs_key = bool(resolve_value(params.get("needs_key"), context))
    key_hex = resolve_value(params.get("key_hex"), context)
    output_path = resolve_value(params.get("output_path"), context)
    chunk_size = resolve_value(params.get("chunk_size"), context) or 10240

    if binz_bytes is None or dict_bytes is None:
        raise RuntimeError("engine_decode missing binz/dict bytes")
    if needs_key and not key_hex:
        raise RuntimeError("engine_decode requires key_hex but none provided")
    if not output_path:
        raise RuntimeError("engine_decode missing output_path")

    if key_hex:
        key_hex = clean_key_hex(str(key_hex))

    output_path = Path(str(output_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with DiterEngine() as engine:
        if key_hex:
            engine.set_key_hex(key_hex)
        engine.init()
        engine.write_dict(dict_bytes)
        engine.pump()

        with output_path.open("wb") as out:
            for offset in range(0, len(binz_bytes), int(chunk_size)):
                chunk = binz_bytes[offset:offset + int(chunk_size)]
                engine.write_chunk(chunk)
                has_output = engine.pump()
                while has_output:
                    out_bytes = engine.output()
                    if out_bytes:
                        out.write(out_bytes)
                    engine.output_advance()
                    has_output = engine.pump()
    return {"output_size": output_path.stat().st_size if output_path.exists() else 0}


ACTIONS = {
    "read_text": action_read_text,
    "read_bytes": action_read_bytes,
    "parse_params": action_parse_params,
    "decode_dict": action_decode_dict,
    "extract_key_hex": action_extract_key_hex,
    "select_key": action_select_key,
    "engine_decode": action_engine_decode,
}


def run_workflow(doc: dict[str, Any], context: dict[str, Any]) -> None:
    nodes = {node["name"]: node for node in doc.get("nodes", [])}
    connections = doc.get("connections", {})

    targets = set()
    for src in connections.values():
        for typ in src.values():
            for outputs in typ.values():
                for target in outputs:
                    targets.add(target["node"])

    start_nodes = [name for name in nodes if name not in targets]
    if not start_nodes:
        raise RuntimeError("No entry nodes found in workflow.")

    visited = set()
    queue = list(start_nodes)
    while queue:
        name = queue.pop(0)
        if name in visited:
            continue
        visited.add(name)
        node = nodes.get(name)
        if not node:
            continue
        if node.get("type") == "diter.action":
            params = node.get("parameters", {})
            action_name = params.get("action")
            if not action_name:
                raise RuntimeError(f"Node '{name}' missing action")
            handler = ACTIONS.get(action_name)
            if not handler:
                raise RuntimeError(f"Unknown action '{action_name}' in node '{name}'")
            result = handler(params, context)
            apply_outputs(result, params.get("outputs"), context)

        next_nodes = connections.get(name, {}).get("main", {}).get("0", [])
        for target in next_nodes:
            queue.append(target["node"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DITER decode workflow.")
    parser.add_argument("--workflow", default="build/runbooks/diter_decode_workflow.json")
    parser.add_argument("--params")
    parser.add_argument("--binz")
    parser.add_argument("--out")
    parser.add_argument("--key-hex")
    parser.add_argument("--key-source")
    parser.add_argument("--chunk-size", type=int)
    args = parser.parse_args()

    workflow_path = Path(args.workflow)
    doc = json.loads(workflow_path.read_text(encoding="utf-8"))

    context = {}
    meta_inputs = doc.get("meta", {}).get("inputs", {})
    if isinstance(meta_inputs, dict):
        context.update(meta_inputs)

    if args.params:
        context["params_path"] = args.params
    if args.binz:
        context["binz_path"] = args.binz
    if args.out:
        context["out_path"] = args.out
    if args.key_hex:
        context["key_hex"] = args.key_hex
    if args.key_source:
        context["key_source_path"] = args.key_source
    if args.chunk_size:
        context["chunk_size"] = args.chunk_size

    run_workflow(doc, context)
    output_size = context.get("output_size")
    if output_size is not None:
        print(f"Output bytes: {output_size}")


if __name__ == "__main__":
    main()
