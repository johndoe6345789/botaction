#!/usr/bin/env python3
"""
Generate an n8n-style JSON workflow from LLVM IR.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterator


def parse_instructions(ir_path: Path) -> Iterator[dict]:
    current_func = None
    index = 0
    with ir_path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith(";"):
                continue
            if stripped.startswith("define "):
                # Example: define void @foo(i32 %0) ...
                at = stripped.find("@")
                if at != -1:
                    end = stripped.find("(", at)
                    current_func = stripped[at + 1:end] if end != -1 else stripped[at + 1:]
                    index = 0
                continue
            if stripped == "}":
                current_func = None
                continue
            if current_func is None:
                continue

            op = ""
            dest = ""
            if stripped.endswith(":"):
                op = "label"
            else:
                if "=" in stripped:
                    left, right = stripped.split("=", 1)
                    dest = left.strip()
                    op = right.strip().split()[0]
                else:
                    op = stripped.split()[0]

            yield {
                "function": current_func,
                "index": index,
                "op": op,
                "dest": dest,
                "text": stripped,
            }
            index += 1


def write_workflow(parts_dir: Path, manifest_path: Path, ir_path: Path, max_nodes: int) -> None:
    parts_dir.mkdir(parents=True, exist_ok=True)
    nodes = []
    connections: dict[str, dict] = {}
    parts = []
    part_index = 1
    prev_name = None

    def flush_part() -> None:
        nonlocal nodes, connections, part_index
        if not nodes:
            return
        part_path = parts_dir / f"part_{part_index:04d}.json"
        part_doc = {
            "nodes": nodes,
            "connections": connections,
        }
        part_path.write_text(json.dumps(part_doc, indent=2), encoding="utf-8")
        parts.append(str(part_path.relative_to(manifest_path.parent)))
        nodes = []
        connections = {}
        part_index += 1

    for inst in parse_instructions(ir_path):
        name = f"{inst['function']}:{inst['index']}"
        node = {
            "id": f"{inst['function']}:{inst['index']}",
            "name": name,
            "type": "llvm.instruction",
            "typeVersion": 1,
            "position": [200 + (inst["index"] % 6) * 240, 200 + (inst["index"] // 6) * 120],
            "parameters": {
                "function": inst["function"],
                "op": inst["op"],
                "dest": inst["dest"] or None,
                "text": inst["text"],
            },
        }
        nodes.append(node)

        if prev_name is not None:
            connections.setdefault(prev_name, {"main": {"0": []}})
            connections[prev_name]["main"]["0"].append({
                "node": name,
                "type": "main",
                "index": 0,
            })
        prev_name = name

        if len(nodes) >= max_nodes:
            flush_part()

    flush_part()

    manifest = {
        "name": "Diter LLVM Workflow",
        "active": False,
        "parts": parts,
        "meta": {
            "source": str(ir_path),
            "type": "llvm-ir",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LLVM IR workflow JSON.")
    parser.add_argument("--ir", required=True)
    parser.add_argument("--parts-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--max-nodes", type=int, default=2000)
    args = parser.parse_args()

    ir_path = Path(args.ir)
    parts_dir = Path(args.parts_dir)
    manifest_path = Path(args.manifest)
    write_workflow(parts_dir, manifest_path, ir_path, args.max_nodes)


if __name__ == "__main__":
    main()
