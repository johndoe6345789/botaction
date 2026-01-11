# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_grid(args):
    """Display responsive grid configuration."""
    
    print(HEADERS['responsive_grid'])
    print("=" * 60)
    print()
    
    for size, config in GRID_COLUMNS.items():
        print(
            f"{size.upper():10} "
            f"{GRID_LABELS['columns_at'].format(cols=config['columns'], breakpoint=config['breakpoint'])}"
        )
    
    print(f"\n\n{GRID_LABELS['css_impl_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['css_grid'])
    
    return 0
