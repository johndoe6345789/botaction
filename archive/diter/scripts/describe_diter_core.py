#!/usr/bin/env python3
import json
import re
from pathlib import Path


def extract_functions(source: str):
    funcs = {}
    pattern = re.compile(r"^\\s*(?:static\\s+)?(?:inline\\s+)?(?:void|u32|s32|u64|s64|f32|f64|int|long)\\s+(diter_core_[A-Za-z0-9_]+)\\s*\\([^)]*\\)\\s*\\{", re.M)
    for match in pattern.finditer(source):
        name = match.group(1)
        start = match.end()
        tail = source[start:]
        next_match = re.search(r"\\n\\s*(?:static\\s+)?(?:inline\\s+)?(?:void|u32|s32|u64|s64|f32|f64|int|long)\\s+diter_core_[A-Za-z0-9_]+\\s*\\(", tail)
        end = next_match.start() if next_match else len(tail)
        body = tail[:end]
        calls = sorted(set(re.findall(r"\\b(diter_core_[A-Za-z0-9_]+)\\b", body)) - {name})
        funcs[name] = {
            "calls": calls,
        }
    return funcs


def extract_exports(header: str):
    exports = []
    for match in re.finditer(r"^/\* export: '([^']+)' \*/\s*\n\s*(?:void|u32)\s+(diter_core_[A-Za-z0-9_]+)\(", header, re.M):
        exports.append({
            "export_name": match.group(1),
            "function": match.group(2),
        })
    return exports


def extract_data_segments(source: str):
    segments = []
    for match in re.finditer(r"static const u8 (data_segment_data_[A-Za-z0-9_]+)\\[(\\d+)\\]", source):
        segments.append({
            "name": match.group(1),
            "size": int(match.group(2)),
        })
    return segments


def main():
    core_c = Path("src/diter_core.c")
    core_h = Path("src/diter_core.h")
    if not core_c.exists() or not core_h.exists():
        raise SystemExit("Missing src/diter_core.c or src/diter_core.h")

    source = core_c.read_text(encoding="utf-8", errors="replace")
    header = core_h.read_text(encoding="utf-8", errors="replace")

    funcs = extract_functions(source)
    exports = extract_exports(header)
    data_segments = extract_data_segments(source)

    export_summary = []
    for item in exports:
        fn = item["function"]
        export_summary.append({
            "export_name": item["export_name"],
            "function": fn,
            "calls": funcs.get(fn, {}).get("calls", []),
        })

    out = {
        "exports": export_summary,
        "data_segments": data_segments,
        "function_count": len(funcs),
    }

    out_path = Path("build/diter_core_declarative.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
