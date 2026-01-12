#!/usr/bin/env python3
"""
WASM De-noiser v4: Extract readable algorithm from DITER codec.

This version focuses on:
1. Decompiling the monster f172 function into readable pseudocode
2. Identifying specific LZ compression patterns
3. Creating a simplified algorithm description
4. Generating a "clean room" specification
"""

import argparse
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple


@dataclass
class BasicBlock:
    """A basic block of WASM instructions."""
    id: int
    instructions: List[str] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)
    predecessors: List[int] = field(default_factory=list)
    loop_header: bool = False
    is_exit: bool = False


@dataclass
class WasmLocal:
    """A local variable."""
    name: str
    type: str
    purpose: str = ""  # inferred purpose


@dataclass
class DecompiledFunction:
    """Decompiled function with pseudocode."""
    name: str
    params: List[WasmLocal]
    locals: List[WasmLocal]
    return_type: Optional[str]
    pseudocode: List[str]
    algorithm_hints: List[str]


# Patterns that indicate specific algorithm components
ALGORITHM_PATTERNS = {
    # Bit reading patterns
    'bit_buffer_check': r'i32\.const 32.*i32\.lt_u.*br_if',
    'bit_refill': r'i64\.load.*i64\.shl.*i64\.or',
    'extract_bits': r'i64\.and.*i64\.shr_u',

    # LZ patterns
    'distance_decode': r'i32\.sub.*i32\.and.*i32\.load8_u',
    'length_decode': r'i32\.add.*i32\.const 3',  # minimum match length
    'copy_loop': r'loop.*i32\.load8_u.*i32\.store8.*br',

    # Huffman patterns
    'table_lookup': r'i32\.shl.*i32\.add.*i32\.load',
    'symbol_decode': r'i32\.and.*i32\.const 15.*i32\.shr_u',

    # State machine patterns
    'state_switch': r'br_table',
    'state_store': r'i32\.store.*i32\.const 4104',
}


def extract_function_body(content: str, func_name: str) -> Optional[str]:
    """Extract a specific function's body from WAT."""
    # Find function start
    pattern = rf'\(func \${re.escape(func_name)}\s+\(type'
    match = re.search(pattern, content)
    if not match:
        return None

    start = match.start()

    # Find matching close paren
    depth = 0
    i = start
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return content[start:i+1]
        i += 1

    return None


def parse_locals(func_body: str) -> List[WasmLocal]:
    """Parse local variable declarations."""
    locals = []

    # Parse params
    for match in re.finditer(r'\(param \$(\w+) (\w+)\)', func_body):
        locals.append(WasmLocal(match.group(1), match.group(2), "param"))

    # Parse locals
    for match in re.finditer(r'\(local \$(\w+) (\w+)\)', func_body):
        locals.append(WasmLocal(match.group(1), match.group(2)))

    return locals


def identify_local_purposes(func_body: str, locals: List[WasmLocal]) -> None:
    """Try to identify what each local variable is used for."""
    for local in locals:
        name = local.name

        # Check usage patterns
        if f'local.get ${name}' in func_body:
            get_count = func_body.count(f'local.get ${name}')
            set_count = func_body.count(f'local.set ${name}')

            # Check what operations follow
            after_get = re.findall(rf'local\.get \${name}\s+(\S+)', func_body)
            ops = set(after_get)

            if 'i64.shr_u' in ops or 'i64.and' in ops:
                local.purpose = "bit_buffer"
            elif 'i32.load8_u' in ops or 'i32.store8' in ops:
                local.purpose = "byte_ptr"
            elif 'i32.add' in ops and get_count > 10:
                local.purpose = "counter/offset"
            elif set_count == 1 and get_count > 5:
                local.purpose = "constant/base"
            elif 'br_if' in str(after_get):
                local.purpose = "condition"


def extract_basic_blocks(func_body: str) -> List[BasicBlock]:
    """Extract basic blocks from function body."""
    blocks = []
    current_block = BasicBlock(id=0)
    block_id = 1

    lines = func_body.split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith(';;'):
            continue

        # Control flow boundaries
        if any(kw in line for kw in ['block', 'loop', 'if', 'else', 'end', 'br', 'br_if', 'br_table']):
            if current_block.instructions:
                blocks.append(current_block)
                current_block = BasicBlock(id=block_id)
                block_id += 1

            if 'loop' in line:
                current_block.loop_header = True

        current_block.instructions.append(line)

    if current_block.instructions:
        blocks.append(current_block)

    return blocks


def identify_algorithm_components(func_body: str) -> Dict[str, List[Tuple[int, str]]]:
    """Identify algorithm components in the function."""
    components = defaultdict(list)

    lines = func_body.split('\n')

    for i, line in enumerate(lines):
        # Check for algorithm patterns
        for pattern_name, pattern in ALGORITHM_PATTERNS.items():
            # Look at surrounding context
            context = '\n'.join(lines[max(0, i-5):min(len(lines), i+5)])
            if re.search(pattern, context, re.DOTALL):
                components[pattern_name].append((i, line.strip()))

    return components


