# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_filesize(args):
    """Format file sizes in human-readable format."""
    size_bytes = args.bytes
    
    if size_bytes < 0:
        print(ERROR_MESSAGES['size_must_be_positive'])
        return 1
    
    # Human-readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            print(f"{size_bytes:.2f} {unit}")
            break
        size_bytes /= 1024.0
    else:
        print(f"{size_bytes:.2f} PB")
    
    return 0
