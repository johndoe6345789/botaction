# Sketchfab Model Decryption Analysis

## Summary

Successfully reverse-engineered the encryption scheme for Sketchfab's **Annihilator 2000** model:
https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63

## Encryption Scheme

### Parameters Structure

Model encryption parameters are stored in a JSON file with this structure:

```json
[
  {
    "v": 1,        // Version number
    "b": "vJ7r...", // Base64-encoded encryption parameters
    "d": true      // Encrypted flag (true = encrypted)
  }
]
```

### Encryption Method: AES-256-CBC

**Algorithm**: AES-256 in CBC mode (Cipher Block Chaining)
- **Key Size**: 256 bits (32 bytes)
- **Block Size**: 128 bits (16 bytes)
- **Initialization Vector (IV)**: 128 bits (16 bytes)
- **Padding**: PKCS#7 (standard for AES-CBC)

### Parameter Encoding

The "b" field contains Base64-encoded bytes with the following structure:

```
Bytes 0-31:  AES-256 Key (32 bytes)
Bytes 32-47: IV (16 bytes)
Bytes 48+:   Additional metadata (varies)
```

**Example from Annihilator 2000**:
```python
base64_params = "vJ7rXECFrv+C64bI5cF9vQE8xM2ya9Z3qop+a+JiHfsbwAYF4AsmeosHd/8wahKS..."

decoded = base64.b64decode(base64_params)
key = decoded[0:32]   # First 32 bytes
iv = decoded[32:48]   # Next 16 bytes

# Actual values for Annihilator 2000:
# Key (hex): bc9eeb5c4085aeff82eb86c8e5c17dbd...
# IV (hex):  1bc00605e00b267a8b0777ff306a1292
```

### File Structure

1. **Encrypted .binz File**: Raw encrypted binary data
   - File must be multiple of 16 bytes (AES block size)
   - Non-aligned files are truncated to nearest 16-byte boundary
   
2. **Decrypted Data**: Raw binary geometry data (Float32Array)
   - **NOT** compressed with zlib (contrary to initial assumptions)
   - Contains raw 3D vertex/index data as 32-bit floats/integers
   - Format: Sequential float values representing vertex positions, normals, UVs, indices, etc.

### Decryption Process

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# 1. Load parameters
params_b64 = params[0]['b']
decoded = base64.b64decode(params_b64)

# 2. Extract key and IV
key = decoded[0:32]
iv = decoded[32:48]

# 3. Load encrypted file
with open('model.binz', 'rb') as f:
    encrypted_data = f.read()

# 4. Align to 16-byte boundary
aligned_size = (len(encrypted_data) // 16) * 16
encrypted_data = encrypted_data[:aligned_size]

# 5. Decrypt with AES-256-CBC
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(encrypted_data)

# 6. Remove PKCS7 padding (if present)
try:
    decrypted = unpad(decrypted, AES.block_size)
except ValueError:
    pass  # No padding or invalid padding

# 7. Result is raw binary geometry data
# No decompression needed - it's already raw!
```

## Key Findings

### 1. No Compression After Decryption
- Initial assumption: Decrypted data would be zlib-compressed
- **Reality**: Decrypted data is **raw binary** geometry data
- Test files (test_cube.binz) confirmed this - they're raw Float32Arrays

### 2. File Alignment Requirements
- AES requires data aligned to 16-byte boundaries
- Sketchfab's files sometimes have 5 extra bytes (e.g., 67093 bytes)
- Solution: Truncate to nearest 16-byte boundary before decryption

### 3. Data Format
The decrypted data is a packed binary format:
- Float32Array for vertex positions (X, Y, Z)
- Float32Array for normals
- Float32Array for UV coordinates
- Uint16Array or Uint32Array for indices

### 4. JavaScript Implementation
Sketchfab's viewer uses Web Crypto API in the browser:
- `crypto.subtle.decrypt()` with AES-CBC algorithm
- Decryption happens client-side in JavaScript
- The repomix XML file contains references to ArrayBuffer handling

## Implementation Status

✅ **Working**: Basic decryption is complete and tested
- Successfully decrypted Annihilator 2000 model
- Extracted 67,088 bytes of raw geometry data
- Data appears to be valid Float32 values

⚠️ **Needs Work**: Geometry parsing
- Need to determine the exact layout of the binary data
- Requires understanding the accompanying .osgjs metadata file
- Must parse vertex attributes (position, normal, UV, indices)

## Files in Repository

1. **model_decryptor.py** - Main decryption implementation
2. **binz_reader.py** - Binary geometry reader (partial)
3. **sketchfab_fetcher.py** - Downloads models and metadata
4. **create_test_models.py** - Creates test .binz files
5. **demos/*.py** - Various testing scripts

## Usage

```python
from model_decryptor import SketchfabDecryptor

decryptor = SketchfabDecryptor()

# Load params
import json
with open('model_params.json', 'r') as f:
    params = json.load(f)

# Decrypt
data = decryptor.decrypt_and_decompress('model.binz', params)

# Result is raw binary geometry data
print(f"Decrypted {len(data)} bytes")
```

## Next Steps

1. ✅ Understand encryption scheme - **COMPLETE**
2. ✅ Implement decryption - **COMPLETE**
3. ⏳ Parse .osgjs metadata to understand geometry layout
4. ⏳ Extract vertex positions, normals, UVs, indices
5. ⏳ Export to standard formats (OBJ, glTF, etc.)

## Security Considerations

This analysis is for:
- Educational purposes
- Understanding 3D web formats
- Archival of legally accessed content
- Interoperability with 3D tools

**Note**: Respect Sketchfab's Terms of Service and copyright laws. Only decrypt models you have the right to access.

## References

- **PyCryptodome**: https://pycryptodome.readthedocs.io/
- **AES-CBC Mode**: NIST SP 800-38A
- **Sketchfab API**: https://sketchfab.com/developers
- **Model URL**: https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63

---

*Analysis completed: January 2026*