def generate_pseudocode(func_body: str, locals: List[WasmLocal]) -> List[str]:
    """Generate readable pseudocode from WASM."""
    pseudocode = []
    indent = 0

    # Build local name mapping
    local_purposes = {l.name: l.purpose for l in locals if l.purpose}

    lines = func_body.split('\n')
    stack = []  # simplified value stack

    for line in lines:
        line = line.strip()
        if not line or line.startswith('(func') or line.startswith('(local'):
            continue

        # Track structure
        if '(block' in line or '(loop' in line:
            label = re.search(r'\$(\w+)', line)
            label_name = label.group(1) if label else f"block_{indent}"
            if '(loop' in line:
                pseudocode.append(f"{'  ' * indent}loop {label_name}:")
            else:
                pseudocode.append(f"{'  ' * indent}block {label_name}:")
            indent += 1
            continue

        if line == ')' or line == 'end':
            indent = max(0, indent - 1)
            continue

        if '(if' in line or 'if ' in line:
            pseudocode.append(f"{'  ' * indent}if (condition):")
            indent += 1
            continue

        if 'else' in line:
            indent = max(0, indent - 1)
            pseudocode.append(f"{'  ' * indent}else:")
            indent += 1
            continue

        # Simplify common patterns
        if 'local.get' in line:
            match = re.search(r'local\.get \$(\w+)', line)
            if match:
                var = match.group(1)
                purpose = local_purposes.get(var, var)
                stack.append(purpose if purpose != var else f"${var}")

        elif 'local.set' in line:
            match = re.search(r'local\.set \$(\w+)', line)
            if match:
                var = match.group(1)
                if stack:
                    val = stack.pop()
                    pseudocode.append(f"{'  ' * indent}{var} = {val}")

        elif 'i32.load' in line or 'i64.load' in line:
            if stack:
                addr = stack.pop()
                width = '64' if 'i64' in line else '32'
                size = 'byte' if '8' in line else ('short' if '16' in line else 'word')
                stack.append(f"mem[{addr}].{size}")

        elif 'i32.store' in line or 'i64.store' in line:
            if len(stack) >= 2:
                val = stack.pop()
                addr = stack.pop()
                size = 'byte' if '8' in line else ('short' if '16' in line else 'word')
                pseudocode.append(f"{'  ' * indent}mem[{addr}].{size} = {val}")

        elif 'i32.const' in line or 'i64.const' in line:
            match = re.search(r'const (\d+)', line)
            if match:
                stack.append(match.group(1))

        elif 'i32.add' in line or 'i64.add' in line:
            if len(stack) >= 2:
                b, a = stack.pop(), stack.pop()
                stack.append(f"({a} + {b})")

        elif 'i32.sub' in line or 'i64.sub' in line:
            if len(stack) >= 2:
                b, a = stack.pop(), stack.pop()
                stack.append(f"({a} - {b})")

        elif 'i32.and' in line or 'i64.and' in line:
            if len(stack) >= 2:
                b, a = stack.pop(), stack.pop()
                stack.append(f"({a} & {b})")

        elif 'i32.or' in line or 'i64.or' in line:
            if len(stack) >= 2:
                b, a = stack.pop(), stack.pop()
                stack.append(f"({a} | {b})")

        elif 'i32.shl' in line or 'i64.shl' in line:
            if len(stack) >= 2:
                b, a = stack.pop(), stack.pop()
                stack.append(f"({a} << {b})")

        elif 'i32.shr_u' in line or 'i64.shr_u' in line:
            if len(stack) >= 2:
                b, a = stack.pop(), stack.pop()
                stack.append(f"({a} >> {b})")

        elif 'br_if' in line:
            label = re.search(r'br_if \$(\w+)', line)
            label_name = label.group(1) if label else "?"
            cond = stack.pop() if stack else "condition"
            pseudocode.append(f"{'  ' * indent}if ({cond}) goto {label_name}")

        elif 'br ' in line:
            label = re.search(r'br \$(\w+)', line)
            label_name = label.group(1) if label else "?"
            pseudocode.append(f"{'  ' * indent}goto {label_name}")

        elif 'call' in line:
            match = re.search(r'call \$(\S+)', line)
            if match:
                func = match.group(1)
                # Simplify known function names
                if len(func) > 20:
                    func = f"fn_{hash(func) % 1000:03d}"
                pseudocode.append(f"{'  ' * indent}call {func}()")

    return pseudocode


