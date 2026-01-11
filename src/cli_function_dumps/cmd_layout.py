# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_layout(args):
    """Display responsive layout information."""
    
    if args.breakpoints:
        print(HEADERS['responsive_breakpoints'])
        print("=" * 60)
        
        for name, info in BREAKPOINTS.items():
            max_val = info['max'] if info['max'] else MAIN_LABELS['infinity']
            print(f"\n{name.upper()} - {info['desc']}")
            print(f"  Min: {info['min']}px")
            print(
                f"  Max: {max_val}px"
                if info['max']
                else f"  Max: {MAIN_LABELS['no_limit']}"
            )
            
            # Generate media query
            if info['min'] == 0 and info['max']:
                print(f"  Media Query: @media (max-width: {info['max']}px)")
            elif info['max']:
                print(f"  Media Query: @media (min-width: {info['min']}px) and (max-width: {info['max']}px)")
            else:
                print(f"  Media Query: @media (min-width: {info['min']}px)")
        return 0
    
    if args.dimensions:
        print(HEADERS['layout_dimensions'])
        print("=" * 60)
        
        for component, dims in LAYOUT_DIMENSIONS.items():
            print(f"\n{component.upper()}:")
            for key, value in dims.items():
                print(f"  {key}: {value}px")
        return 0
    
    if args.spacing:
        print(HEADERS['spacing_scale'])
        print("=" * 60)
        
        for level, value in SPACING_SCALE.items():
            print(f"  {level:3}: {value}")
        
        print(f"\n\n{HEADERS['css_custom_props']}")
        for level, value in SPACING_SCALE.items():
            print(f"  --spacing-{level}: {value};")
        return 0
    
    if args.generate_scss:
        print("// Sketchfab SCSS Variables")
        print()
        print("// Breakpoints")
        print("$breakpoints: (")
        for name, info in BREAKPOINTS.items():
            print(f"  '{name}': {info['min']}px,")
        print(");")
        print()
        print("// Spacing")
        print("$spacing: (")
        for level, value in SPACING_SCALE.items():
            print(f"  {level}: {value},")
        print(");")
        print()
        print("// Layout")
        for component, dims in LAYOUT_DIMENSIONS.items():
            for key, value in dims.items():
                var_name = f"${component}-{key}".replace('_', '-').lower()
                # Convert camelCase to kebab-case
                var_name = re.sub(r'([a-z])([A-Z])', r'\1-\2', var_name).lower()
                print(f"{var_name}: {value}px;")
        return 0
    
    # Default: show summary
    print(HEADERS['layout_responsive'])
    print("=" * 60)
    print(f"\n{LAYOUT_SUMMARY['options_header']}")
    print("  --breakpoints    Show responsive breakpoints")
    print("  --dimensions     Show layout dimensions")
    print("  --spacing        Show spacing scale")
    print("  --generate-scss  Generate SCSS variables")
    print()
    print(LAYOUT_SUMMARY['quick_stats'])
    print(
        f"  {LAYOUT_SUMMARY['breakpoints']} {len(BREAKPOINTS)} "
        f"({', '.join(BREAKPOINTS.keys())})"
    )
    print(f"  {LAYOUT_SUMMARY['spacing_levels']} {len(SPACING_SCALE)}")
    print(f"  {LAYOUT_SUMMARY['layout_components']} {len(LAYOUT_DIMENSIONS)}")
    
    return 0
