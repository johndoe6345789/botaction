#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const args = {
    input: "downloads/diter_wasm_blob.wasm",
    output: "downloads/diter_wasm_blob.wat",
    noNames: false,
    foldExprs: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--in") {
      args.input = argv[++i];
    } else if (arg === "--out") {
      args.output = argv[++i];
    } else if (arg === "--no-names") {
      args.noNames = true;
    } else if (arg === "--fold-exprs") {
      args.foldExprs = true;
    }
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const inputPath = path.resolve(args.input);
  const outputPath = path.resolve(args.output);

  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input wasm not found: ${inputPath}`);
  }

  const wasmBuffer = fs.readFileSync(inputPath);
  const wabtFactory = require("wabt");
  const wabt = await wabtFactory();

  const wasmModule = wabt.readWasm(wasmBuffer, {
    readDebugNames: true,
  });

  if (!args.noNames) {
    wasmModule.generateNames();
    wasmModule.applyNames();
  }

  const wat = wasmModule.toText({
    foldExprs: args.foldExprs,
    inlineExport: false,
  });

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, wat);
  wasmModule.destroy();

  console.log(`Wrote ${outputPath}`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
