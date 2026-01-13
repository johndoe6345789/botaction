import json
from pathlib import Path

# Load the decoded OSGJS file
osgjs_path = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.osgjs.json')
with open(osgjs_path) as f:
    data = json.load(f)

print('Root keys:', list(data.keys())[:10])

# Find first geometry
def find_geom(obj, depth=0):
    if depth > 50 or not isinstance(obj, dict):
        return None
    if 'osg.Geometry' in obj:
        return obj['osg.Geometry']
    for v in obj.values():
        if isinstance(v, dict):
            r = find_geom(v, depth+1)
            if r:
                return r
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    r = find_geom(item, depth+1)
                    if r:
                        return r
    return None

geom = find_geom(data)
if geom and 'VertexAttributeList' in geom:
    print('\nFirst geometry found:')
    va = geom['VertexAttributeList'].get('Vertex', {})
    if 'Array' in va:
        arr_type = list(va['Array'].keys())[0] if va['Array'] else 'None'
        arr_data = va['Array'].get(arr_type, {})
        print(f'  Vertex Array Type: {arr_type}')
        print(f'  File: {arr_data.get("File")}')
        print(f'  Offset: {arr_data.get("Offset")}')
        print(f'  Size: {arr_data.get("Size")}')
        print(f'  ItemSize: {va.get("ItemSize")}')
        print(f'  Encoding: {arr_data.get("Encoding")}')

# Check model file size
model_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_model_file.binz')
if model_file.exists():
    size = model_file.stat().st_size
    print(f'\nModel file size: {size} bytes')
    print(f'Offset exceeds buffer: {arr_data.get("Offset", 0)} > {size}')
