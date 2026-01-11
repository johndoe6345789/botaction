"""
Build and run the native C DITER decoder.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


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


def build_decoder(build_dir: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[1]
    build_dir = build_dir or (root / "build" / "diter_decode_c")
    build_dir.mkdir(parents=True, exist_ok=True)

    cc = _resolve_cc()
    if not cc:
        raise RuntimeError("C compiler not found (need cc/gcc/clang).")

    exe_name = "diter_decode_c.exe" if os.name == "nt" else "diter_decode_c"
    exe = build_dir / exe_name
    src_dir = root / "src"
    wasm2c_c = src_dir / "diter_wasm_blob_wasm2c.c"
    wasm2c_h = src_dir / "diter_wasm_blob_wasm2c.h"
    rt_impl = src_dir / "wasm_rt" / "wasm-rt-impl.c"
    wrapper = src_dir / "diter_decode_c.c"
    engine = src_dir / "diter_engine.c"
    if _needs_rebuild(exe, [wasm2c_c, wasm2c_h, rt_impl, wrapper, engine]):
        cmd = [
            cc,
            "-O2",
            "-std=c11",
            "-I",
            str(src_dir / "wasm_rt"),
            "-I",
            str(src_dir),
            "-o",
            str(exe),
            str(wrapper),
            str(engine),
            str(wasm2c_c),
            str(rt_impl),
        ]
        subprocess.run(cmd, check=True)
    return exe


def decode_diter_file(
    binz_path: Path,
    params_path: Path,
    output_path: Path,
    *,
    wasm_path: Path | None = None,
    key_hex: str | None = None,
    key_source: Path | None = None,
) -> int:
    exe = build_decoder()
    cmd = [
        str(exe),
        "--binz",
        str(binz_path),
        "--params",
        str(params_path),
        "--out",
        str(output_path),
    ]
    if key_hex:
        cmd += ["--key-hex", key_hex]
    if key_source:
        cmd += ["--key-source", str(key_source)]
    subprocess.run(cmd, check=True)
    return output_path.stat().st_size if output_path.exists() else 0
