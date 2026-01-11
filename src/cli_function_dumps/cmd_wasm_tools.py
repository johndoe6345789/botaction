# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *
import base64
import shutil
import subprocess


def _resolve_tool(root: Path, name: str):
    local = root / "node_modules" / ".bin" / name
    if local.exists():
        return str(local)
    local_cmd = local.with_suffix(".cmd")
    if local_cmd.exists():
        return str(local_cmd)
    system = shutil.which(name)
    if system:
        return system
    return None


def _run_node(script_path: Path, args, step, msgs, root: Path):
    if not script_path.exists():
        print(msgs['missing_script'].format(path=script_path))
        return False
    cmd = ["node", str(script_path)] + args
    try:
        subprocess.run(cmd, check=True, cwd=root)
    except subprocess.CalledProcessError as exc:
        print(msgs['command_failed'].format(step=step, error=exc))
        return False
    return True


def _extract_base64(text: str) -> str:
    double_idx = text.find('"')
    single_idx = text.find("'")
    if double_idx == -1 and single_idx == -1:
        return text.strip()
    if double_idx == -1 or (single_idx != -1 and single_idx < double_idx):
        quote = "'"
        start = single_idx
    else:
        quote = '"'
        start = double_idx
    end = text.rfind(quote)
    if end <= start:
        return text.strip()
    return text[start + 1:end]


def _decode_wasm_b64(input_path: Path, output_path: Path, msgs, symbols) -> bool:
    if not input_path.exists():
        print(msgs['missing_input'].format(path=input_path))
        return False
    try:
        text = input_path.read_text(encoding="utf-8", errors="replace")
        b64_text = _extract_base64(text)
        b64_text = b64_text.replace("\\n", "").replace("\\r", "")
        b64_text = "".join(b64_text.split())
        decoded = base64.b64decode(b64_text)
    except Exception as exc:
        print(msgs['command_failed'].format(step="decode-wasm", error=exc))
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(decoded)
    print(f"{symbols['checkmark']} {msgs['wrote'].format(path=output_path)}")
    return True


def cmd_wasm_tools(args):
    """Run WASM reverse tooling for the DITER module."""
    msgs = get_messages()['wasm_tools']
    symbols = get_symbols()
    root = Path(__file__).resolve().parents[2]
    scripts_dir = root / "scripts"

    action = (args.action or "all").lower()
    standalone_path = Path(args.standalone)
    deps_path = Path(args.deps) if args.deps else None
    deob_path = Path(args.deob)
    wasm_b64_path = Path(args.wasm_b64)
    wasm_path = Path(args.wasm)
    wat_path = Path(args.wat)
    decompile_path = Path(args.decompile) if args.decompile else None

    def run_extract():
        print(msgs['extracting'])
        args_list = ["--out", str(standalone_path), "--module", args.module]
        if args.chunks:
            args_list += ["--chunks", args.chunks]
        if deps_path:
            args_list += ["--deps", str(deps_path)]
        if not _run_node(scripts_dir / "extract_diter.js", args_list, "extract", msgs, root):
            return False
        print(f"{symbols['checkmark']} {msgs['wrote'].format(path=standalone_path)}")
        if deps_path:
            print(f"{symbols['checkmark']} {msgs['wrote_deps'].format(path=deps_path)}")
        return True

    def run_deobfuscate():
        if not standalone_path.exists():
            print(msgs['missing_input'].format(path=standalone_path))
            return False
        print(msgs['deobfuscating'])
        args_list = [
            "--in",
            str(standalone_path),
            "--out",
            str(deob_path),
            "--wasm",
            str(wasm_b64_path),
            "--rename-len",
            str(args.rename_len),
        ]
        if not _run_node(scripts_dir / "deobfuscate_diter.js", args_list, "deobfuscate", msgs, root):
            return False
        print(f"{symbols['checkmark']} {msgs['wrote'].format(path=deob_path)}")
        print(f"{symbols['checkmark']} {msgs['wrote'].format(path=wasm_b64_path)}")
        return True

    def run_decode_wasm():
        print(msgs['decoding_wasm'])
        return _decode_wasm_b64(wasm_b64_path, wasm_path, msgs, symbols)

    def run_wat():
        if not wasm_path.exists():
            print(msgs['missing_input'].format(path=wasm_path))
            return False
        print(msgs['converting_wat'])
        args_list = ["--in", str(wasm_path), "--out", str(wat_path)]
        if args.no_names:
            args_list.append("--no-names")
        if args.fold_exprs:
            args_list.append("--fold-exprs")
        if not _run_node(scripts_dir / "wasm_to_wat.js", args_list, "wat", msgs, root):
            return False
        print(f"{symbols['checkmark']} {msgs['wrote'].format(path=wat_path)}")
        return True

    def run_decompile():
        if not wasm_path.exists():
            print(msgs['missing_input'].format(path=wasm_path))
            return False
        if not decompile_path:
            return True
        tool = _resolve_tool(root, "wasm-decompile")
        if not tool:
            print(msgs['missing_tool'].format(name="wasm-decompile"))
            return False
        print(msgs['decompiling'])
        decompile_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(decompile_path, "w", encoding="utf-8") as handle:
                subprocess.run([tool, str(wasm_path)], check=True, stdout=handle, cwd=root)
        except subprocess.CalledProcessError as exc:
            print(msgs['command_failed'].format(step="decompile", error=exc))
            return False
        print(f"{symbols['checkmark']} {msgs['wrote'].format(path=decompile_path)}")
        return True

    if action == "all":
        steps = [run_extract, run_deobfuscate, run_decode_wasm, run_wat, run_decompile]
        for step in steps:
            if not step():
                return 1
        return 0

    actions = {
        "extract": run_extract,
        "deobfuscate": run_deobfuscate,
        "decode-wasm": run_decode_wasm,
        "wat": run_wat,
        "decompile": run_decompile,
    }

    handler = actions.get(action)
    if not handler:
        print(msgs['command_failed'].format(step=action, error="unknown action"))
        return 1
    return 0 if handler() else 1
