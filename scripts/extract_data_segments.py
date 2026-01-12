#!/usr/bin/env python3
"""
Extract wasm2c data segments from legacy/diter_core.c into JSON.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


def parse_segment_bytes(text: str, name: str) -> list[int]:
    match = re.search(rf"{re.escape(name)}\[\]\s*=\s*\{{(.*?)\}};", text, re.S)
    if not match:
        raise ValueError(f"Missing segment {name}")
    blob = match.group(1)
    values = []
    for token in re.findall(r"0x[0-9a-fA-F]+|\\d+", blob):
        values.append(int(token, 16) if token.startswith("0x") else int(token))
    return values


def parse_loads(text: str) -> list[tuple[int, str, int]]:
    loads = []
    for line in text.splitlines():
        line = line.strip()
        if "LOAD_DATA((*instance->env_memory)" in line:
            # LOAD_DATA((*instance->env_memory), 1024u, data_segment_data_diter_core_d0, 2944);
            parts = line.split(",")
            if len(parts) >= 4:
                offset = int(parts[1].strip().rstrip("u"))
                seg_name = parts[2].strip()
                length = int(parts[3].strip().rstrip("u);"))
                loads.append((offset, seg_name, length))
    return loads


def main() -> None:
    src = Path("legacy/diter_core.c")
    out = Path("build/diter_core_data_segments.json")
    text = src.read_text(encoding="utf-8", errors="replace")
    loads = parse_loads(text)
    segments = []
    for offset, seg_name, length in loads:
        data = parse_segment_bytes(text, seg_name)
        if length != len(data):
            data = data[:length]
        segments.append({
            "name": seg_name,
            "offset": offset,
            "size": length,
            "bytes": data,
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"segments": segments}, indent=2), encoding="utf-8")
    print(f"Wrote {out} with {len(segments)} segments")


if __name__ == "__main__":
    main()
