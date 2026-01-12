#!/usr/bin/env python3
"""
WASM De-noiser v3: Deep analysis of DITER codec for AI understanding.

This version:
1. Traces call graphs to find the real implementation
2. Identifies state machine patterns
3. Extracts the core decompression loop
4. Generates pseudocode summary
"""

import argparse
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set, Optional


@dataclass
class WasmFunc:
    name: str
    params: List[str]
    result: Optional[str]
    locals: List[str]
    body: str
    line_start: int
    line_end: int
    calls: Set[str]  # Functions this calls
    called_by: Set[str]  # Functions that call this

    # Analysis results
    loads: int = 0
    stores: int = 0
    bitops: int = 0
    branches: int = 0
    is_leaf: bool = False
    category: str = ""


# Known API function mappings
API_FUNCTIONS = {
    "heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl": ("alloc", "Allocate buffer, returns pointer"),
    "mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l": ("init", "Initialize/reset decoder state"),
    "Umlja1JvbGxlZDRV": ("set_key", "Set decryption key (RickRolled4U)"),
    "dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI": ("write_dict", "Write dictionary data"),
    "GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW": ("get_dict_ptr", "Get dictionary pointer"),
    "FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN": ("pump", "Process compressed data"),
    "bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg": ("output_size", "Get output buffer size"),
    "TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT": ("output_ptr", "Get output buffer pointer"),
}


def parse_wat(content: str) -> Dict[str, WasmFunc]:
    """Parse WAT file into function objects."""
    functions = {}
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for function definition
        match = re.match(r'\s*\(func \$(\S+)\s+\(type \$\w+\)', line)
        if match:
            func_name = match.group(1)
            func_start = i

            # Parse params and result from type
            params = re.findall(r'\(param \$\w+ (\w+)\)', line)
            result_match = re.search(r'\(result (\w+)\)', line)
            result = result_match.group(1) if result_match else None

            # Parse locals
            locals_match = re.findall(r'\(local \$\w+ (\w+)\)', line)

            # Find function body (until matching close paren)
            depth = line.count('(') - line.count(')')
            body_lines = [line]
            i += 1

            while i < len(lines) and depth > 0:
                body_lines.append(lines[i])
                depth += lines[i].count('(') - lines[i].count(')')
                i += 1

            body = '\n'.join(body_lines)

            # Find calls
            calls = set(re.findall(r'call \$(\S+)', body))

            # Count operations
            loads = body.count('.load')
            stores = body.count('.store')
            bitops = body.count('.and') + body.count('.or') + body.count('.xor') + body.count('.shl') + body.count('.shr')
            branches = body.count('br_if') + body.count('br ') + body.count('if ')

            functions[func_name] = WasmFunc(
                name=func_name,
                params=params,
                result=result,
                locals=locals_match,
                body=body,
                line_start=func_start,
                line_end=i,
                calls=calls,
                called_by=set(),
                loads=loads,
                stores=stores,
                bitops=bitops,
                branches=branches,
                is_leaf=len(calls) == 0,
            )
        else:
            i += 1

    # Build called_by relationships
    for name, func in functions.items():
        for called in func.calls:
            if called in functions:
                functions[called].called_by.add(name)

    return functions


def categorize_functions(functions: Dict[str, WasmFunc]) -> None:
    """Categorize functions by their behavior."""
    for name, func in functions.items():
        # Check if it's an API wrapper
        if name in [v[0] for v in API_FUNCTIONS.values()]:
            func.category = "api"
        elif any(name == orig for orig in API_FUNCTIONS.keys()):
            func.category = "api"
        # Memory management
        elif 'sbrk' in func.body or 'memory.grow' in func.body:
            func.category = "memory_mgmt"
        # Heavy computation (likely core algorithm)
        elif func.bitops > 20 and func.branches > 10:
            func.category = "core_decompress"
        elif func.bitops > 10:
            func.category = "bit_reader"
        # Data movement
        elif func.loads > 20 and func.stores > 20:
            func.category = "buffer_copy"
        elif func.stores > func.loads * 2:
            func.category = "writer"
        elif func.loads > func.stores * 2:
            func.category = "reader"
        # Control flow
        elif func.branches > 10 and func.bitops < 5:
            func.category = "state_machine"
        # Simple helpers
        elif func.is_leaf and len(func.body) < 500:
            func.category = "helper"
        else:
            func.category = "unknown"


