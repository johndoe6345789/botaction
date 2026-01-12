# DITER Algorithm Analysis

This document summarizes reverse-engineering analysis of Sketchfab's DITER WebAssembly decompression codec.

## What is DITER?

DITER is a proprietary binary decompression codec embedded in Sketchfab's web viewer. It processes `.binz` geometry files to extract 3D model data.

### Obfuscation

The WASM binary uses obfuscated function names that are Base64-encoded fragments of Rick Astley's "Never Gonna Give You Up" lyrics:

| Obfuscated Name | Decoded Lyrics | Actual Function |
|-----------------|----------------|-----------------|
| `heSBnb29kYnllCk5ldmVy...` | "...goodbye\nNever gonna te..." | `alloc()` |
| `mV2ZXIgZ29ubmEgbGV0IHlv...` | "...ever gonna let you down\nNe..." | `init()` |
| `Umlja1JvbGxlZDRV` | "RickRolled4U" | `set_key()` |
| `FrZSB5b3UgY3J5Ck5ldmVy...` | "...ake you cry\nNever gonna s..." | `pump()` |

## Codec Statistics

| Metric | Value |
|--------|-------|
| Total functions | 193 |
| WASM size | ~253 KB |
| Largest function (f172) | 84,679 bytes |
| Total bitwise ops | ~2,500+ |
| Total loops | ~100+ |

### Comparison to Standard Libraries

| Library | Typical Size | Notes |
|---------|--------------|-------|
| LZ4 | ~14 KB | Fast, simple |
| Miniz (zlib) | ~25 KB | DEFLATE |
| Zstd | ~139 KB | Modern, complex |
| **DITER** | **253 KB** | Heavily obfuscated |

DITER is ~10x larger than comparable codecs, likely due to obfuscation and compiler-generated boilerplate.

## Public API

```
init()              - Initialize/reset decoder state
alloc(size) -> ptr  - Allocate buffer in WASM memory
set_key(ptr, len)   - Set decryption key (optional AES layer)
write_dict(size)    - Write dictionary data, returns pointer
get_dict_ptr()      - Get current dictionary pointer
pump(mode) -> stat  - Process data (mode: 0=continue, 1=flush)
output_ptr() -> ptr - Get output buffer start
output_size() -> n  - Get output buffer size
```

## Algorithm Overview

Based on code analysis, DITER implements an **LZ-family dictionary compression** algorithm with:

1. **Variable-length entropy coding** (Huffman-like)
2. **Dictionary-based backreferences** (LZ77/LZSS style)
3. **Optional AES encryption layer**

### Data Flow

```
Compressed Input
      |
      v
+------------------+
|   Bit Reader     |  <- Reads variable-length codes
+------------------+
      |
      v
+------------------+
| Entropy Decoder  |  <- Table-based symbol decode
+------------------+
      |
      +-----> Literal bytes ----+
      |                         |
      +-----> Match codes ------+
              (distance/length) |
                    |           |
                    v           |
            +---------------+   |
            | Dictionary    |   |
            | Copy Loop     |   |
            +---------------+   |
                    |           |
                    v           v
               +-------------------+
               |  Output Buffer    |
               +-------------------+
```

## Key Function Categories

| Category | Count | Description |
|----------|-------|-------------|
| `core_decompress` | 23 | Main decompression logic |
| `bit_reader` | 11 | Variable-length code reading |
| `buffer_copy` | 4 | Backreference copy operations |
| `state_machine` | 2 | Control flow dispatch |
| `memory_mgmt` | 1 | Heap allocation (sbrk) |
| `reader` | 30 | Memory read utilities |
| `unknown` | 107 | Unclassified helpers |

## Core Algorithm Functions

### f172 (84 KB) - Main Decompression

The monster function that processes compressed data:
- 171 memory loads, 77 stores
- 41 bitwise operations, 12 shifts
- 518 local variables
- Called from `get_dict_ptr()`

### f152 - Pump Dispatch

Entry point called by `pump()`:
- Calls `f151` for actual processing
- Manages state machine transitions

### f18 - Core Bit Operations

Bit buffer management:
- Uses 64-bit buffer for efficiency
- Extracts variable-length codes
- Refills when buffer runs low

