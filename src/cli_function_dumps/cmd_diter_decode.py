# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_diter_decode(args):
    """Decode DITER-compressed .binz file."""
    msgs = get_messages()['diter_decode']
    binz_path = Path(args.binz_file)
    params_path = Path(args.params)
    output_path = Path(args.output)

    if not binz_path.exists():
        print(msgs['error_binz_not_found'].format(path=binz_path))
        return 1

    if not params_path.exists():
        print(msgs['error_params_not_found'].format(path=params_path))
        return 1

    print(msgs['decoding'].format(name=binz_path.name))

    decoder = args.decoder
    
    if decoder == "python":
        try:
            from src.diter_decoder import decode_diter_file
        except ImportError as e:
            print(f"Error: Python DITER decoder unavailable ({e})")
            return 1

        wasm_path = Path(args.wasm) if args.wasm else None
        wasm_b64_path = Path(args.wasm_b64) if args.wasm_b64 else None
        key_source = Path(args.key_source) if args.key_source else None

        try:
            decode_diter_file(
                binz_path,
                params_path,
                output_path,
                wasm_path=wasm_path if wasm_path and wasm_path.exists() else None,
                wasm_b64_path=wasm_b64_path if wasm_b64_path and wasm_b64_path.exists() else None,
                key_source=key_source if key_source and key_source.exists() else None,
                key_hex=args.key_hex if hasattr(args, 'key_hex') else None,
            )
            print(msgs['decoded'].format(path=output_path))
            return 0
        except Exception as e:
            print(f"Error: DITER decode failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

    elif decoder == "c":
        try:
            from src.diter_decoder_c import decode_diter_file
        except ImportError as e:
            print(f"Error: C DITER decoder unavailable ({e})")
            return 1

        key_source = Path(args.key_source) if args.key_source else None

        try:
            decode_diter_file(
                binz_path,
                params_path,
                output_path,
                key_source=key_source if key_source and key_source.exists() else None,
            )
            print(msgs['decoded'].format(path=output_path))
            return 0
        except Exception as e:
            print(f"Error: C DITER decode failed: {e}")
            return 1

    else:  # node decoder
        import subprocess
        root = Path(__file__).resolve().parents[2]
        script_path = root / "scripts" / "diter_decode.js"
        
        if not script_path.exists():
            print(f"Error: Node.js DITER decoder not found at {script_path}")
            return 1

        cmd = [
            "node",
            str(script_path),
            "--binz",
            str(binz_path),
            "--params",
            str(params_path),
            "--out",
            str(output_path),
        ]

        try:
            subprocess.run(cmd, check=True)
            print(msgs['decoded'].format(path=output_path))
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Error: Node.js DITER decode failed ({e})")
            return 1
