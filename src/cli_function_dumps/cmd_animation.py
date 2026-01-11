# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_animation(args):
    """Display spring animation presets."""
    
    print(HEADERS['spring_animation'])
    print("=" * 60)
    print(SUBHEADERS['physics_based'])
    print()
    
    for name, preset in SPRING_PRESETS.items():
        print(f"\n{name.upper()}")
        print(f"  {ANIMATION_LABELS['stiffness']} {preset['stiffness']}")
        print(f"  {ANIMATION_LABELS['damping']} {preset['damping']}")
        print(f"  {ANIMATION_LABELS['description']} {preset['desc']}")
    
    print(f"\n\n{ANIMATION_LABELS['formula_header']}")
    print("-" * 40)
    for formula in SPRING_FORMULAS:
        print(f"  {formula['formula']}  ({formula['description']})")
    print()
    for variable in SPRING_VARIABLES:
        print(f"  {variable['var']} = {variable['description']}")
    
    if args.generate_js:
        print(f"\n\n{ANIMATION_LABELS['js_impl_header']}")
        print("-" * 40)
        print(CODE_SNIPPETS['spring_js'])
    
    return 0
