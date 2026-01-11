# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_markdown(args):
    """Display markdown syntax reference from Sketchfab's editor."""
    
    print(HEADERS['markdown_reference'])
    print("=" * 60)
    print(SUBHEADERS['based_on_editor'])
    print()
    
    for category, buttons in MARKDOWN_TOOLBAR.items():
        display_name = category.replace('_', ' ').title()
        print(f"\n{display_name}:")
        print("-" * 40)
        
        for btn in buttons:
            shortcut = f" ({btn['shortcut']})" if btn.get('shortcut') else ""
            syntax = btn['syntax'].replace('\n', '\\n')
            print(f"  {btn['label']:20}{shortcut}")
            print(f"    Syntax: {syntax}")
    
    print(f"\n\n{HEADERS['examples']}")
    print("-" * 40)
    for example in MARKDOWN_EXAMPLES:
        print(f"  {example['syntax']:20} → {example['result']}")
    
    return 0
