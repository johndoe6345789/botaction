# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_validate(args):
    """Validate input values against Sketchfab patterns."""
    value = args.value
    val_type = args.type
    
    if val_type not in VALIDATION_PATTERNS:
        print(f"Unknown validation type: {val_type}")
        print(f"Available types: {', '.join(VALIDATION_PATTERNS.keys())}")
        return 1
    
    pattern = VALIDATION_PATTERNS[val_type]
    
    if re.match(pattern, value):
        print(f"✓ Valid {val_type}: {value}")
        return 0
    else:
        print(f"✗ Invalid {val_type}: {value}")
        print(f"  Expected pattern: {pattern}")
        return 1
