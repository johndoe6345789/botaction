# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_stats(args):
    """Fetch and display model statistics."""
    try:
        import requests
    except ImportError:
        print("Error: requests library required. Install with: pip install requests")
        return 1
    
    model_id = extract_model_id(args.model_id_or_url)
    if not model_id:
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
        return 1
    
    print(f"Fetching stats for model: {model_id}")
    
    api_url = f"{SKETCHFAB_API_BASE}/models/{model_id}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    if args.token:
        headers['Authorization'] = f'Token {args.token}'
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("\nModel Information:")
        print("=" * 50)
        print(f"  Name: {data.get('name', 'Unknown')}")
        print(f"  UID: {data.get('uid', model_id)}")
        
        user = data.get('user', {})
        print(f"  Author: {user.get('displayName', user.get('username', 'Unknown'))}")
        
        print(f"\nStats:")
        print(f"  Views: {data.get('viewCount', 0):,}")
        print(f"  Likes: {data.get('likeCount', 0):,}")
        print(f"  Comments: {data.get('commentCount', 0):,}")
        
        if data.get('isDownloadable'):
            print(f"  Downloads: {data.get('downloadCount', 0):,}")
        
        print(f"\nProperties:")
        print(f"  Downloadable: {'Yes' if data.get('isDownloadable') else 'No'}")
        print(f"  Animated: {'Yes' if data.get('isAnimated') else 'No'}")
        print(f"  Staff Pick: {'Yes' if data.get('staffpickedAt') else 'No'}")
        
        license_info = data.get('license', {})
        if license_info:
            print(f"  License: {license_info.get('label', 'Unknown')}")
        
        categories = data.get('categories', [])
        if categories:
            cat_names = [c.get('name', 'Unknown') for c in categories]
            print(f"  Categories: {', '.join(cat_names)}")
        
        tags = data.get('tags', [])
        if tags:
            tag_names = [t.get('name', t) if isinstance(t, dict) else t for t in tags[:10]]
            print(f"  Tags: {', '.join(tag_names)}")
        
        if args.json:
            print(f"\nRaw JSON:")
            print(json.dumps(data, indent=2))
        
        return 0
        
    except requests.RequestException as e:
        print(f"Error fetching model: {e}")
        return 1
