#!/usr/bin/env python3
"""
Namespace workflow node names/ids and connections to avoid collisions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def namespace_workflow(doc: dict, prefix: str) -> dict:
    nodes = doc.get("nodes", [])
    name_map = {}
    id_map = {}
    for node in nodes:
        old_name = node.get("name")
        if old_name:
            name_map[old_name] = f"{prefix}:{old_name}"
        old_id = node.get("id")
        if old_id:
            id_map[old_id] = f"{prefix}:{old_id}"

    for node in nodes:
        if node.get("name") in name_map:
            node["name"] = name_map[node["name"]]
        if node.get("id") in id_map:
            node["id"] = id_map[node["id"]]

    connections = doc.get("connections", {})
    if isinstance(connections, dict):
        new_connections = {}
        for src_name, by_type in connections.items():
            new_src = name_map.get(src_name, src_name)
            new_connections[new_src] = by_type
            for typ, outputs in by_type.items():
                for idx, targets in outputs.items():
                    for target in targets:
                        target_name = target.get("node")
                        if target_name in name_map:
                            target["node"] = name_map[target_name]
        doc["connections"] = new_connections

    return doc


def main() -> None:
    parser = argparse.ArgumentParser(description="Namespace workflow JSON files.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--prefix", default=None, help="Prefix for node names/ids.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(input_dir.glob("*.json")):
        prefix = args.prefix or path.stem
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc = namespace_workflow(doc, prefix)
        out_path = output_dir / path.name
        out_path.write_text(json.dumps(doc, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
