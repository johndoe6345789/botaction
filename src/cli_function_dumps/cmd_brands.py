# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_brands(args):
    """Display brand/social media colors."""
    
    print(HEADERS['brand_colors'])
    print("=" * 60)
    
    for brand, color in BRAND_COLORS.items():
        # Create a simple visual indicator
        print(f"  {brand:15} {color}  {'█' * 3}")
    
    print(f"\n\n{HEADERS['usage_in_css']}")
    print("-" * 40)
    for brand, color in BRAND_COLORS.items():
        print(f"  --color-{brand}: {color};")
    
    return 0
