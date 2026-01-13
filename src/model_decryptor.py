"""
Sketchfab Model Decryptor

Handles decryption of encrypted .binz files from Sketchfab.
The encryption uses AES with parameters stored in base64 format.
"""

import base64
import struct
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import json

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class SketchfabDecryptor:
    """Decrypts encrypted Sketchfab model files."""
    
    def __init__(self):
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "PyCryptodome is required for decryption. "
                "Install it with: pip install pycryptodome"
            )
    
    def decode_encryption_params(self, params_b64: str) -> Tuple[bytes, bytes]:
        """
        Decode base64-encoded encryption parameters.
        
        Format: First 32 bytes = AES key, Next 16 bytes = IV
        
        Args:
            params_b64: Base64-encoded parameter string
            
        Returns:
            Tuple of (key, iv)
        """
        # Decode base64
        decoded = base64.b64decode(params_b64)
        
        # Extract key and IV
        key = decoded[:32]  # AES-256 uses 32-byte key
        iv = decoded[32:48]  # AES uses 16-byte IV
        
        return key, iv
    
    def decrypt_file(
        self,
        encrypted_path: str | Path,
        params: list[Dict[str, Any]]
    ) -> bytes:
        """
        Decrypt an encrypted .binz file.
        
        Args:
            encrypted_path: Path to the encrypted .binz file
            params: Encryption parameters from the model config
            
        Returns:
            Decrypted binary data
        """
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Get first param (usually only one)
        if not params or not isinstance(params, list):
            raise ValueError("Invalid params format")
        
        param = params[0]
        
        # Check if encrypted
        if not param.get('d', False):
            # Not encrypted, return as-is
            return encrypted_data
        
        # Get encryption parameters
        params_b64 = param.get('b', '')
        if not params_b64:
            raise ValueError("No encryption parameters found")
        
        # Decode key and IV
        key, iv = self.decode_encryption_params(params_b64)
        
        # AES requires data to be multiple of 16 bytes
        # Sketchfab may have non-aligned encrypted files - pad with null bytes
        original_size = len(encrypted_data)
        if original_size % 16 != 0:
            padding_needed = 16 - (original_size % 16)
            print(f"Warning: File size {original_size} not aligned to 16 bytes, padding with {padding_needed} null bytes")
            # Pad with null bytes (0x00) which is safer than truncating
            encrypted_data = encrypted_data + b'\x00' * padding_needed
        
        # Decrypt using AES-256-CBC
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data)

        # Sketchfab files may not use standard PKCS7 padding
        # Try to remove padding, but don't fail if it's not there
        try:
            decrypted_unpadded = unpad(decrypted, AES.block_size)
            # Check if unpadding made sense (didn't remove too much data)
            if len(decrypted_unpadded) > len(decrypted) * 0.9:  # Lost less than 10%
                decrypted = decrypted_unpadded
            else:
                print(f"Warning: Unpadding removed {len(decrypted) - len(decrypted_unpadded)} bytes, keeping original")
        except ValueError as e:
            # Data is not padded or padding is invalid - keep as-is
            print(f"Note: No valid PKCS7 padding found, using raw decrypted data ({e})")

        return decrypted
    
    def decrypt_and_decompress(
        self,
        encrypted_path: str | Path,
        params: list[Dict[str, Any]]
    ) -> bytes:
        """
        Decrypt and then decompress a .binz file.
        
        Note: Decrypted .binz files may NOT be compressed!
        They can be raw binary geometry data.
        
        Args:
            encrypted_path: Path to encrypted file
            params: Encryption parameters
            
        Returns:
            Binary geometry data (decompressed if it was compressed)
        """
        import zlib
        
        # First decrypt
        decrypted = self.decrypt_file(encrypted_path, params)
        
        # Check if it looks like zlib-compressed data
        # zlib header bytes: 78 01 (no compression), 78 9C (default), 78 DA (max compression)
        if len(decrypted) >= 2 and decrypted[0] == 0x78 and decrypted[1] in (0x01, 0x9C, 0xDA):
            # Looks like zlib, try to decompress
            try:
                return zlib.decompress(decrypted)
            except zlib.error:
                try:
                    return zlib.decompress(decrypted, -zlib.MAX_WBITS)
                except zlib.error:
                    try:
                        return zlib.decompress(decrypted, zlib.MAX_WBITS | 16)
                    except zlib.error:
                        # Not compressed, return as-is
                        print("Warning: Data has zlib-like header but decompression failed, returning as-is")
                        return decrypted
        else:
            # Not zlib-compressed, return raw binary data
            print("Note: Data is not zlib-compressed, returning raw binary")
            return decrypted


def decrypt_model(
    binz_path: str | Path,
    params_path: str | Path
) -> bytes:
    """
    Convenience function to decrypt a model.
    
    Args:
        binz_path: Path to .binz file
        params_path: Path to params.json file
        
    Returns:
        Decrypted and decompressed geometry data
    """
    decryptor = SketchfabDecryptor()
    
    # Load params
    with open(params_path, 'r') as f:
        params = json.load(f)
    
    # Decrypt and decompress
    return decryptor.decrypt_and_decompress(binz_path, params)


__all__ = [
    'SketchfabDecryptor',
    'decrypt_model',
    'CRYPTO_AVAILABLE',
]