### f125 - Huffman Decoder

Table-based entropy decoding:
- 264 bitwise operations
- 416 conditional branches
- Complex table lookups

## State Structure

Global state stored at address **4104**:

```c
struct DiterState {
    uint8_t* input_ptr;       // Current input position
    uint8_t* input_end;       // End of input buffer
    uint8_t* output_ptr;      // Current output position
    uint8_t* output_start;    // Start of output buffer
    uint64_t bit_buffer;      // 64-bit bit accumulator
    uint32_t bits_available;  // Bits remaining in buffer
    uint32_t decode_state;    // State machine state
    uint8_t* dictionary;      // Sliding window pointer
    // ... additional fields
};
```

## Algorithm Pseudocode

```python
def decompress(input_data):
    state = init_state()

    while not done:
        # Refill bit buffer if needed
        if state.bits_available < 32:
            refill_bits(state)

        # Read symbol type
        symbol = decode_huffman(state)

        if is_literal(symbol):
            # Direct byte output
            output_byte(symbol & 0xFF)
        else:
            # Backreference
            distance = decode_distance(state)
            length = decode_length(state) + 3  # minimum match length

            # Copy from dictionary
            for i in range(length):
                byte = state.dictionary[state.out_pos - distance]
                output_byte(byte)

    return output_buffer
```

## Bit Reading Pattern

```python
def read_bits(state, n):
    # Refill if needed
    while state.bits_available < n:
        byte = read_input_byte(state)
        state.bit_buffer |= byte << state.bits_available
        state.bits_available += 8

    # Extract n bits
    result = state.bit_buffer & ((1 << n) - 1)
    state.bit_buffer >>= n
    state.bits_available -= n

    return result
```

## Comparison to Known Algorithms

| Feature | DEFLATE | LZ4 | DITER |
|---------|---------|-----|-------|
| Entropy coding | Huffman | None | Huffman-like |
| Min match length | 3 | 4 | ~3 |
| Max distance | 32 KB | 64 KB | Unknown |
| Bit buffer | Yes | No | Yes (64-bit) |
| Block format | Dynamic | Fixed | Unknown |

DITER appears closest to **DEFLATE/zlib** in structure but with custom Huffman tables and encoding.

## Analysis Tools

The `archive/diter/` folder contains analysis tools:

- `denoise_wasm.py` - Basic rickroll decoder
- `denoise_wasm_v2.py` - AI-friendly cleaner with function classification
- `denoise_wasm_v3.py` - Call graph tracing and algorithm identification
- `denoise_wasm_v4.py` - Pseudocode generation and clean-room spec

### Usage

```bash
# Analyze function categories
python denoise_wasm_v3.py --wat downloads/diter_wasm_blob.wat --report

# Trace specific function
python denoise_wasm_v3.py --wat downloads/diter_wasm_blob.wat --trace f152

# Generate pseudocode
python denoise_wasm_v4.py --wat downloads/diter_wasm_blob.wat --function f172 --all

# Generate cleaned WAT file
python denoise_wasm_v2.py --wat downloads/diter_wasm_blob.wat -o cleaned.wat
```

## Conclusion

DITER is a reasonably standard LZ-family codec hidden under layers of obfuscation. The algorithm itself is not novel - it appears to be a variant of DEFLATE-style compression with:

1. Standard Huffman entropy coding
2. Standard LZ77 backreferences
3. Optional AES encryption layer
4. Heavily obfuscated function names (rickroll)
5. Compiler-bloated code (~10x expected size)

The obfuscation is purely cosmetic (funny function names) and does not provide any real security - the algorithm can be fully understood through static analysis.


I can see the DITER implementation now. It uses a Web Worker to load and run the WASM. The key insight from the code:

Message type 1: Initialize - sends WASM blob
Message type 3: Set decryption key (derived from git commit hash)
Message type 2: Decode data - sends input data and encryption key
The actual WASM API calls inside the worker are:

mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l() = init()
heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl(size) = alloc(size)
[function at 358](mode) = pump(mode) - processes data
TmV2ZXIgZ29ubmEdZ2l2ZSB5b3UgdXAKT() = output_ptr()
bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg() = output_size()