def analyze_algorithm(func_body: str) -> List[str]:
    """Analyze the function to determine what algorithm it implements."""
    hints = []

    # Count operations
    bit_ops = func_body.count('.and') + func_body.count('.or') + func_body.count('.xor')
    shifts = func_body.count('.shl') + func_body.count('.shr')
    loads = func_body.count('.load')
    stores = func_body.count('.store')
    loops = func_body.count('(loop')
    branches = func_body.count('br_if') + func_body.count('br_table')

    hints.append(f"Operations: {bit_ops} bitwise, {shifts} shifts, {loads} loads, {stores} stores")
    hints.append(f"Control flow: {loops} loops, {branches} conditional branches")

    # Check for specific algorithm signatures

    # 1. Huffman/entropy coding
    if 'br_table' in func_body and bit_ops > 50:
        hints.append("LIKELY: Huffman/table-based entropy decoding (br_table + heavy bitops)")

    # 2. LZ77/LZSS distance-length
    if func_body.count('i32.load8_u') > 20 and func_body.count('i32.store8') > 20:
        hints.append("LIKELY: Byte-by-byte copy loop (LZ backreference copy)")

    # 3. Bit buffer management
    if 'i64' in func_body and func_body.count('i64.shr_u') > 10:
        hints.append("LIKELY: 64-bit bit buffer for variable-length decoding")

    # 4. State machine
    if branches > 50 and 'i32.const 4104' in func_body:
        hints.append("LIKELY: State machine with global state at address 4104")

    # 5. Dictionary lookup
    if func_body.count('i32.shl') > 20 and func_body.count('i32.add') > 30:
        hints.append("LIKELY: Array/table indexing (dictionary lookup)")

    # Overall assessment
    if bit_ops > 100 and loads > 50 and loops > 5:
        hints.append("")
        hints.append("ALGORITHM ASSESSMENT: LZ77/LZSS with Huffman entropy coding")
        hints.append("  - Bit buffer for reading variable-length codes")
        hints.append("  - Table-based Huffman decoding")
        hints.append("  - Backreference copy loop")
        hints.append("  - State machine for different decode phases")

    return hints


def generate_clean_room_spec(components: Dict, hints: List[str]) -> str:
    """Generate a clean-room specification of the algorithm."""
    spec = []
    spec.append("=" * 70)
    spec.append("DITER ALGORITHM SPECIFICATION (Clean Room)")
    spec.append("=" * 70)
    spec.append("")
    spec.append("OVERVIEW:")
    spec.append("-" * 40)
    spec.append("DITER is an LZ-family decompression codec with:")
    spec.append("  1. Variable-length entropy coding (likely Huffman)")
    spec.append("  2. Dictionary-based backreferences (LZ77/LZSS style)")
    spec.append("  3. Optional AES encryption layer")
    spec.append("")
    spec.append("DATA STRUCTURES:")
    spec.append("-" * 40)
    spec.append("Global State (at address 4104):")
    spec.append("  - Input buffer pointer")
    spec.append("  - Input buffer end pointer")
    spec.append("  - Output buffer pointer")
    spec.append("  - Output position")
    spec.append("  - Bit buffer (64-bit)")
    spec.append("  - Bits available in buffer")
    spec.append("  - Decode state (state machine)")
    spec.append("  - Dictionary/sliding window pointer")
    spec.append("")
    spec.append("ALGORITHM FLOW:")
    spec.append("-" * 40)
    spec.append("1. INIT:")
    spec.append("   - Reset state to initial")
    spec.append("   - Clear bit buffer")
    spec.append("   - Optional: load decryption key")
    spec.append("")
    spec.append("2. MAIN DECODE LOOP:")
    spec.append("   while (input_available && !done):")
    spec.append("     a. Refill bit buffer if needed (read 8 bytes)")
    spec.append("     b. Read symbol type (literal vs match)")
    spec.append("     c. If literal:")
    spec.append("        - Decode literal byte value")
    spec.append("        - Write to output")
    spec.append("     d. If match (backreference):")
    spec.append("        - Decode distance (offset into history)")
    spec.append("        - Decode length (bytes to copy)")
    spec.append("        - Copy from dictionary to output")
    spec.append("")
    spec.append("3. BIT READING:")
    spec.append("   - 64-bit bit buffer for efficiency")
    spec.append("   - Refill when < 32 bits available")
    spec.append("   - Extract N bits: (buffer >> (64-N)) & mask")
    spec.append("   - Consume bits: buffer <<= N; bits_available -= N")
    spec.append("")
    spec.append("4. ENTROPY DECODING:")
    spec.append("   - Table-based Huffman decoder")
    spec.append("   - Peek N bits as table index")
    spec.append("   - Table entry contains: symbol + bit length")
    spec.append("   - Consume actual bit length used")
    spec.append("")
    spec.append("5. BACKREFERENCE COPY:")
    spec.append("   - Distance: offset into sliding window")
    spec.append("   - Length: number of bytes to copy (min 3)")
    spec.append("   - Byte-by-byte copy (handles overlapping)")
    spec.append("")
    spec.append("KEY OBSERVATIONS:")
    spec.append("-" * 40)
    for hint in hints:
        if hint:
            spec.append(f"  {hint}")
    spec.append("")
    spec.append("COMPARISON TO KNOWN ALGORITHMS:")
    spec.append("-" * 40)
    spec.append("  - Similar to DEFLATE (zlib) but with different:")
    spec.append("    - Huffman table format")
    spec.append("    - Distance/length encoding")
    spec.append("    - State machine structure")
    spec.append("  - May be derived from or inspired by:")
    spec.append("    - LZ4 (simplicity)")
    spec.append("    - Zstd (modern features)")
    spec.append("    - Brotli (web optimization)")
    spec.append("")
    spec.append("=" * 70)

    return '\n'.join(spec)


