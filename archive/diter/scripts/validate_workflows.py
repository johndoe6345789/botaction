#!/usr/bin/env python3
import json
from pathlib import Path


def validate_workflow(doc):
    errors = []
    if not isinstance(doc, dict):
        return ["workflow is not an object"]
    for key in ("name", "nodes", "connections"):
        if key not in doc:
            errors.append(f"missing required key: {key}")
    nodes = doc.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes must be a non-empty list")
        return errors
    names = set()
    ids = set()
    for node in nodes:
        if not isinstance(node, dict):
            errors.append("node is not an object")
            continue
        node_id = node.get("id")
        node_name = node.get("name")
        if not node_id or not node_name:
            errors.append("node missing id or name")
        if node_id in ids:
            errors.append(f"duplicate node id: {node_id}")
        if node_name in names:
            errors.append(f"duplicate node name: {node_name}")
        ids.add(node_id)
        names.add(node_name)
    connections = doc.get("connections", {})
    if not isinstance(connections, dict):
        errors.append("connections must be an object")
        return errors
    for src_name, by_type in connections.items():
        if src_name not in names:
            errors.append(f"connection source not found: {src_name}")
            continue
        if not isinstance(by_type, dict):
            errors.append(f"connection map invalid for: {src_name}")
            continue
        for typ, outputs in by_type.items():
            if not isinstance(outputs, dict):
                errors.append(f"connections {src_name}.{typ} invalid")
                continue
            for idx, targets in outputs.items():
                if not isinstance(targets, list):
                    errors.append(f"connections {src_name}.{typ}.{idx} invalid")
                    continue
                for target in targets:
                    node = target.get("node")
                    if node not in names:
                        errors.append(f"target node not found: {node}")
    return errors


def main():
    folder = Path("build/runbooks/diter_core_workflows")
    if not folder.exists():
        raise SystemExit(f"Missing {folder}")
    failures = 0
    for path in sorted(folder.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"{path}: invalid JSON ({exc})")
            failures += 1
            continue
        errors = validate_workflow(doc)
        if errors:
            failures += 1
            print(f"{path}:")
            for err in errors:
                print(f"  - {err}")
    if failures:
        raise SystemExit(f"{failures} workflow(s) failed validation")
    print("All workflows passed basic validation.")


if __name__ == "__main__":
    main()
