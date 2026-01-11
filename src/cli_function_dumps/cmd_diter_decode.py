# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *
import subprocess


def cmd_diter_decode(args):
    """Decode DITER-compressed .binz."""
    msgs = get_messages()['diter_decode']
    symbols = get_symbols()

    binz_path = Path(args.binz_file)
    if not binz_path.exists():
        print(msgs['error_binz_not_found'].format(path=binz_path))
        return 1

    params_path = Path(args.params)
    if not params_path.exists():
        print(msgs['error_params_not_found'].format(path=params_path))
        return 1

    output_path = Path(args.output)
    wasm_path = Path(args.wasm) if args.wasm else None
    wasm_b64_path = Path(args.wasm_b64) if args.wasm_b64 else None
    key_source = Path(args.key_source) if args.key_source else None

    print(msgs['decoding'].format(name=binz_path.name))
    try:
        decoder = (args.decoder or "python").lower()
        if decoder == "python":
            from src.diter_decoder import decode_diter_file
            decoded_size = decode_diter_file(
                binz_path,
                params_path,
                output_path,
                wasm_path=wasm_path,
                wasm_b64_path=wasm_b64_path,
                key_hex=args.key_hex,
                key_source=key_source,
            )
        elif decoder == "node":
            root = Path(__file__).resolve().parents[2]
            script_path = root / "scripts" / "diter_decode.js"
            if not script_path.exists():
                raise RuntimeError(f"DITER decoder not found at {script_path}")
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
            subprocess.run(cmd, check=True)
            decoded_size = output_path.stat().st_size if output_path.exists() else 0
        elif decoder == "c":
            from src.diter_decoder_c import decode_diter_file
            if not wasm_path or not wasm_path.exists():
                raise RuntimeError("WASM binary required for C decoder.")
            decoded_size = decode_diter_file(
                binz_path,
                params_path,
                output_path,
                wasm_path=wasm_path,
                key_hex=args.key_hex,
                key_source=key_source,
            )
        else:
            raise RuntimeError(f"Unknown decoder: {decoder}")
    except Exception as exc:
        print(msgs['error_decode_failed'].format(error=exc))
        return 1

    print(f"{symbols['checkmark']} {msgs['decoded_bytes'].format(count=decoded_size)}")
    print(f"{symbols['checkmark']} {msgs['saved_to'].format(path=output_path)}")
    return 0
