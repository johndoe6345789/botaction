"""
Pure-Python DITER decoder using a WASM interpreter (pywasm).
"""

from __future__ import annotations

import base64
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

try:
    import pywasm
except ImportError:  # pragma: no cover - optional dependency
    pywasm = None


DITER_EXPORTS = {
    "ctor": "__wasm_call_ctors",
    "init": "mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l",
    "load_dict": "dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI",
    "load_chunk": "heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl",
    "pump": "GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW",
    "out_ptr": "TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT",
    "out_len": "bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg",
    "out_advance": "FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN",
    "set_key": "Umlja1JvbGxlZDRV",
}


@dataclass
class DiterParams:
    b: bytes
    d: bool
    v: Optional[int] = None


def _require_pywasm():
    if pywasm is None:
        raise RuntimeError("pywasm is required for Python DITER decoding. Install with: pip install pywasm")


def _extract_js_string(text: str) -> Optional[str]:
    idx = text.find("module.exports")
    if idx == -1:
        return None
    eq = text.find("=", idx)
    if eq == -1:
        return None
    quote_pos = None
    quote_char = None
    for ch in ('"', "'"):
        pos = text.find(ch, eq)
        if pos != -1 and (quote_pos is None or pos < quote_pos):
            quote_pos = pos
            quote_char = ch
    if quote_pos is None:
        return None
    end = text.find(quote_char, quote_pos + 1)
    if end == -1:
        return None
    return text[quote_pos + 1:end]


def _clean_hex(text: str) -> str:
    return re.sub(r"[^0-9a-fA-F]", "", text)


def _load_key_hex(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r"module\\.exports\\s*=\\s*([\"'])(?P<val>.*?)(\\1)", text, re.S):
        cleaned = _clean_hex(match.group("val"))
        if len(cleaned) >= 40:
            return cleaned[:40].lower()
    for match in re.findall(r"[0-9a-fA-F]{40,}", text):
        cleaned = _clean_hex(match)
        if len(cleaned) >= 40:
            return cleaned[:40].lower()
    return None


def _load_wasm_bytes(wasm_path: Optional[Path], wasm_b64_path: Optional[Path]) -> bytes:
    if wasm_path and wasm_path.exists():
        return wasm_path.read_bytes()
    if wasm_b64_path and wasm_b64_path.exists():
        text = wasm_b64_path.read_text(encoding="utf-8", errors="replace")
        raw = _extract_js_string(text)
        if raw is None:
            raise RuntimeError(f"Failed to parse base64 from {wasm_b64_path}")
        raw = raw.replace("\\n", "").replace("\\r", "")
        raw = "".join(raw.split())
        return base64.b64decode(raw)
    raise RuntimeError("WASM binary not found. Provide wasm_path or wasm_b64_path.")


def _parse_params(params_path: Path) -> DiterParams:
    params = json.loads(params_path.read_text(encoding="utf-8"))
    if not isinstance(params, list) or not params:
        raise ValueError("params.json must be a non-empty array")
    param = params[0]
    if not isinstance(param, dict) or "b" not in param:
        raise ValueError("params.json missing required 'b' field")
    b64_text = str(param["b"])
    b64_text = "".join(b64_text.split())
    decoded = base64.b64decode(b64_text)
    return DiterParams(
        b=decoded,
        d=bool(param.get("d")),
        v=param.get("v"),
    )


@dataclass
class _DiterRuntime:
    runtime: "pywasm.Runtime"
    memory: "pywasm.Memory"
    heap_ptr: int


