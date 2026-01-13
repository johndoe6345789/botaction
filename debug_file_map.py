import json
import sys
from pathlib import Path

# Direct import to avoid circular dependencies
sys.path.insert(0, str(Path(__file__).parent / 'src'))
import model_decryptor

# Check the model_file.binz
model_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_model_file.binz')
params_file = Path('downloads/dea4f17e94974e1fa720cbadc531ed63_7dffeb160ae740c082d33243f011454f_params.json')

print(f"Model file size: {model_file.stat().st_size}")
print(f"Params file exists: {params_file.exists()}")

# Load params
with open(params_file) as f:
    params = json.load(f)
print(f"Params: {params}")
print(f"Is encrypted: {params[0].get('d', False) if params else False}")

# Try to decrypt
if params and isinstance(params, list) and params[0].get('d', False):
    print("\nAttempting decryption...")
    decryptor = model_decryptor.SketchfabDecryptor()
    payload = decryptor.decrypt_file(model_file, params)
    print(f"Decrypted payload size: {len(payload)}")
else:
    print("\nFile is not encrypted, reading raw")
    payload = model_file.read_bytes()
    print(f"Raw payload size: {len(payload)}")
