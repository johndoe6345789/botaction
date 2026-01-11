# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_design(args):
    """Display Sketchfab design system information."""
    
    if args.colors:
        print("Sketchfab Color Palette")
        print("=" * 60)
        
        for theme_name, colors in THEME_COLORS.items():
            print(f"\n{theme_name.upper()} THEME:")
            print("-" * 40)
            for color_name, color_value in colors.items():
                print(f"  {color_name:20} {color_value}")
        return 0
    
    if args.typography:
        print("Sketchfab Typography Scale")
        print("=" * 60)
        
        for level, props in TYPOGRAPHY_SCALE.items():
            print(f"\n{level.upper()}:")
            for prop, value in props.items():
                print(f"  {prop}: {value}")
        return 0
    
    if args.gradients:
        print("Sketchfab Gradient Presets")
        print("=" * 60)
        
        for name, colors in GRADIENT_PRESETS.items():
            print(f"\n{name.upper()}:")
            for key, value in colors.items():
                print(f"  {key}: {value}")
        return 0
    
    if args.shadows:
        print("Sketchfab Shadow Presets")
        print("=" * 60)
        
        for name, value in SHADOW_PRESETS.items():
            print(f"\n{name.upper()}:")
            print(f"  {value}")
        return 0
    
    if args.notifications:
        print("Sketchfab Notification Types")
        print("=" * 60)
        
        for notif_type, colors in NOTIFICATION_TYPES.items():
            print(f"\n{notif_type.upper()}:")
            for key, value in colors.items():
                print(f"  {key}: {value}")
        return 0
    
    if args.generate_css:
        theme = args.theme or 'light'
        if theme not in THEME_COLORS:
            print(f"Unknown theme: {theme}. Available: {', '.join(THEME_COLORS.keys())}")
            return 1
        
        print(f"/* Sketchfab {theme.title()} Theme CSS Variables */")
        print(":root {")
        for color_name, color_value in THEME_COLORS[theme].items():
            css_name = ''.join(['-' + c.lower() if c.isupper() else c for c in color_name]).lstrip('-')
            print(f"  --color-{css_name}: {color_value};")
        print("}")
        print()
        print("/* Typography */")
        for level, props in TYPOGRAPHY_SCALE.items():
            print(f".text-{level} {{")
            print(f"  font-size: {props['fontSize']};")
            print(f"  font-weight: {props['fontWeight']};")
            print(f"  line-height: {props['lineHeight']};")
            print("}")
        return 0
    
    # Default: show summary
    print("Sketchfab Design System")
    print("=" * 60)
    print("\nAvailable design information:")
    print("  --colors         Show color palettes (light/dark themes)")
    print("  --typography     Show typography scale")
    print("  --gradients      Show gradient presets")
    print("  --shadows        Show shadow presets")
    print("  --notifications  Show notification type colors")
    print("  --generate-css   Generate CSS variables")
    print("                   Use with --theme light|dark")
    print()
    print("Quick Stats:")
    print(f"  Themes: {', '.join(THEME_COLORS.keys())}")
    print(f"  Colors per theme: {len(THEME_COLORS['light'])}")
    print(f"  Typography levels: {len(TYPOGRAPHY_SCALE)}")
    print(f"  Gradient presets: {len(GRADIENT_PRESETS)}")
    print(f"  Shadow presets: {len(SHADOW_PRESETS)}")
    print(f"  Notification types: {len(NOTIFICATION_TYPES)}")
    
    return 0
