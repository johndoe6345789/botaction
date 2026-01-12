#!/usr/bin/env python3
"""
WASM De-noiser v2: Clean up Sketchfab's DITER codec for AI understanding.

Based on analysis of the JS wrapper, the exported functions are:
- heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl -> allocate(size) - allocate buffer, returns pointer
- mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l -> init() - initialize decoder state
- Umlja1JvbGxlZDRV -> "RickRolled4U" - set_key(ptr, len) - set decryption key
- dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI -> write_dict(size) - write dictionary, returns ptr
- GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW -> get_dict_ptr() - get dictionary pointer
- FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN -> pump(mode) - process data, returns status
- bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg -> output_size() - get output buffer size
- TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT -> output_ptr() - get output buffer pointer

The algorithm appears to be a dictionary-based decompression codec.
"""

import argparse
import re
from pathlib import Path

# Mapping of rickroll Base64 names to meaningful function names
# Based on analysis of diter_standalone_deob.js usage patterns
FUNCTION_MAP = {
    # Exported API functions (rickroll names)
    "heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl": "alloc",           # allocate(size) -> ptr
    "mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l": "init",          # init() - reset state
    "Umlja1JvbGxlZDRV": "set_key",                           # RickRolled4U - set_key(ptr, len)
    "dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI": "write_dict",      # write_dict(size) -> ptr
    "GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW": "get_dict_ptr",    # get_dict_ptr() -> ptr
    "FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN": "pump",            # pump(mode) -> status
    "bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg": "output_size",        # output_size() -> size
    "TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT": "output_ptr",      # output_ptr() -> ptr
    "__wasm_call_ctors": "wasm_init",                        # WASM constructors
}

# Common WASM runtime function patterns
RUNTIME_PATTERNS = {
    r'env\.abort': 'abort',
    r'env\.sbrk': 'heap_grow',
    r'env\.memory': 'memory',
}


def analyze_function_body(name: str, body: str) -> str:
    """Try to classify a function by its body content."""
    # Count operations
    loads = body.count('i32.load') + body.count('i64.load')
    stores = body.count('i32.store') + body.count('i64.store')
    calls = body.count('call $')
    loops = body.count('loop') + body.count('br ')
    bitops = body.count('i32.and') + body.count('i32.or') + body.count('i32.xor') + body.count('i32.shl') + body.count('i32.shr')

    # Classify by pattern
    if loops > 3 and bitops > 5:
        return 'decompress_loop'
    elif loads > 10 and stores > 10:
        return 'memcpy_or_buffer'
    elif bitops > 10:
        return 'bitwise_op'
    elif calls > 5 and loops == 0:
        return 'dispatcher'
    elif stores > loads * 2:
        return 'writer'
    elif loads > stores * 2:
        return 'reader'

    return None


def clean_wat_for_ai(content: str, verbose: bool = False) -> str:
    """Clean WAT file to be AI-readable."""

    lines = content.split('\n')
    output_lines = []

    # Track function bodies for analysis
    current_func = None
    current_body = []
    func_count = 0
    renamed_count = 0

    # First pass: collect all functions and their bodies
    functions = {}
    in_func = False
    func_start = 0
    depth = 0

    for i, line in enumerate(lines):
        if '(func $' in line:
            match = re.search(r'\(func \$(\S+)', line)
            if match:
                current_func = match.group(1)
                func_start = i
                in_func = True
                depth = 1
                current_body = [line]
        elif in_func:
            current_body.append(line)
            depth += line.count('(') - line.count(')')
            if depth <= 0:
                functions[current_func] = {
                    'start': func_start,
                    'end': i,
                    'body': '\n'.join(current_body)
                }
                in_func = False
                current_func = None

    # Analyze and rename functions
    name_map = {}
    type_counters = {}

    for name, info in functions.items():
        # Check if it's a known rickroll name
        if name in FUNCTION_MAP:
            name_map[name] = FUNCTION_MAP[name]
            renamed_count += 1
            if verbose:
                print(f"  {name[:30]:30} -> {FUNCTION_MAP[name]} (API)")
        # Check if it's already a clean name
        elif name.startswith('f') and name[1:].isdigit():
            # Try to classify by body
            func_type = analyze_function_body(name, info['body'])
            if func_type:
                type_counters[func_type] = type_counters.get(func_type, 0) + 1
                new_name = f"{func_type}_{type_counters[func_type]:02d}"
                name_map[name] = new_name
                renamed_count += 1
                if verbose:
                    print(f"  {name:30} -> {new_name} (classified)")
            else:
                name_map[name] = name  # Keep as-is
        elif name.startswith('fn_'):
            # Already renamed in v1, try to classify
            func_type = analyze_function_body(name, info['body'])
            if func_type:
                type_counters[func_type] = type_counters.get(func_type, 0) + 1
                new_name = f"{func_type}_{type_counters[func_type]:02d}"
                name_map[name] = new_name
                if verbose:
                    print(f"  {name:30} -> {new_name} (classified)")
            else:
                name_map[name] = name
        else:
            # Unknown name, might be rickroll or other obfuscation
            name_map[name] = name

    # Second pass: replace names in content
    cleaned = content

    # Replace function definitions and calls
    for old_name, new_name in name_map.items():
        if old_name != new_name:
            # Replace function definition
            cleaned = re.sub(
                rf'\(func \${re.escape(old_name)}(\s)',
                f'(func ${new_name}\\1',
                cleaned
            )
            # Replace calls
            cleaned = re.sub(
                rf'call \${re.escape(old_name)}(\s|\))',
                f'call ${new_name}\\1',
                cleaned
            )
            # Replace exports
            cleaned = re.sub(
                rf'\(export "[^"]*" \(func \${re.escape(old_name)}\)\)',
                f'(export "{new_name}" (func ${new_name}))',
                cleaned
            )

    # Add header comment explaining the API
    header = ''';;
;; DITER Decompression Codec - Cleaned for AI Analysis
;;
;; This is Sketchfab's proprietary geometry decompression algorithm.
;; Originally obfuscated with Base64-encoded rickroll lyrics as function names.
;;
;; PUBLIC API:
;;   init()              - Initialize/reset decoder state
;;   alloc(size) -> ptr  - Allocate buffer in WASM memory
;;   set_key(ptr, len)   - Set decryption key (optional)
;;   write_dict(size)    - Write dictionary data, returns pointer
;;   get_dict_ptr()      - Get current dictionary pointer
;;   pump(mode) -> stat  - Process data (mode: 0=continue, 1=flush)
;;   output_ptr() -> ptr - Get output buffer start
;;   output_size() -> n  - Get output buffer size
;;
;; ALGORITHM: Appears to be LZ-family dictionary compression
;;   - Uses sliding window/dictionary for backreferences
;;   - Supports optional AES-like key for encrypted streams
;;   - Processes data in chunks via pump() calls
;;

'''

    cleaned = header + cleaned

    if verbose:
        print(f"\nRenamed {renamed_count} functions")
        print(f"Function type distribution:")
        for ftype, count in sorted(type_counters.items(), key=lambda x: -x[1]):
            print(f"  {ftype}: {count}")

    return cleaned


