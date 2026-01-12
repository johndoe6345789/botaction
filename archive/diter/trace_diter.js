#!/usr/bin/env node
/**
 * DITER Runtime Tracer
 *
 * Instruments the DITER WASM module to log all function calls,
 * memory operations, and state changes during decompression.
 *
 * Usage:
 *   node trace_diter.js --binz sample.binz --params params.json --trace calls
 *   node trace_diter.js --binz sample.binz --params params.json --trace memory
 *   node trace_diter.js --binz sample.binz --params params.json --trace all
 */

const fs = require('fs');
const path = require('path');

// API function name mappings (rickroll -> readable)
const API_NAMES = {
    'heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl': 'alloc',
    'mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l': 'init',
    'Umlja1JvbGxlZDRV': 'set_key',
    'dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI': 'write_dict',
    'GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW': 'get_dict_ptr',
    'FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN': 'pump',
    'bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg': 'output_size',
    'TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT': 'output_ptr',
};

// Reverse mapping
const READABLE_TO_RICKROLL = {};
for (const [rick, readable] of Object.entries(API_NAMES)) {
    READABLE_TO_RICKROLL[readable] = rick;
}

class DiterTracer {
    constructor(options = {}) {
        this.traceLevel = options.trace || 'calls';
        this.maxLogs = options.maxLogs || 10000;
        this.logs = [];
        this.callStack = [];
        this.callCounts = {};
        this.memoryAccess = { reads: 0, writes: 0 };
        this.stateSnapshots = [];
        this.instance = null;
        this.memory = null;
    }

    log(type, data) {
        if (this.logs.length < this.maxLogs) {
            this.logs.push({
                type,
                data,
                timestamp: Date.now(),
                depth: this.callStack.length
            });
        }
    }

    // Create instrumented import object
    createImports() {
        const self = this;

        return {
            env: {
                // Memory (will be replaced by actual memory)
                memory: null,

                // Abort handler
                abort: (msg, file, line, col) => {
                    self.log('abort', { msg, file, line, col });
                    console.error(`WASM ABORT at ${file}:${line}:${col}`);
                    throw new Error('WASM aborted');
                },

                // Memory growth (sbrk equivalent)
                sbrk: (increment) => {
                    self.log('sbrk', { increment });
                    // Simple bump allocator
                    const oldSize = self.memory.buffer.byteLength;
                    if (increment > 0) {
                        const pages = Math.ceil(increment / 65536);
                        self.memory.grow(pages);
                        self.log('memory_grow', { pages, oldSize, newSize: self.memory.buffer.byteLength });
                    }
                    return oldSize;
                }
            }
        };
    }

    // Wrap exported functions to trace calls
    wrapExports(exports) {
        const self = this;
        const wrapped = {};

        for (const [name, fn] of Object.entries(exports)) {
            if (typeof fn === 'function') {
                const readableName = API_NAMES[name] || name;

                wrapped[name] = function(...args) {
                    self.callStack.push(readableName);
                    self.callCounts[readableName] = (self.callCounts[readableName] || 0) + 1;

                    const entry = {
                        func: readableName,
                        args: args.slice(),
                        depth: self.callStack.length
                    };

                    if (self.traceLevel === 'all' || self.traceLevel === 'calls') {
                        self.log('call', entry);
                    }

                    // Snapshot state before call for key functions
                    if (['pump', 'init', 'write_dict'].includes(readableName)) {
                        self.snapshotState('before_' + readableName);
                    }

                    const result = fn.apply(this, args);

                    // Snapshot state after call
                    if (['pump', 'init', 'write_dict'].includes(readableName)) {
                        self.snapshotState('after_' + readableName);
                    }

                    entry.result = result;
                    if (self.traceLevel === 'all' || self.traceLevel === 'calls') {
                        self.log('return', entry);
                    }

                    self.callStack.pop();
                    return result;
                };

                // Also add readable name alias
                if (API_NAMES[name]) {
                    wrapped[API_NAMES[name]] = wrapped[name];
                }
            } else {
                wrapped[name] = fn;
            }
        }

        return wrapped;
    }

