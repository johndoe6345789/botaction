#!/usr/bin/env python3
"""Quick helper to dump all top-level function definitions from cli.py."""

from pathlib import Path
import ast


def main():
    src_path = Path("cli.py")
    dest_dir = Path("src/cli_function_dumps")
    source = src_path.read_text()
    tree = ast.parse(source)

    dest_dir.mkdir(parents=True, exist_ok=True)

    functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("cmd_")
    ]

    header = (
        "# Auto-generated extract of cli.py\n"
        "# See cli.py for shared context and imports\n"
        "from src.cli_context import *\n\n"
    )

    for node in functions:
        snippet = ast.get_source_segment(source, node) or ""
        if not snippet.strip():
            continue

        file_path = dest_dir / f"{node.name}.py"
        file_path.write_text(
            header + snippet.strip() + "\n"
        )

    print(f"Wrote {len(functions)} function(s) to {dest_dir}")


if __name__ == "__main__":
    main()