def decompile_function(content: str, func_name: str) -> Optional[DecompiledFunction]:
    """Fully decompile a function."""
    func_body = extract_function_body(content, func_name)
    if not func_body:
        return None

    # Parse structure
    locals = parse_locals(func_body)
    identify_local_purposes(func_body, locals)

    # Generate pseudocode
    pseudocode = generate_pseudocode(func_body, locals)

    # Analyze algorithm
    hints = analyze_algorithm(func_body)

    # Get return type
    ret_match = re.search(r'\(result (\w+)\)', func_body)
    return_type = ret_match.group(1) if ret_match else None

    params = [l for l in locals if l.purpose == "param"]
    local_vars = [l for l in locals if l.purpose != "param"]

    return DecompiledFunction(
        name=func_name,
        params=params,
        locals=local_vars,
        return_type=return_type,
        pseudocode=pseudocode,
        algorithm_hints=hints
    )


def main():
    parser = argparse.ArgumentParser(
        description='Deep decompilation of DITER WASM algorithm'
    )
    parser.add_argument('--wat', required=True, help='Input WAT file')
    parser.add_argument('--function', '-f', default='f172',
                        help='Function to decompile (default: f172)')
    parser.add_argument('--output', '-o', help='Output file for spec')
    parser.add_argument('--pseudocode', '-p', action='store_true',
                        help='Generate pseudocode')
    parser.add_argument('--spec', '-s', action='store_true',
                        help='Generate clean-room specification')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Full analysis (pseudocode + spec)')

    args = parser.parse_args()

    input_path = Path(args.wat)
    content = input_path.read_text()

    print(f"Analyzing: {input_path}")
    print(f"Target function: {args.function}")
    print()

    # Decompile target function
    result = decompile_function(content, args.function)

    if not result:
        print(f"Error: Function ${args.function} not found")
        return 1

    output_lines = []

    # Function signature
    output_lines.append("=" * 70)
    output_lines.append(f"FUNCTION: {result.name}")
    output_lines.append("=" * 70)

    param_str = ', '.join(f"{p.type} {p.name}" for p in result.params)
    output_lines.append(f"Signature: {result.name}({param_str}) -> {result.return_type or 'void'}")
    output_lines.append("")

    # Locals with purposes
    output_lines.append("LOCAL VARIABLES:")
    output_lines.append("-" * 40)
    for local in result.locals[:20]:  # Limit output
        purpose = f" ({local.purpose})" if local.purpose else ""
        output_lines.append(f"  {local.type:5} ${local.name}{purpose}")
    if len(result.locals) > 20:
        output_lines.append(f"  ... and {len(result.locals) - 20} more")
    output_lines.append("")

    # Algorithm hints
    output_lines.append("ALGORITHM ANALYSIS:")
    output_lines.append("-" * 40)
    for hint in result.algorithm_hints:
        output_lines.append(f"  {hint}")
    output_lines.append("")

    # Pseudocode (abbreviated)
    if args.pseudocode or args.all:
        output_lines.append("PSEUDOCODE (abbreviated):")
        output_lines.append("-" * 40)
        # Show first 100 meaningful lines
        meaningful = [l for l in result.pseudocode if l.strip()]
        for line in meaningful[:100]:
            output_lines.append(line)
        if len(meaningful) > 100:
            output_lines.append(f"... and {len(meaningful) - 100} more lines")
        output_lines.append("")

    # Clean room spec
    if args.spec or args.all:
        func_body = extract_function_body(content, args.function)
        components = identify_algorithm_components(func_body)
        spec = generate_clean_room_spec(components, result.algorithm_hints)
        output_lines.append(spec)

    output_text = '\n'.join(output_lines)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output_text)
        print(f"Written to: {output_path}")
    else:
        print(output_text)

    return 0


if __name__ == '__main__':
    exit(main())
