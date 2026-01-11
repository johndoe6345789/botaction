# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_decrypt(args):
    """Decrypt an encrypted .binz file."""
    msgs = get_messages()['decrypt']
    binz_path = Path(args.binz_file)
    params_path = Path(args.params_file) if args.params_file else None

    if not binz_path.exists():
        print(msgs['error_binz_not_found'].format(path=binz_path))
        return 1

    if params_path and not params_path.exists():
        print(msgs['error_params_not_found'].format(path=params_path))
        return 1

    print(msgs['decrypting'].format(name=binz_path.name))

    try:
        if params_path:
            # Use the convenience function
            decrypted_data = decrypt_model(binz_path, params_path)
        else:
            # Manual decryption with key
            if not args.key:
                print(msgs['error_need_key'])
                return 1

            try:
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import unpad
            except ImportError:
                print(msgs['error_pycryptodome'])
                return 1

            decryptor = SketchfabDecryptor()
            key, iv = decryptor.decode_encryption_params(args.key)

            # Read and decrypt
            with open(binz_path, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt AES-256-CBC
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

            # Try to decompress if it looks compressed
            import zlib
            if len(decrypted_data) >= 2 and decrypted_data[0] == 0x78 and decrypted_data[1] in (0x01, 0x9C, 0xDA):
                try:
                    decrypted_data = zlib.decompress(decrypted_data)
                except:
                    pass  # Not compressed, use as-is

        # Save decrypted file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        print(msgs['decrypted_bytes'].format(count=len(decrypted_data)))
        print(msgs['saved_to'].format(path=output_path))

        # Inspect if requested
        if args.inspect:
            reader = BinzReader()
            info = reader.inspect(decrypted_data)
            print(f"\n{msgs['inspection_header']}")
            for key, value in info.items():
                print(f"  {key}: {value}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1
