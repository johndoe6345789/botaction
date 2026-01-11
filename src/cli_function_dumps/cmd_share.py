# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_share(args):
    """Generate social sharing URLs for a model."""
    model_id = extract_model_id(args.model_id_or_url)
    
    if not model_id:
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
        return 1
    
    model_url = f"{SKETCHFAB_BASE_URL}/3d-models/{model_id}"
    text = args.text or DEFAULTS['share_text']

    print(f"{HEADERS['social_sharing']} {model_id}")
    print("=" * 60)
    print(f"\n{LABELS['model_url']} {model_url}")
    print()
    
    for platform in SHARE_PLATFORMS:
        share_url = platform['url_template'].format(
            url=model_url,
            text=text.replace(' ', '%20')
        )
        print(f"{platform['name']:12} {share_url}")
    
    if args.platform:
        platform = next((p for p in SHARE_PLATFORMS if p['id'] == args.platform), None)
        if platform:
            share_url = platform['url_template'].format(
                url=model_url,
                text=text.replace(' ', '%20')
            )
            print(f"\n{LABELS['direct_link_for'].format(platform=platform['name'])}")
            print(share_url)
    
    return 0
