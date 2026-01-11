# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *


def cmd_diter_decode(args):
    """Decode DITER-compressed .binz using Python."""
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
    except Exception as exc:
        print(msgs['error_decode_failed'].format(error=exc))
        return 1

    print(f"{symbols['checkmark']} {msgs['decoded_bytes'].format(count=decoded_size)}")
    print(f"{symbols['checkmark']} {msgs['saved_to'].format(path=output_path)}")
    return 0