def _build_runtime(wasm_bytes: bytes) -> _DiterRuntime:
    _require_pywasm()
    module = pywasm.ModuleDesc.from_reader(io.BytesIO(wasm_bytes))

    import_min = 1
    for imp in module.import_list:
        if isinstance(imp.desc, pywasm.MemType):
            import_min = imp.desc.limits.n
            break

    heap_base = 65536
    for global_def in module.global_list:
        if not global_def.expr.data:
            continue
        op = global_def.expr.data[0]
        if op.opcode == pywasm.opcode.i32_const:
            heap_base = op.args[0]
            break

    aligned = ((heap_base + 65535) >> 16) << 16
    total_bytes = 262144 + aligned
    total_pages = total_bytes >> 16
    initial_pages = max(import_min, total_pages - import_min)

    limits = pywasm.Limits()
    limits.n = initial_pages
    limits.m = 0
    mem_type = pywasm.MemType()
    mem_type.limits = limits
    memory = pywasm.MemInst(mem_type)

    heap_ptr = {"value": heap_base}

    def sbrk(store, n):  # pylint: disable=unused-argument
        old = heap_ptr["value"]
        new = old + n
        if new > len(memory.data):
            need = new - len(memory.data)
            pages = (need + 65535) >> 16
            memory.grow(pages)
        heap_ptr["value"] = new
        return old

    def abort(store):  # pylint: disable=unused-argument
        raise RuntimeError("WASM abort called")

    runtime = pywasm.Runtime(
        module,
        {"env": {"abort": abort, "sbrk": sbrk, "memory": memory}},
    )

    try:
        runtime.exec(DITER_EXPORTS["ctor"], [])
    except Exception:
        # ctor is optional for this module
        pass

    return _DiterRuntime(runtime=runtime, memory=memory, heap_ptr=heap_base)


def _write_key(runtime: _DiterRuntime, key_hex: str) -> None:
    ptr = runtime.runtime.exec(DITER_EXPORTS["set_key"], [0, 40])
    key_hex = _clean_hex(key_hex).lower().ljust(40, "0")[:40]
    for i in range(10):
        chunk = key_hex[i * 4:(i + 1) * 4].rjust(4, "0")
        for j, ch in enumerate(chunk):
            runtime.memory.data[ptr + i * 4 + j] = ord(ch)


def decode_diter_bytes(
    binz_bytes: bytes,
    params: DiterParams,
    *,
    wasm_path: Optional[Path] = None,
    wasm_b64_path: Optional[Path] = None,
    key_hex: Optional[str] = None,
    key_source: Optional[Path] = None,
) -> bytes:
    wasm_bytes = _load_wasm_bytes(wasm_path, wasm_b64_path)
    runtime = _build_runtime(wasm_bytes)

    if params.d:
        if not key_hex and key_source:
            key_hex = _load_key_hex(key_source)
        if not key_hex:
            raise RuntimeError("DITER key hex not provided and could not be derived.")
        _write_key(runtime, key_hex)

    rt = runtime.runtime
    mem = runtime.memory.data

    rt.exec(DITER_EXPORTS["init"], [])
    dict_ptr = rt.exec(DITER_EXPORTS["load_dict"], [len(params.b)])
    mem[dict_ptr:dict_ptr + len(params.b)] = params.b
    rt.exec(DITER_EXPORTS["pump"], [])

    output = bytearray()
    for offset in range(0, len(binz_bytes), 10240):
        chunk = binz_bytes[offset:offset + 10240]
        if not chunk:
            continue
        chunk_ptr = rt.exec(DITER_EXPORTS["load_chunk"], [len(chunk)])
        mem[chunk_ptr:chunk_ptr + len(chunk)] = chunk

        has_output = rt.exec(DITER_EXPORTS["pump"], [])
        while has_output:
            out_ptr = rt.exec(DITER_EXPORTS["out_ptr"], [])
            out_len = rt.exec(DITER_EXPORTS["out_len"], [])
            if out_len:
                output.extend(mem[out_ptr:out_ptr + out_len])
            rt.exec(DITER_EXPORTS["out_advance"], [])
            has_output = rt.exec(DITER_EXPORTS["pump"], [])

    return bytes(output)


def decode_diter_file(
    binz_path: Path,
    params_path: Path,
    output_path: Path,
    *,
    wasm_path: Optional[Path] = None,
    wasm_b64_path: Optional[Path] = None,
    key_hex: Optional[str] = None,
    key_source: Optional[Path] = None,
) -> int:
    params = _parse_params(params_path)
    binz_bytes = binz_path.read_bytes()
    decoded = decode_diter_bytes(
        binz_bytes,
        params,
        wasm_path=wasm_path,
        wasm_b64_path=wasm_b64_path,
        key_hex=key_hex,
        key_source=key_source,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(decoded)
    return len(decoded)
