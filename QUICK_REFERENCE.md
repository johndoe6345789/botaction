# Sketchfab Decryption - Quick Reference

## TL;DR

**Encryption**: AES-256-CBC  
**Key Location**: Base64-encoded in `*_params.json` file  
**Key Format**: First 32 bytes = key, next 16 bytes = IV  
**Output**: Raw binary geometry data (NOT compressed)

## One-Command Decryption

```bash
python demo_decryption.py
```

## Code Snippet

```python
from Crypto.Cipher import AES
import base64, json

# Load params
with open('params.json') as f:
    p = json.load(f)[0]

# Extract key & IV
d = base64.b64decode(p['b'])
key, iv = d[:32], d[32:48]

# Decrypt
with open('model.binz', 'rb') as f:
    enc = f.read()
enc = enc[:len(enc)//16*16]  # Align to 16 bytes

cipher = AES.new(key, AES.MODE_CBC, iv)
data = cipher.decrypt(enc)

# data is now raw Float32Array geometry
```

## Key Points

1. **Not Compressed**: Decrypted data is raw binary, no zlib
2. **16-Byte Alignment**: Truncate file to multiple of 16 before decrypt
3. **Client-Side**: Browser gets the key, so we can too
4. **Works Universally**: Same scheme for all encrypted Sketchfab models

## Files You Need

- `model.binz` - Encrypted geometry file
- `model_params.json` - Contains encryption key (as base64)

## Test with Annihilator 2000

```bash
# Files are already downloaded in downloads/
python demo_decryption.py

# Output: annihilator_2000_decrypted.bin
```

## Next Steps

1. Parse `.osgjs` metadata to understand layout
2. Extract vertex arrays (position, normal, UV)
3. Export to OBJ/glTF

---

For full details see: **SOLUTION_SUMMARY.md**
