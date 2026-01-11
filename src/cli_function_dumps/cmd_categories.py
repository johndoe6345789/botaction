# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_categories(args):
    """Display Sketchfab model categories."""
    print("Sketchfab Model Categories")
    print("=" * 40)
    
    for i, category in enumerate(SEARCH_CATEGORIES, 1):
        # Convert slug to display name
        display_name = category.replace('-', ' & ' if '-' in category else ' ').title()
        print(f"  {i:2}. {display_name}")
        print(f"      Slug: {category}")
    
    print(f"\nTotal: {len(SEARCH_CATEGORIES)} categories")
    print("\nUse these slugs with: python cli.py search --category <slug> <query>")
    
    return 0