def trace_api_implementation(functions: Dict[str, WasmFunc], api_name: str) -> List[str]:
    """Trace what functions an API call actually uses."""
    if api_name not in functions:
        return []

    visited = set()
    trace = []

    def visit(name: str, depth: int = 0):
        if name in visited or name.startswith('env.'):
            return
        visited.add(name)

        if name in functions:
            func = functions[name]
            trace.append((depth, name, func.category, len(func.body)))
            for called in sorted(func.calls):
                visit(called, depth + 1)

    visit(api_name)
    return trace


def generate_pseudocode(func: WasmFunc) -> str:
    """Generate readable pseudocode from WAT."""
    # This is a simplified version - real decompilation is complex
    pseudo = []
    pseudo.append(f"function {func.name}({', '.join(func.params)}):")

    # Identify key patterns
    if 'i32.const 4104' in func.body:
        pseudo.append("  state = global_state[4104]  // State structure at fixed address")

    # Look for common patterns
    if func.bitops > 10:
        pseudo.append("  // Bit manipulation (likely varint/huffman decoding)")
        if 'i32.and' in func.body and 'i32.shr' in func.body:
            pseudo.append("  bits = read_bits()")
            pseudo.append("  value = bits & mask")
            pseudo.append("  bits >>= shift")

    if func.loads > 10 and func.stores > 10:
        pseudo.append("  // Buffer operations")
        pseudo.append("  copy_bytes(src, dst, len)")

    if 'call $' in func.body:
        calls = re.findall(r'call \$(\S+)', func.body)
        unique_calls = sorted(set(calls))
        pseudo.append(f"  // Calls: {', '.join(unique_calls[:5])}")

    return '\n'.join(pseudo)


def generate_algorithm_report(functions: Dict[str, WasmFunc]) -> str:
    """Generate a comprehensive algorithm report."""
    lines = []
    lines.append("=" * 70)
    lines.append("DITER DECOMPRESSION ALGORITHM - DETAILED ANALYSIS")
    lines.append("=" * 70)
    lines.append("")

    # Count categories
    categories = defaultdict(list)
    for name, func in functions.items():
        categories[func.category].append(name)

    lines.append("FUNCTION CATEGORIES:")
    lines.append("-" * 40)
    for cat, funcs in sorted(categories.items(), key=lambda x: -len(x[1])):
        lines.append(f"  {cat:20} {len(funcs):3} functions")
    lines.append("")

    # API trace
    lines.append("API IMPLEMENTATION TRACES:")
    lines.append("-" * 40)

    for old_name, (new_name, desc) in API_FUNCTIONS.items():
        # Try both old and new names
        api_func = new_name if new_name in functions else old_name
        if api_func in functions:
            lines.append(f"\n{new_name}() - {desc}")
            trace = trace_api_implementation(functions, api_func)
            for depth, fname, cat, size in trace[:10]:
                indent = "  " * (depth + 1)
                lines.append(f"{indent}{fname} [{cat}] ({size} bytes)")
            if len(trace) > 10:
                lines.append(f"  ... and {len(trace) - 10} more functions")

    # Core algorithm identification
    lines.append("")
    lines.append("CORE ALGORITHM FUNCTIONS:")
    lines.append("-" * 40)

    core_funcs = [f for f in functions.values() if f.category == "core_decompress"]
    core_funcs.sort(key=lambda x: -(x.bitops + x.branches))

    for func in core_funcs[:5]:
        lines.append(f"\n{func.name}:")
        lines.append(f"  Bit operations: {func.bitops}")
        lines.append(f"  Branches: {func.branches}")
        lines.append(f"  Memory loads: {func.loads}")
        lines.append(f"  Memory stores: {func.stores}")
        lines.append(f"  Called by: {', '.join(list(func.called_by)[:3])}")
        lines.append(generate_pseudocode(func))

    # State machine analysis
    lines.append("")
    lines.append("STATE MACHINE FUNCTIONS:")
    lines.append("-" * 40)

    state_funcs = [f for f in functions.values() if f.category == "state_machine"]
    for func in state_funcs[:3]:
        lines.append(f"  {func.name}: {func.branches} branches, called by {len(func.called_by)} funcs")

    # Algorithm hypothesis
    lines.append("")
    lines.append("ALGORITHM HYPOTHESIS:")
    lines.append("-" * 40)
    lines.append("""
Based on the analysis:

1. STRUCTURE: Dictionary-based LZ compression
   - Global state at address 4104
   - Dictionary buffer for backreferences
   - Bit reader for variable-length codes

2. FLOW:
   init() -> Reset state machine
   write_dict() -> Load dictionary/sliding window
   pump() -> Main decompression loop:
     - Read variable-length codes (bit manipulation)
     - Either: literal byte or backreference (offset, length)
     - Copy bytes to output buffer
   output_ptr/size() -> Get decompressed data

3. KEY FUNCTIONS:
   - f152: Main dispatch (called by pump)
   - Core decompress functions: Heavy bitops + branches
   - Bit readers: Extract variable-length integers
   - Buffer copy: Move data for backreferences

4. ENCRYPTION (optional):
   - set_key() suggests AES-like XOR layer
   - Applied before/after compression
""")

    lines.append("=" * 70)
    return '\n'.join(lines)


