# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_webgl(args):
    """Display WebGL error types and troubleshooting."""
    
    print(HEADERS['webgl_errors'])
    print("=" * 60)
    print()
    
    for error_type, info in WEBGL_ERRORS.items():
        print(f"\n{error_type.upper()}")
        print("-" * 40)
        print(f"{WEBGL_LABELS['title']} {info['title']}")
        print(f"{WEBGL_LABELS['message']} {info['message']}")
        print(WEBGL_LABELS['suggestions'])
        for suggestion in info['suggestions']:
            print(f"  • {suggestion}")
    
    print(f"\n\n{WEBGL_LABELS['detection_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['webgl_detection'])
    
    return 0
