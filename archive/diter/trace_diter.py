#!/usr/bin/env python3
"""
DITER Runtime Tracer (Python version)

Uses wasmtime to run the DITER WASM with full instrumentation.
Logs all memory reads/writes, function calls, and state transitions.

Usage:
    python trace_diter.py --binz sample.binz --params params.json
    python trace_diter.py --binz sample.binz --params params.json --trace all
    python trace_diter.py --binz sample.binz --params params.json --output decoded.bin
"""

import argparse
import json
import base64
import struct
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Try to import wasmtime
try:
    import wasmtime
    HAS_WASMTIME = True
except ImportError:
    HAS_WASMTIME = False
    print("Warning: wasmtime not installed. Install with: pip install wasmtime")


# API function name mappings
API_NAMES = {
    "heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl": "alloc",
    "mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l": "init",
    "Umlja1JvbGxlZDRV": "set_key",
    "dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI": "write_dict",
    "GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW": "get_dict_ptr",
    "FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN": "pump",
    "bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg": "output_size",
    "TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT": "output_ptr",
}

# Reverse mapping
READABLE_TO_RICK = {v: k for k, v in API_NAMES.items()}


@dataclass
class TraceEvent:
    """A single trace event."""
    event_type: str
    data: Dict[str, Any]
    timestamp: int = 0


@dataclass
class FunctionStats:
    """Statistics for a function."""
    call_count: int = 0
    total_time_us: int = 0
    args_histogram: Dict[str, int] = field(default_factory=dict)