def extract_algorithm_summary(content: str) -> str:
    """Extract a high-level summary of the algorithm for AI."""

    summary = []
    summary.append("=" * 60)
    summary.append("DITER ALGORITHM SUMMARY")
    summary.append("=" * 60)
    summary.append("")
    summary.append("1. INITIALIZATION")
    summary.append("   - init() resets decoder state")
    summary.append("   - Optional: set_key() for encrypted streams")
    summary.append("")
    summary.append("2. DICTIONARY SETUP")
    summary.append("   - write_dict(size) allocates dictionary buffer")
    summary.append("   - Dictionary contains backreference data")
    summary.append("")
    summary.append("3. DECOMPRESSION LOOP")
    summary.append("   - alloc(chunk_size) to get input buffer")
    summary.append("   - Copy compressed data to buffer")
    summary.append("   - pump(1) to process chunk")
    summary.append("   - Read output from output_ptr(), output_size()")
    summary.append("   - Repeat until pump() returns 0")
    summary.append("")
    summary.append("4. KEY OBSERVATIONS")

    # Count patterns in code
    bitops = content.count('i32.and') + content.count('i32.or') + content.count('i32.xor')
    shifts = content.count('i32.shl') + content.count('i32.shr')
    loops = content.count('(loop')

    summary.append(f"   - {bitops} bitwise operations (compression bit manipulation)")
    summary.append(f"   - {shifts} shift operations (variable-length encoding)")
    summary.append(f"   - {loops} loops (main decompression iterations)")
    summary.append("")
    summary.append("This appears to be an LZ77/LZSS variant with:")
    summary.append("   - Dictionary-based backreferences")
    summary.append("   - Variable-length encoded lengths/offsets")
    summary.append("   - Optional encryption layer")
    summary.append("")
    summary.append("=" * 60)

    return '\n'.join(summary)


def main():
    parser = argparse.ArgumentParser(
        description='De-noise DITER WASM for AI understanding'
    )
    parser.add_argument('--wat', required=True, help='Input WAT file')
    parser.add_argument('--output', '-o', help='Output cleaned WAT file')
    parser.add_argument('--summary', '-s', action='store_true',
                        help='Print algorithm summary')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show renamed functions')

    args = parser.parse_args()

    input_path = Path(args.wat)
    content = input_path.read_text()

    print(f"Processing: {input_path}")
    print(f"Size: {len(content):,} bytes")

    if args.summary:
        print(extract_algorithm_summary(content))
        return 0

    cleaned = clean_wat_for_ai(content, verbose=args.verbose)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(cleaned)
        print(f"\nOutput: {output_path}")
        print(f"Size: {len(cleaned):,} bytes")
    else:
        # Print first part
        print("\n" + "=" * 60)
        print("CLEANED OUTPUT (first 3000 chars):")
        print("=" * 60)
        print(cleaned[:3000])
        print("\n... (use --output to save full file)")

    return 0


if __name__ == '__main__':
    exit(main())
