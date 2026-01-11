# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_thumbnail(args):
    """Generate thumbnail URLs for a model."""
    model_id = extract_model_id(args.model_id_or_url)
    
    if not model_id:
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
        return 1
    
    print(f"Thumbnail URLs for model: {model_id}")
    print("=" * 60)
    
    # Generate Sketchfab CDN thumbnail URLs
    base_url = f"https://media.sketchfab.com/models/{model_id}/thumbnails"
    
    print("\nStandard Thumbnails:")
    for size_name, dims in THUMBNAIL_SIZES.items():
        url = f"{base_url}/{dims['width']}x{dims['height']}.jpeg"
        print(f"  {size_name.capitalize()} ({dims['width']}x{dims['height']}):")
        print(f"    {url}")
    
    print("\nAlternative Formats:")
    print(f"  Default: {base_url}/default.jpeg")
    print(f"  Square: {base_url}/200x200.jpeg")
    
    if args.fetch:
        try:
            import requests
            api_url = f"{SKETCHFAB_API_BASE}/models/{model_id}"
            response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            thumbnails = data.get('thumbnails', {}).get('images', [])
            if thumbnails:
                print(f"\nActual Thumbnails from API ({len(thumbnails)} available):")
                for thumb in thumbnails:
                    width = thumb.get('width', 'N/A')
                    height = thumb.get('height', 'N/A')
                    url = thumb.get('url', 'N/A')
                    print(f"  {width}x{height}: {url}")
        except Exception as e:
            print(f"\nCould not fetch actual thumbnails: {e}")
    
    return 0
