#!/usr/bin/env python3
import json
import math
import re
from pathlib import Path


def extract_exports(header: str):
    exports = {}
    pattern = re.compile(r"^/\* export: '([^']+)' \*/\s*\n\s*(?:void|u32)\s+(diter_core_[A-Za-z0-9_]+)\(", re.M)
    for match in pattern.finditer(header):
        exports[match.group(2)] = match.group(1)
    return exports


def extract_functions(source: str):
    funcs = []
    pattern = re.compile(r"^\s*(?:static\s+)?(?:inline\s+)?(?:void|u32|s32|u64|s64|f32|f64|int|long)\s+(diter_core_[A-Za-z0-9_]+)\s*\([^)]*\)\s*\{", re.M)
    for match in pattern.finditer(source):
        name = match.group(1)
        start = match.end()
        tail = source[start:]
        next_match = re.search(r"\n\s*(?:static\s+)?(?:inline\s+)?(?:void|u32|s32|u64|s64|f32|f64|int|long)\s+diter_core_[A-Za-z0-9_]+\s*\(", tail)
        end = next_match.start() if next_match else len(tail)
        body = tail[:end]
        calls = sorted(set(re.findall(r"\b(diter_core_[A-Za-z0-9_]+)\b", body)) - {name})
        funcs.append({
            "name": name,
            "calls": calls,
        })
    return funcs


def chunk_list(items, chunk_count):
    chunks = [[] for _ in range(chunk_count)]
    if not items:
        return chunks
    for idx, item in enumerate(items):
        chunks[idx % chunk_count].append(item)
    return chunks


def build_workflow(index, functions, exports):
    nodes = []
    connections = {}
    trigger_id = f"wf{index:03d}-trigger"
    trigger_node = {
        "id": trigger_id,
        "name": "Manual Trigger",
        "type": "trigger.manual",
        "typeVersion": 1,
        "position": [200, 200],
        "parameters": {},
    }
    nodes.append(trigger_node)

    prev_name = trigger_node["name"]
    x = 500
    y = 200
    for i, fn in enumerate(functions):
        node_id = f"wf{index:03d}-fn-{i:03d}"
        node_name = fn["name"]
        node = {
            "id": node_id,
            "name": node_name,
            "type": "analysis.function",
            "typeVersion": 1,
            "position": [x, y + i * 120],
            "parameters": {
                "function": fn["name"],
                "role": "export" if fn["name"] in exports else "internal",
                "exportName": exports.get(fn["name"]),
                "calls": fn["calls"],
            },
        }
        nodes.append(node)
        if prev_name not in connections:
            connections[prev_name] = {"main": {"0": []}}
        connections[prev_name]["main"]["0"].append({
            "node": node_name,
            "type": "main",
            "index": 0,
        })
        prev_name = node_name

    workflow = {
        "name": f"Diter Core Actions {index:03d}",
        "active": False,
        "nodes": nodes,
        "connections": connections,
        "tags": [{"name": "diter"}, {"name": "actions"}],
        "meta": {
            "source": "src/diter_core.c",
            "chunkIndex": index,
            "functionCount": len(functions),
        },
        "settings": {
            "timezone": "UTC",
            "saveExecutionProgress": True,
            "saveManualExecutions": True,
            "saveDataErrorExecution": "all",
            "saveDataSuccessExecution": "all",
            "saveDataManualExecution": "all",
        },
        "triggers": [
            {
                "nodeId": trigger_id,
                "kind": "manual",
                "enabled": True,
            }
        ],
    }
    return workflow


def main():
    core_c = Path("src/diter_core.c")
    core_h = Path("src/diter_core.h")
    if not core_c.exists() or not core_h.exists():
        raise SystemExit("Missing src/diter_core.c or src/diter_core.h")

    source = core_c.read_text(encoding="utf-8", errors="replace")
    header = core_h.read_text(encoding="utf-8", errors="replace")

    exports = extract_exports(header)
    functions = extract_functions(source)
    chunk_count = 100
    chunks = chunk_list(functions, chunk_count)

    out_dir = Path("build/runbooks/diter_core_workflows")
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, chunk in enumerate(chunks, start=1):
        workflow = build_workflow(i, chunk, exports)
        out_path = out_dir / f"diter_core_actions_{i:03d}.json"
        out_path.write_text(json.dumps(workflow, indent=2), encoding="utf-8")

    print(f"Wrote {len(chunks)} workflows to {out_dir}")


if __name__ == "__main__":
    main()
