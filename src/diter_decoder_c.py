"""
Build and run the wasm2c-based DITER decoder.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _resolve_tool(root: Path, name: str) -> str | None:
    local = root / "node_modules" / ".bin" / name
    if local.exists():
        return str(local)
    local_cmd = local.with_suffix(".cmd")
    if local_cmd.exists():
        return str(local_cmd)
    system = shutil.which(name)
    if system:
        return system
    return None


def _resolve_cc() -> str | None:
    for name in ("cc", "gcc", "clang"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def _needs_rebuild(output: Path, inputs: list[Path]) -> bool:
    if not output.exists():
        return True
    out_mtime = _mtime(output)
    return any(_mtime(path) > out_mtime for path in inputs if path.exists())


def build_decoder(wasm_path: Path, build_dir: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[1]
    build_dir = build_dir or (root / "build" / "diter_decode_c")
    build_dir.mkdir(parents=True, exist_ok=True)

    wasm2c = _resolve_tool(root, "wasm2c")
    if not wasm2c:
        raise RuntimeError("wasm2c not found (install wabt or npm dependency).")

    out_c = build_dir / "diter_wasm_blob_wasm2c.c"
    out_h = build_dir / "diter_wasm_blob_wasm2c.h"
    if _needs_rebuild(out_c, [wasm_path]):
        subprocess.run([wasm2c, str(wasm_path), "-o", str(out_c)], check=True)
        if not out_h.exists():
            raise RuntimeError("wasm2c output header missing.")

    cc = _resolve_cc()
    if not cc:
        raise RuntimeError("C compiler not found (need cc/gcc/clang).")

    exe_name = "diter_decode_c.exe" if os.name == "nt" else "diter_decode_c"
    exe = build_dir / exe_name
    src_dir = root / "src"
    rt_impl = src_dir / "wasm_rt" / "wasm-rt-impl.c"
    wrapper = src_dir / "diter_decode_c.c"
    if _needs_rebuild(exe, [out_c, out_h, rt_impl, wrapper]):
        cmd = [
            cc,
            "-O2",
            "-std=c11",
            "-I",
            str(src_dir / "wasm_rt"),
            "-I",
            str(build_dir),
            "-o",
            str(exe),
            str(wrapper),
            str(out_c),
            str(rt_impl),
        ]
        subprocess.run(cmd, check=True)
    return exe


def decode_diter_file(
    binz_path: Path,
    params_path: Path,
    output_path: Path,
    *,
    wasm_path: Path,
    key_hex: str | None = None,
    key_source: Path | None = None,
) -> int:
    exe = build_decoder(wasm_path)
    cmd = [
        str(exe),
        "--binz",
        str(binz_path),
        "--params",
        str(params_path),
        "--out",
        str(output_path),
        "--wasm",
        str(wasm_path),
    ]
    if key_hex:
        cmd += ["--key-hex", key_hex]
    if key_source:
        cmd += ["--key-source", str(key_source)]
    subprocess.run(cmd, check=True)
    return output_path.stat().st_size if output_path.exists() else 0
