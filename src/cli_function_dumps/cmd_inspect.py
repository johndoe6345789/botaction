# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_inspect(args):
    """Inspect a .binz file."""
    msgs = get_messages()['inspect']
    symbols = get_symbols()
    binz_path = Path(args.binz_file)

    if not binz_path.exists():
        print(f"Error: File not found: {binz_path}")
        return 1

    print(msgs['inspecting'].format(name=binz_path.name))
    print(msgs['size'].format(size=binz_path.stat().st_size))

    try:
        reader = BinzReader()
        data = reader.read_file(binz_path)
        print(msgs['decompressed_size'].format(size=len(data)))

        info = reader.inspect(data)
        print(f"\n{msgs['data_structure']}")
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Try to load params and parse geometry
        params_path = binz_path.with_suffix('.binz').parent / f"{binz_path.stem}_params.json"
        if params_path.exists():
            print(f"\n{msgs['found_params'].format(name=params_path.name)}")
            with open(params_path, 'r') as f:
                params = json.load(f)

            print(msgs['parsing_geometry'])
            geometry = reader.parse_geometry_from_params(data, params)

            if geometry.vertices:
                print(f"{symbols['checkmark']} {msgs['found_vertices'].format(count=geometry.vertex_count)}")
            if geometry.normals:
                print(f"{symbols['checkmark']} {msgs['found_normals'].format(count=geometry.normal_count)}")
            if geometry.uvs:
                print(f"{symbols['checkmark']} {msgs['found_uvs'].format(count=geometry.uv_count)}")
            if geometry.indices:
                print(f"{symbols['checkmark']} {msgs['found_indices'].format(count=geometry.index_count)}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1