    // Take a snapshot of the decoder state
    snapshotState(label) {
        if (!this.memory) return;

        const view = new DataView(this.memory.buffer);
        const STATE_ADDR = 4104;  // Global state address

        try {
            const snapshot = {
                label,
                timestamp: Date.now(),
                // Read state structure (guessed layout)
                state: {
                    field0: view.getUint32(STATE_ADDR, true),
                    field1: view.getUint32(STATE_ADDR + 4, true),
                    field2: view.getUint32(STATE_ADDR + 8, true),
                    field3: view.getUint32(STATE_ADDR + 12, true),
                    field4: view.getUint32(STATE_ADDR + 16, true),
                    field5: view.getUint32(STATE_ADDR + 20, true),
                    field6: view.getUint32(STATE_ADDR + 24, true),
                    field7: view.getUint32(STATE_ADDR + 28, true),
                }
            };

            this.stateSnapshots.push(snapshot);
            this.log('state_snapshot', snapshot);
        } catch (e) {
            // Memory might not be initialized yet
        }
    }

    // Load and instrument the WASM module
    async loadWasm(wasmPath) {
        const wasmBuffer = fs.readFileSync(wasmPath);
        const imports = this.createImports();

        // Create memory
        this.memory = new WebAssembly.Memory({ initial: 256, maximum: 65536 });
        imports.env.memory = this.memory;

        // Instantiate
        const module = await WebAssembly.instantiate(wasmBuffer, imports);
        this.instance = module.instance;

        // Get memory from exports if available
        if (this.instance.exports.memory) {
            this.memory = this.instance.exports.memory;
        }

        // Wrap exports
        const wrapped = this.wrapExports(this.instance.exports);

        return wrapped;
    }

    // Run decompression with tracing
    async decompress(binzPath, paramsPath) {
        // Load params
        const params = JSON.parse(fs.readFileSync(paramsPath, 'utf8'));
        const keyData = Buffer.from(params.b || params.key || '', 'base64');

        // Load compressed data
        const compressed = fs.readFileSync(binzPath);

        console.log(`\n${'='.repeat(60)}`);
        console.log('DITER RUNTIME TRACE');
        console.log('='.repeat(60));
        console.log(`Input: ${binzPath} (${compressed.length} bytes)`);
        console.log(`Params: ${paramsPath}`);
        console.log(`Trace level: ${this.traceLevel}`);
        console.log('');

        // Find WASM file
        const wasmPath = path.join(__dirname, 'downloads', 'diter_wasm_blob.wasm');
        if (!fs.existsSync(wasmPath)) {
            console.error(`WASM not found at ${wasmPath}`);
            return null;
        }

        // Load instrumented WASM
        console.log('Loading WASM...');
        const exports = await this.loadWasm(wasmPath);

        console.log('Available exports:', Object.keys(exports).map(k => API_NAMES[k] || k).join(', '));
        console.log('');

        // Run decompression sequence
        console.log('--- DECOMPRESSION TRACE ---');

        try {
            // 1. Initialize
            console.log('\n[1] Calling init()...');
            exports.init();

            // 2. Set key if available
            if (keyData.length >= 32) {
                console.log('\n[2] Setting decryption key...');
                const keyPtr = exports.alloc(keyData.length);
                const keyView = new Uint8Array(this.memory.buffer, keyPtr, keyData.length);
                keyView.set(keyData);
                exports.set_key(keyPtr, keyData.length);
            }

            // 3. Allocate input buffer
            console.log('\n[3] Allocating input buffer...');
            const inputPtr = exports.alloc(compressed.length);
            const inputView = new Uint8Array(this.memory.buffer, inputPtr, compressed.length);
            inputView.set(compressed);

            // 4. Write dictionary
            console.log('\n[4] Writing dictionary...');
            const dictPtr = exports.write_dict(compressed.length);

            // 5. Pump data
            console.log('\n[5] Pumping data...');
            let status;
            let pumpCount = 0;
            do {
                status = exports.pump(1);
                pumpCount++;
                if (pumpCount % 100 === 0) {
                    console.log(`  pump() called ${pumpCount} times, status=${status}`);
                }
            } while (status !== 0 && pumpCount < 100000);

            console.log(`  Total pump() calls: ${pumpCount}`);

            // 6. Get output
            console.log('\n[6] Getting output...');
            const outPtr = exports.output_ptr();
            const outSize = exports.output_size();
            console.log(`  Output: ${outSize} bytes at ptr ${outPtr}`);

            // Extract output
            const output = new Uint8Array(this.memory.buffer, outPtr, outSize);

            return Buffer.from(output);

        } catch (e) {
            console.error('Decompression error:', e.message);
            return null;
        }
    }