def rewrite_wat_readable(content: str, functions: Dict[str, WasmFunc]) -> str:
    """Rewrite WAT with better names and comments."""

    # Build name mapping based on analysis
    name_map = {}
    category_counters = defaultdict(int)

    for name, func in functions.items():
        # Keep API names
        if func.category == "api":
            continue

        # Rename based on category
        cat = func.category
        category_counters[cat] += 1
        new_name = f"{cat}_{category_counters[cat]:02d}"
        name_map[name] = new_name

    # Apply renames
    result = content
    for old_name, new_name in name_map.items():
        result = result.replace(f'${old_name})', f'${new_name})')
        result = result.replace(f'${old_name} ', f'${new_name} ')
        result = result.replace(f'${old_name}\n', f'${new_name}\n')

    # Add header
    header = ''';;
;; DITER Decompression Codec - Deobfuscated for AI Analysis
;;
;; ALGORITHM: LZ-family dictionary compression with optional encryption
;;
;; MEMORY LAYOUT:
;;   [4104]: Global state structure
;;   - Input buffer pointer
;;   - Output buffer pointer
;;   - Dictionary/sliding window
;;   - Bit buffer for variable-length decoding
;;
;; FUNCTION CATEGORIES:
;;   api_*           - Public API wrappers
;;   core_decompress - Main decompression logic (bitops + branches)
;;   bit_reader      - Variable-length integer decoding
;;   buffer_copy     - Memory copy for backreferences
;;   state_machine   - Control flow dispatch
;;   memory_mgmt     - Heap allocation (sbrk wrapper)
;;   helper          - Small utility functions
;;

'''

    return header + result


def main():
    parser = argparse.ArgumentParser(
        description='Deep analysis and deobfuscation of DITER WASM'
    )
    parser.add_argument('--wat', required=True, help='Input WAT file')
    parser.add_argument('--output', '-o', help='Output cleaned WAT file')
    parser.add_argument('--report', '-r', action='store_true',
                        help='Generate detailed algorithm report')
    parser.add_argument('--trace', '-t', help='Trace specific function')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    input_path = Path(args.wat)
    content = input_path.read_text()

    print(f"Parsing: {input_path}")
    functions = parse_wat(content)
    print(f"Found {len(functions)} functions")

    print("Categorizing functions...")
    categorize_functions(functions)

    if args.trace:
        print(f"\nTracing {args.trace}:")
        trace = trace_api_implementation(functions, args.trace)
        for depth, name, cat, size in trace:
            indent = "  " * depth
            print(f"{indent}{name} [{cat}]")
        return 0

    if args.report:
        print(generate_algorithm_report(functions))
        return 0

    if args.output:
        print("Generating readable output...")
        cleaned = rewrite_wat_readable(content, functions)

        output_path = Path(args.output)
        output_path.write_text(cleaned)
        print(f"Written to: {output_path}")
        print(f"Size: {len(cleaned):,} bytes")
    else:
        # Print summary
        print(generate_algorithm_report(functions))

    return 0


if __name__ == '__main__':
    exit(main())