class DiterTracer:
    """Traces DITER WASM execution."""

    STATE_ADDR = 4104  # Global state structure address

    def __init__(self, trace_level: str = "calls"):
        self.trace_level = trace_level
        self.events: List[TraceEvent] = []
        self.call_stack: List[str] = []
        self.func_stats: Dict[str, FunctionStats] = defaultdict(FunctionStats)
        self.memory_snapshots: List[Dict] = []

        # WASM runtime
        self.store = None
        self.memory = None
        self.instance = None
        self.exports = {}

    def log(self, event_type: str, data: Dict):
        """Log a trace event."""
        if len(self.events) < 100000:  # Limit events
            self.events.append(TraceEvent(event_type, data))

    def get_readable_name(self, name: str) -> str:
        """Convert rickroll name to readable name."""
        return API_NAMES.get(name, name)

    def snapshot_state(self, label: str):
        """Take a snapshot of decoder state."""
        if self.memory is None:
            return

        try:
            mem_data = self.memory.data_ptr(self.store)
            mem_len = self.memory.data_len(self.store)

            # Read state structure
            if mem_len > self.STATE_ADDR + 64:
                state_bytes = bytes(mem_data[self.STATE_ADDR:self.STATE_ADDR + 64])
                fields = struct.unpack('<16I', state_bytes)

                snapshot = {
                    'label': label,
                    'fields': {f'field_{i}': v for i, v in enumerate(fields)},
                    'fields_hex': {f'field_{i}': hex(v) for i, v in enumerate(fields)},
                }
                self.memory_snapshots.append(snapshot)
                self.log('state', snapshot)
        except Exception as e:
            self.log('error', {'msg': f'Failed to snapshot state: {e}'})

    def load_wasm(self, wasm_path: Path):
        """Load the WASM module."""
        if not HAS_WASMTIME:
            raise RuntimeError("wasmtime is required but not installed")

        # Create engine and store
        engine = wasmtime.Engine()
        self.store = wasmtime.Store(engine)

        # Create memory
        memory_type = wasmtime.MemoryType(wasmtime.Limits(256, 65536))
        self.memory = wasmtime.Memory(self.store, memory_type)

        # Load module
        module = wasmtime.Module.from_file(engine, str(wasm_path))

        # Create imports
        linker = wasmtime.Linker(engine)

        # Add memory
        linker.define(self.store, "env", "memory", self.memory)

        # Add abort function
        abort_type = wasmtime.FuncType([wasmtime.ValType.i32()] * 4, [])
        def abort_fn(msg, file, line, col):
            self.log('abort', {'msg': msg, 'file': file, 'line': line, 'col': col})
            raise RuntimeError(f"WASM abort at {file}:{line}:{col}")
        linker.define(self.store, "env", "abort", wasmtime.Func(self.store, abort_type, abort_fn))

        # Add sbrk function
        sbrk_type = wasmtime.FuncType([wasmtime.ValType.i32()], [wasmtime.ValType.i32()])
        self.heap_ptr = [self.memory.data_len(self.store)]
        def sbrk_fn(increment):
            old_ptr = self.heap_ptr[0]
            self.heap_ptr[0] += increment
            self.log('sbrk', {'increment': increment, 'old_ptr': old_ptr, 'new_ptr': self.heap_ptr[0]})
            # Grow memory if needed
            needed_pages = (self.heap_ptr[0] - self.memory.data_len(self.store) + 65535) // 65536
            if needed_pages > 0:
                self.memory.grow(self.store, needed_pages)
            return old_ptr
        linker.define(self.store, "env", "sbrk", wasmtime.Func(self.store, sbrk_type, sbrk_fn))

        # Instantiate
        self.instance = linker.instantiate(self.store, module)

        # Get memory from exports if present
        mem_export = self.instance.exports(self.store).get("memory")
        if mem_export:
            self.memory = mem_export

        # Collect exports
        for export in module.exports:
            name = export.name
            item = self.instance.exports(self.store).get(name)
            if item is not None:
                self.exports[name] = item
                # Also add readable alias
                if name in API_NAMES:
                    self.exports[API_NAMES[name]] = item

        print(f"Loaded WASM with {len(self.exports)} exports")

    def call_func(self, name: str, *args) -> Any:
        """Call a WASM function with tracing."""
        # Find function (try both rickroll and readable names)
        func = self.exports.get(name)
        if func is None and name in READABLE_TO_RICK:
            func = self.exports.get(READABLE_TO_RICK[name])
        if func is None:
            raise RuntimeError(f"Function {name} not found")

        readable = self.get_readable_name(name)
        self.call_stack.append(readable)
        self.func_stats[readable].call_count += 1

        self.log('call', {
            'func': readable,
            'args': list(args),
            'depth': len(self.call_stack)
        })

        # Snapshot before key calls
        if readable in ['pump', 'init', 'write_dict'] and self.trace_level == 'all':
            self.snapshot_state(f'before_{readable}')

        # Call the function
        result = func(self.store, *args)

        # Snapshot after key calls
        if readable in ['pump', 'init', 'write_dict'] and self.trace_level == 'all':
            self.snapshot_state(f'after_{readable}')

        self.log('return', {
            'func': readable,
            'result': result,
            'depth': len(self.call_stack)
        })

        self.call_stack.pop()
        return result

    def write_memory(self, ptr: int, data: bytes):
        """Write data to WASM memory."""
        mem_data = self.memory.data_ptr(self.store)
        for i, b in enumerate(data):
            mem_data[ptr + i] = b

    def read_memory(self, ptr: int, size: int) -> bytes:
        """Read data from WASM memory."""
        mem_data = self.memory.data_ptr(self.store)
        return bytes(mem_data[ptr:ptr + size])

    def decompress(self, binz_path: Path, params_path: Path) -> Optional[bytes]:
        """Run decompression with tracing."""
        # Load params
        with open(params_path) as f:
            params = json.load(f)

        key_b64 = params.get('b') or params.get('key', '')
        key_data = base64.b64decode(key_b64) if key_b64 else b''

        # Load compressed data
        compressed = binz_path.read_bytes()

        print("=" * 60)
        print("DITER RUNTIME TRACE")
        print("=" * 60)
        print(f"Input: {binz_path} ({len(compressed)} bytes)")
        print(f"Key: {len(key_data)} bytes")
        print(f"Trace level: {self.trace_level}")
        print()

        # Find WASM
        wasm_path = Path(__file__).parent / "downloads" / "diter_wasm_blob.wasm"
        if not wasm_path.exists():
            # Try relative to script
            wasm_path = Path(__file__).parent.parent.parent / "downloads" / "diter_wasm_blob.wasm"
        if not wasm_path.exists():
            print(f"Error: WASM not found at {wasm_path}")
            return None

        # Load WASM
        print("Loading WASM...")
        self.load_wasm(wasm_path)

        print("--- DECOMPRESSION TRACE ---")

        try:
            # 1. Initialize
            print("\n[1] init()")
            self.call_func('init')

            # 2. Set key if available
            if len(key_data) >= 32:
                print(f"\n[2] set_key({len(key_data)} bytes)")
                key_ptr = self.call_func('alloc', len(key_data))
                self.write_memory(key_ptr, key_data)
                self.call_func('set_key', key_ptr, len(key_data))

            # 3. Allocate and write input
            print(f"\n[3] alloc({len(compressed)}) for input")
            input_ptr = self.call_func('alloc', len(compressed))
            self.write_memory(input_ptr, compressed)

            # 4. Write dictionary
            print(f"\n[4] write_dict({len(compressed)})")
            dict_ptr = self.call_func('write_dict', len(compressed))
            print(f"   -> dict_ptr = {dict_ptr}")

            # 5. Pump
            print("\n[5] pump() loop...")
            status = 1
            pump_count = 0
            while status != 0 and pump_count < 100000:
                status = self.call_func('pump', 1)
                pump_count += 1
                if pump_count % 1000 == 0:
                    print(f"   pump #{pump_count}, status={status}")

            print(f"   Total pump() calls: {pump_count}")

            # 6. Get output
            print("\n[6] Getting output...")
            out_ptr = self.call_func('output_ptr')
            out_size = self.call_func('output_size')
            print(f"   output_ptr = {out_ptr}")
            print(f"   output_size = {out_size}")

            if out_size > 0:
                output = self.read_memory(out_ptr, out_size)
                return output
            else:
                print("   Warning: output_size is 0")
                return b''

        except Exception as e:
            print(f"Error during decompression: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_report(self):
        """Print trace report."""
        print()
        print("=" * 60)
        print("TRACE REPORT")
        print("=" * 60)

        print("\nFUNCTION CALL COUNTS:")
        print("-" * 40)
        for name, stats in sorted(self.func_stats.items(), key=lambda x: -x[1].call_count):
            print(f"  {name:20} {stats.call_count}")

        if self.memory_snapshots:
            print("\nSTATE SNAPSHOTS:")
            print("-" * 40)
            for snap in self.memory_snapshots[:10]:  # Limit output
                print(f"\n  {snap['label']}:")
                for name, value in list(snap['fields'].items())[:8]:
                    hex_val = snap['fields_hex'][name]
                    print(f"    {name}: {value:10} ({hex_val})")

        if self.trace_level == 'all' and self.events:
            print("\nEVENT LOG (first 30):")
            print("-" * 40)
            for event in self.events[:30]:
                if event.event_type == 'call':
                    indent = "  " * event.data.get('depth', 0)
                    args = ', '.join(str(a) for a in event.data.get('args', []))
                    print(f"{indent}-> {event.data['func']}({args})")
                elif event.event_type == 'return':
                    indent = "  " * event.data.get('depth', 0)
                    print(f"{indent}<- {event.data['func']} = {event.data.get('result')}")
                elif event.event_type in ['sbrk', 'abort']:
                    print(f"  [{event.event_type}] {event.data}")

            if len(self.events) > 30:
                print(f"  ... and {len(self.events) - 30} more events")

        print()
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='DITER Runtime Tracer')
    parser.add_argument('--binz', required=True, help='Path to .binz file')
    parser.add_argument('--params', required=True, help='Path to params.json')
    parser.add_argument('--trace', default='calls', choices=['calls', 'memory', 'state', 'all'],
                        help='Trace level')
    parser.add_argument('--output', '-o', help='Save decompressed output to file')

    args = parser.parse_args()

    if not HAS_WASMTIME:
        print("Error: wasmtime is required. Install with: pip install wasmtime")
        return 1

    tracer = DiterTracer(trace_level=args.trace)
    output = tracer.decompress(Path(args.binz), Path(args.params))

    tracer.generate_report()

    if output:
        print(f"\nDecompression successful: {len(output)} bytes")
        print(f"Output preview (first 64 bytes hex):")
        print(' '.join(f'{b:02x}' for b in output[:64]))

        if args.output:
            Path(args.output).write_bytes(output)
            print(f"\nSaved to: {args.output}")

    return 0


if __name__ == '__main__':
    exit(main())