    // Generate trace report
    generateReport() {
        console.log('\n' + '='.repeat(60));
        console.log('TRACE REPORT');
        console.log('='.repeat(60));

        console.log('\nCALL COUNTS:');
        console.log('-'.repeat(40));
        for (const [name, count] of Object.entries(this.callCounts).sort((a,b) => b[1] - a[1])) {
            console.log(`  ${name.padEnd(20)} ${count}`);
        }

        console.log('\nSTATE SNAPSHOTS:');
        console.log('-'.repeat(40));
        for (const snap of this.stateSnapshots) {
            console.log(`\n  ${snap.label}:`);
            for (const [field, value] of Object.entries(snap.state)) {
                console.log(`    ${field}: ${value} (0x${value.toString(16)})`);
            }
        }

        if (this.traceLevel === 'all') {
            console.log('\nDETAILED LOG (first 50 entries):');
            console.log('-'.repeat(40));
            for (const entry of this.logs.slice(0, 50)) {
                const indent = '  '.repeat(entry.depth || 0);
                if (entry.type === 'call') {
                    console.log(`${indent}-> ${entry.data.func}(${entry.data.args.join(', ')})`);
                } else if (entry.type === 'return') {
                    console.log(`${indent}<- ${entry.data.func} = ${entry.data.result}`);
                } else {
                    console.log(`${indent}[${entry.type}] ${JSON.stringify(entry.data)}`);
                }
            }
            if (this.logs.length > 50) {
                console.log(`  ... and ${this.logs.length - 50} more entries`);
            }
        }

        console.log('\n' + '='.repeat(60));
    }
}

// Main
async function main() {
    const args = process.argv.slice(2);

    let binzPath = null;
    let paramsPath = null;
    let traceLevel = 'calls';

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--binz' && args[i+1]) {
            binzPath = args[++i];
        } else if (args[i] === '--params' && args[i+1]) {
            paramsPath = args[++i];
        } else if (args[i] === '--trace' && args[i+1]) {
            traceLevel = args[++i];
        } else if (args[i] === '--help' || args[i] === '-h') {
            console.log(`
DITER Runtime Tracer

Usage:
  node trace_diter.js --binz <file.binz> --params <params.json> [--trace <level>]

Options:
  --binz <path>     Path to compressed .binz file
  --params <path>   Path to params.json (contains decryption key)
  --trace <level>   Trace level: calls, memory, state, all (default: calls)

Example:
  node trace_diter.js --binz sample.binz --params params.json --trace all
`);
            process.exit(0);
        }
    }

    if (!binzPath || !paramsPath) {
        console.error('Error: --binz and --params are required');
        console.error('Run with --help for usage');
        process.exit(1);
    }

    const tracer = new DiterTracer({ trace: traceLevel });
    const output = await tracer.decompress(binzPath, paramsPath);

    tracer.generateReport();

    if (output) {
        console.log(`\nDecompression successful: ${output.length} bytes`);

        // Show first few bytes of output
        console.log('Output preview (first 64 bytes):');
        console.log(output.slice(0, 64).toString('hex').match(/.{2}/g).join(' '));
    }
}

main().catch(console.error);
