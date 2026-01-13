"""Check what counts are being used"""
import json
from pathlib import Path

osgjs_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f.osgjs.json')
with open(osgjs_file) as f:
    data = json.load(f)

# Find all geometry nodes with vertex data
def find_all_arrays(obj, path="root", depth=0):
    if depth > 100:
        return
    if isinstance(obj, dict):
        if 'osg.Geometry' in obj:
            geom = obj['osg.Geometry']
            va_list = geom.get('VertexAttributeList', {})
            for attr_name, attr_data in va_list.items():
                if isinstance(attr_data, dict) and 'Array' in attr_data:
                    arr_block = attr_data['Array']
                    if arr_block:
                        arr_type = list(arr_block.keys())[0]
                        arr_info = arr_block[arr_type]
                        item_size = attr_data.get('ItemSize', 1)
                        size = arr_info.get('Size', 0)
                        offset = arr_info.get('Offset', 0)
                        encoding = arr_info.get('Encoding')
                        count = size * item_size
                        print(f"\nFound array at {path}/{attr_name}:")
                        print(f"  Type: {arr_type}")
                        print(f"  File: {arr_info.get('File')}")
                        print(f"  Offset: {offset:,}")
                        print(f"  Size: {size:,}")
                        print(f"  ItemSize: {item_size}")
                        print(f"  Count: {count:,}")
                        print(f"  Encoding: {encoding}")
                        if count > 100_000_000:
                            print(f"  ⚠️ WARNING: Count is very large!")

            prim_sets = geom.get('PrimitiveSetList', [])
            for i, prim in enumerate(prim_sets):
                for prim_type, prim_data in prim.items():
                    if 'Indices' in prim_data:
                        indices_attr = prim_data['Indices']
                        if 'Array' in indices_attr:
                            arr_block = indices_attr['Array']
                            if arr_block:
                                arr_type = list(arr_block.keys())[0]
                                arr_info = arr_block[arr_type]
                                item_size = indices_attr.get('ItemSize', 1)
                                size = arr_info.get('Size', 0)
                                offset = arr_info.get('Offset', 0)
                                encoding = arr_info.get('Encoding')
                                count = size * item_size
                                print(f"\nFound indices at {path}/PrimitiveSet[{i}]:")
                                print(f"  Type: {arr_type}")
                                print(f"  File: {arr_info.get('File')}")
                                print(f"  Offset: {offset:,}")
                                print(f"  Size: {size:,}")
                                print(f"  ItemSize: {item_size}")
                                print(f"  Count: {count:,}")
                                print(f"  Encoding: {encoding}")
                                if count > 100_000_000:
                                    print(f"  ⚠️ WARNING: Count is very large!")

        for key, value in obj.items():
            find_all_arrays(value, f"{path}/{key}", depth+1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_all_arrays(item, f"{path}[{i}]", depth+1)

find_all_arrays(data)
