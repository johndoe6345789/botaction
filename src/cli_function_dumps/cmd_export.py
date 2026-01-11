# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *
import subprocess

def _decode_diter(binz_path: Path, params_path: Path, output_path: Path, decoder: str = "node") -> bool:
    root = Path(__file__).resolve().parents[2]
    if decoder == "python":
        try:
            from src.diter_decoder import decode_diter_file
        except Exception as exc:
            print(f"Error: Python DITER decoder unavailable ({exc})")
            return False
        wasm_path = root / "downloads" / "diter_wasm_blob.wasm"
        wasm_b64_path = root / "downloads" / "diter_wasm_blob.js"
        key_source = root / "downloads" / "diter_standalone_deob.js"
        if not key_source.exists():
            fallback = root / "downloads" / "diter_standalone.js"
            key_source = fallback if fallback.exists() else None
        try:
            decode_diter_file(
                binz_path,
                params_path,
                output_path,
                wasm_path=wasm_path if wasm_path.exists() else None,
                wasm_b64_path=wasm_b64_path if wasm_b64_path.exists() else None,
                key_source=key_source,
            )
        except Exception as exc:
            print(f"Error: Python DITER decode failed ({exc})")
            return False
        return True

    script_path = root / "scripts" / "diter_decode.js"
    if not script_path.exists():
        print(f"Error: DITER decoder not found at {script_path}")
        return False
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
    except subprocess.CalledProcessError as exc:
        print(f"Error: DITER decode failed ({exc})")
        return False
    return True


def cmd_export(args):
    """Export models to 3MF or STL format."""
    msgs = get_messages()['export']
    symbols = get_symbols()
    output_path = Path(args.output)
    export_format = (args.format or "3mf").lower()

    if export_format == "3mf":
        try:
            from src.export_3mf import Model3MFExporter
        except ImportError:
            print(msgs['error_import'])
            return 1

        if not args.binz_file:
            print(msgs['error_not_found'].format(path=""))
            return 1
        binz_path = Path(args.binz_file)
        if not binz_path.exists():
            print(msgs['error_not_found'].format(path=binz_path))
            return 1

        print(msgs['exporting'].format(name=binz_path.name))
        try:
            exporter = Model3MFExporter()
            exporter.load_from_binary(binz_path)
            exporter.export_3mf(output_path)

            print(f"{symbols['checkmark']} {msgs['exported'].format(path=output_path)}")
            print(f"  {msgs['vertices'].format(count=len(exporter.vertices))}")
            print(f"  {msgs['triangles'].format(count=len(exporter.triangles))}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    if export_format != "stl":
        print(f"Error: Unsupported export format: {export_format}")
        return 1

    try:
        from src.export_stl import ModelSTLExporter
    except ImportError:
        print(msgs.get('error_import_stl', "Error: Could not import STL exporter"))
        return 1

    geometry_path = Path(args.geometry) if args.geometry else None
    if not geometry_path or not geometry_path.exists():
        print(msgs.get('error_geometry_not_found', "Error: geometry file not found: {path}").format(
            path=geometry_path or ""
        ))
        return 1

    params_path = Path(args.params) if args.params else None
    if args.params and (not params_path or not params_path.exists()):
        print(msgs.get('error_params_missing', "Error: params file required for DITER decode"))
        return 1

    osgjs_path = Path(args.osgjs) if args.osgjs else None
    binz_path = Path(args.binz_file) if args.binz_file else None
    if osgjs_path is None:
        if binz_path is None or not binz_path.exists():
            print(msgs.get('error_osgjs_missing', "Error: OSGJS source not provided"))
            return 1
        if "model_file" in binz_path.name:
            print(msgs.get('error_osgjs_missing', "Error: OSGJS source not provided"))
            return 1
        if not params_path:
            print(msgs.get('error_params_missing', "Error: params file required for DITER decode"))
            return 1
        osgjs_path = binz_path.with_suffix(".osgjs.json")
        if not osgjs_path.exists() or args.force_decode:
            if not _decode_diter(binz_path, params_path, osgjs_path, args.decoder):
                return 1

    if not osgjs_path.exists():
        print(msgs.get('error_osgjs_not_found', "Error: OSGJS file not found: {path}").format(path=osgjs_path))
        return 1

    geometry_to_use = geometry_path
    if params_path and (args.force_decode or "decoded" not in geometry_path.stem.lower()):
        decoded_geometry_path = geometry_path.with_name(f"{geometry_path.stem}_decoded{geometry_path.suffix}")
        if args.force_decode or not decoded_geometry_path.exists():
            print(msgs.get('decoding_geometry', "Decoding geometry {name} with DITER...").format(
                name=geometry_path.name
            ))
            if _decode_diter(geometry_path, params_path, decoded_geometry_path, args.decoder):
                print(msgs.get('geometry_decoded', "Decoded geometry saved to: {path}").format(
                    path=decoded_geometry_path
                ))
            else:
                if args.force_decode:
                    return 1
                print(msgs.get('geometry_decode_failed', "Warning: geometry decode failed, using raw file"))
                decoded_geometry_path = geometry_path
        geometry_to_use = decoded_geometry_path

    print(msgs.get('exporting_stl', "Exporting {name} to STL...").format(name=osgjs_path.name))
    try:
        exporter = ModelSTLExporter()
        exporter.load_from_osgjs(osgjs_path, [geometry_to_use])
        exporter.export_stl(output_path)

        print(f"{symbols['checkmark']} {msgs.get('stl_exported', 'STL saved to: {path}').format(path=output_path)}")
        print(f"  {msgs['vertices'].format(count=exporter.vertex_count)}")
        print(f"  {msgs['triangles'].format(count=len(exporter.triangles))}")

        if args.screenshot:
            screenshot_path = Path(args.screenshot)
            exporter.render_preview(screenshot_path)
            print(f"{symbols['checkmark']} {msgs.get('screenshot_saved', 'Screenshot saved to: {path}').format(path=screenshot_path)}")

        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
