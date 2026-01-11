# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_config(args):
    """Display or generate viewer configuration."""
    
    if args.list_presets:
        print("Quality Presets:")
        print("=" * 50)
        for name, preset in QUALITY_PRESETS.items():
            print(f"\n{name.upper()}:")
            for key, value in preset.items():
                print(f"  {key}: {value}")
        
        print("\n\nEnvironment Presets:")
        print("=" * 50)
        for name, preset in ENVIRONMENT_PRESETS.items():
            print(f"\n{name.upper()}:")
            for key, value in preset.items():
                print(f"  {key}: {value}")
        return 0
    
    if args.list_embed_options:
        print("Embed URL Options:")
        print("=" * 50)
        for name, info in EMBED_OPTIONS.items():
            type_str = info['type'].__name__
            default = info['default']
            desc = info['desc']
            print(f"\n{name}:")
            print(f"  Type: {type_str}")
            print(f"  Default: {default}")
            print(f"  Description: {desc}")
        return 0
    
    if args.list_materials:
        print("Material Display Options:")
        print("=" * 50)
        for name, desc in MATERIAL_OPTIONS.items():
            print(f"  {name}: {desc}")
        return 0
    
    if args.generate:
        config = {
            'renderer': {
                'antialias': True,
                'alpha': False,
                'powerPreference': 'high-performance',
            },
            'camera': {
                'fov': args.fov or 45,
                'near': 0.1,
                'far': 10000,
            },
            'controls': {
                'enabled': True,
                'autoRotate': args.auto_rotate or False,
                'enablePan': True,
                'enableZoom': True,
            },
            'lighting': {
                'environment': args.environment or 'studio',
                'exposure': args.exposure or 1,
                'shadowsEnabled': not args.no_shadows,
            },
            'postProcessing': {
                'enabled': not args.no_postprocessing,
                'ssaoEnabled': args.ssao or False,
                'bloomEnabled': args.bloom or False,
            },
        }
        
        if args.quality and args.quality in QUALITY_PRESETS:
            config['quality'] = QUALITY_PRESETS[args.quality]
        
        print(json.dumps(config, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\nConfig saved to: {args.output}")
        
        return 0
    
    # Default: show help
    print("Use one of the following options:")
    print("  --list-presets       Show quality and environment presets")
    print("  --list-embed-options Show embed URL parameters")
    print("  --list-materials     Show material display options")
    print("  --generate           Generate viewer configuration JSON")
    return 0
