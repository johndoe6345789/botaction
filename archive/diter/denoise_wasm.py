#!/usr/bin/env python3
"""
WASM De-noiser: Clean up Sketchfab's rickroll-obfuscated DITER codec.

The DITER WASM has function names encoded as Base64 rickroll lyrics.
This tool decodes them and attempts to identify the actual algorithm.

Usage:
    python denoise_wasm.py --wat diter_wasm_blob.wat --output cleaned.wat
    python denoise_wasm.py --c diter_wasm_blob_wasm2c.c --output cleaned.c
"""

import argparse
import base64
import re
from pathlib import Path
from collections import Counter


def decode_rickroll_name(b64_name: str) -> tuple[str, str]:
    """Decode a Base64 function name and return (decoded_lyrics, clean_name)."""
    # The names are fragments of rickroll lyrics in Base64
    # Try various padding and prefix combinations
    attempts = [
        b64_name,
        'N' + b64_name,  # Common prefix for "Never"
        b64_name.replace('_', '+').replace('-', '/'),
    ]

    for attempt in attempts:
        try:
            # Pad if needed
            padding_needed = 4 - len(attempt) % 4
            if padding_needed != 4:
                attempt = attempt + '=' * padding_needed

            decoded = base64.b64decode(attempt).decode('utf-8', errors='replace')
            # Check if it looks like text
            if any(phrase in decoded.lower() for phrase in ['gonna', 'never', 'you', 'give', 'let', 'down', 'cry', 'goodbye', 'hurt', 'lie']):
                lyrics = decoded.replace('\n', ' ').strip()[:60]
                return lyrics, None
        except Exception:
            continue

    # Try to decode anyway and show what we get
    try:
        padded = b64_name + '=' * (4 - len(b64_name) % 4) if len(b64_name) % 4 else b64_name
        decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
        return decoded.replace('\n', ' ').strip()[:60], None
    except Exception:
        return "(decode failed)", None


def analyze_wat(content: str) -> dict:
    """Analyze WAT file and extract function info."""
    # Find all function definitions
    func_pattern = r'\(func \$([A-Za-z0-9+/=_]+)'
    matches = re.findall(func_pattern, content)

    results = {
        'total_functions': len(matches),
        'rickroll_functions': [],
        'normal_functions': [],
        'decoded_lyrics': [],
    }

    for name in matches:
        if len(name) > 20 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in name):
            lyrics, _ = decode_rickroll_name(name)
            results['rickroll_functions'].append(name)
            results['decoded_lyrics'].append((name[:30] + '...', lyrics))
        else:
            results['normal_functions'].append(name)

    return results


def clean_wat(content: str, verbose: bool = False) -> str:
    """Replace rickroll Base64 names with clean function names."""
    func_counter = Counter()
    name_map = {}

    def classify_function(name: str, context: str) -> str:
        """Try to classify function by its context/usage."""
        # Look for clues in nearby code
        if 'i32.load' in context or 'i32.store' in context:
            return 'mem'
        if 'call' in context:
            return 'call'
        if 'loop' in context or 'br' in context:
            return 'loop'
        return 'func'

    def replace_name(match):
        name = match.group(1)
        if name in name_map:
            return f'${name_map[name]}'

        # Check if it's a rickroll name
        if len(name) > 20:
            try:
                padded = name + '=' * (4 - len(name) % 4) if len(name) % 4 else name
                decoded = base64.b64decode(padded)
                # It's Base64 - give it a clean name
                prefix = 'fn'
                func_counter[prefix] += 1
                clean_name = f'{prefix}_{func_counter[prefix]:03d}'
                name_map[name] = clean_name

                if verbose:
                    lyrics = decoded.decode('utf-8', errors='ignore')[:40].replace('\n', ' ')
                    print(f'  {clean_name}: "{lyrics}..."')

                return f'${clean_name}'
            except Exception:
                pass

        return match.group(0)

    # Replace function names
    cleaned = re.sub(r'\$([A-Za-z0-9+/=]{20,})', replace_name, content)

    return cleaned


def clean_c(content: str, verbose: bool = False) -> str:
    """Clean up wasm2c generated C code."""
    name_map = {}
    counter = [0]

    def replace_name(match):
        name = match.group(1)
        if name in name_map:
            return name_map[name]

        if len(name) > 20:
            try:
                # wasm2c mangles names, try to extract Base64 part
                padded = name + '=' * (4 - len(name) % 4) if len(name) % 4 else name
                base64.b64decode(padded)
                counter[0] += 1
                clean_name = f'fn_{counter[0]:03d}'
                name_map[name] = clean_name
                return clean_name
            except Exception:
                pass

        return name

    # Replace long identifiers that look like Base64
    cleaned = re.sub(r'\b([A-Za-z0-9_]{30,})\b', replace_name, content)

    # Remove excessive whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    if verbose:
        print(f'  Renamed {counter[0]} obfuscated identifiers')

    return cleaned


def print_rickroll_analysis(results: dict):
    """Print fun analysis of the rickroll obfuscation."""
    print("\n" + "=" * 60)
    print("RICKROLL OBFUSCATION ANALYSIS")
    print("=" * 60)
    print(f"\nTotal functions: {results['total_functions']}")
    print(f"Rickroll-named: {len(results['rickroll_functions'])}")
    print(f"Normal names:   {len(results['normal_functions'])}")

    if results['decoded_lyrics']:
        print("\nSample decoded lyrics:")
        print("-" * 60)
        for name, lyrics in results['decoded_lyrics'][:10]:
            print(f"  {name}")
            print(f"    -> \"{lyrics}\"")

        if len(results['decoded_lyrics']) > 10:
            print(f"  ... and {len(results['decoded_lyrics']) - 10} more")

    print("\n" + "=" * 60)
    print("Never gonna give you up, never gonna let you down...")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='De-noise Sketchfab DITER WASM (decode rickroll obfuscation)'
    )
    parser.add_argument('--wat', help='Input WAT file')
    parser.add_argument('--c', help='Input C file (from wasm2c)')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--analyze', '-a', action='store_true',
                        help='Analyze only, show rickroll stats')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show renamed functions')

    args = parser.parse_args()

    if not args.wat and not args.c:
        parser.print_help()
        return 1

    if args.wat:
        input_path = Path(args.wat)
        content = input_path.read_text()

        if args.analyze:
            results = analyze_wat(content)
            print_rickroll_analysis(results)
            return 0

        print(f"Cleaning WAT: {input_path}")
        cleaned = clean_wat(content, verbose=args.verbose)

    elif args.c:
        input_path = Path(args.c)
        content = input_path.read_text()

        print(f"Cleaning C: {input_path}")
        cleaned = clean_c(content, verbose=args.verbose)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(cleaned)

        original_size = len(content)
        cleaned_size = len(cleaned)
        reduction = (1 - cleaned_size / original_size) * 100

        print(f"\nOutput: {output_path}")
        print(f"Size: {original_size:,} -> {cleaned_size:,} bytes ({reduction:.1f}% reduction)")
    else:
        print(cleaned[:2000])
        print("\n... (use --output to save full file)")

    return 0


if __name__ == '__main__':
    exit(main())
