# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_export(args):
    """Export decrypted model to 3MF format."""
    msgs = get_messages()['export']
    symbols = get_symbols()
    try:
        from src.export_3mf import Model3MFExporter
    except ImportError:
        print(msgs['error_import'])
        return 1

    binz_path = Path(args.binz_file)
    output_path = Path(args.output)

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
