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
        # Truncate to aligned size if necessary
        aligned_size = (len(encrypted_data) // 16) * 16
        if aligned_size != len(encrypted_data):
            print(f"Warning: File size {len(encrypted_data)} not aligned to 16 bytes, truncating to {aligned_size}")
            encrypted_data = encrypted_data[:aligned_size]
        
        # Decrypt using AES-256-CBC
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data)
        
        # Remove PKCS7 padding
        try:
            decrypted = unpad(decrypted, AES.block_size)
        except ValueError:
            # Data might not be padded, or padding is invalid
            # Just return as-is
            pass
        
        return decrypted
    
    def decrypt_and_decompress(
        self,
        encrypted_path: str | Path,
        params: list[Dict[str, Any]]
    ) -> bytes:
        """
        Decrypt and then decompress a .binz file.
        
        Args:
            encrypted_path: Path to encrypted file
            params: Encryption parameters
            
        Returns:
            Decompressed binary geometry data
        """
        import zlib
        
        # First decrypt
        decrypted = self.decrypt_file(encrypted_path, params)
        
        # Then decompress
        try:
            return zlib.decompress(decrypted)
        except zlib.error:
            try:
                return zlib.decompress(decrypted, -zlib.MAX_WBITS)
            except zlib.error:
                return zlib.decompress(decrypted, zlib.MAX_WBITS | 16)


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
