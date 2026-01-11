# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_placements(args):
    """Display UI popup/tooltip placement options."""
    
    print(HEADERS['popup_placements'])
    print("=" * 60)
    print(SUBHEADERS['floating_ui'])
    print()
    
    # Group by direction
    directions = {'top': [], 'right': [], 'bottom': [], 'left': []}
    for placement in POPUP_PLACEMENTS:
        direction = placement.split('-')[0]
        directions[direction].append(placement)
    
    for direction, placements in directions.items():
        print(f"\n{direction.upper()}:")
        for p in placements:
            suffix = p.replace(direction, '').lstrip('-') or 'center'
            print(
                f"  {p:15} "
                f"{PLACEMENTS_LABELS['aligned'].format(suffix=suffix)}"
            )
    
    print(f"\n\n{PLACEMENTS_LABELS['usage_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['floating_ui'])
    
    return 0
