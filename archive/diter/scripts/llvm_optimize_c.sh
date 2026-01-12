#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <input.c> [output-dir]" >&2
  echo "Outputs optimized LLVM IR and (if llvm-cbe is installed) C." >&2
  exit 1
fi

INPUT="$1"
OUT_DIR="${2:-build/llvm_opt}"

if [[ ! -f "$INPUT" ]]; then
  echo "Input not found: $INPUT" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

BASENAME="$(basename "$INPUT" .c)"
IR_RAW="$OUT_DIR/${BASENAME}.ll"
IR_OPT="$OUT_DIR/${BASENAME}.opt.ll"
IR_BC="$OUT_DIR/${BASENAME}.bc"

clang -S -emit-llvm -O0 "$INPUT" -o "$IR_RAW"
opt -O2 -S "$IR_RAW" -o "$IR_OPT"
opt -O2 "$IR_RAW" -o "$IR_BC"

if command -v llvm-cbe >/dev/null 2>&1; then
  C_OUT="$OUT_DIR/${BASENAME}.opt.c"
  llvm-cbe "$IR_BC" -o "$C_OUT"
  echo "Wrote: $C_OUT"
else
  echo "llvm-cbe not found; wrote optimized IR instead: $IR_OPT"
  echo "Install llvm-cbe to emit C from optimized IR."
fi
