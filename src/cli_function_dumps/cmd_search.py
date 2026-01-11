# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_search(args):
    """Search for models on Sketchfab."""
    try:
        import requests
    except ImportError:
        print("Error: requests library required. Install with: pip install requests")
        return 1
    
    print(f"Searching for: {args.query}")
    
    # Build search URL
    params = {
        'q': args.query,
        'type': args.type or 'models',
    }
    
    if args.sort:
        params['sort_by'] = f"-{args.sort}" if args.sort != 'relevance' else args.sort
    if args.downloadable:
        params['downloadable'] = 'true'
    if args.animated:
        params['animated'] = 'true'
    if args.staffpicked:
        params['staffpicked'] = 'true'
    if args.category:
        params['categories'] = args.category
    if args.count:
        params['count'] = min(args.count, 24)  # Max 24 per request
    
    api_url = f"{SKETCHFAB_API_BASE}/search"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        total = data.get('totalCount', len(results))
        
        print(f"\nFound {total:,} results:")
        print("=" * 60)
        
        for i, item in enumerate(results, 1):
            name = item.get('name', 'Unknown')
            uid = item.get('uid', 'N/A')
            user = item.get('user', {}).get('displayName', item.get('user', {}).get('username', 'Unknown'))
            views = item.get('viewCount', 0)
            likes = item.get('likeCount', 0)
            
            print(f"\n{i}. {name}")
            print(f"   ID: {uid}")
            print(f"   Author: {user}")
            print(f"   Views: {format_number(views)} | Likes: {format_number(likes)}")
            
            if item.get('isDownloadable'):
                print(f"   ✓ Downloadable")
            if item.get('isAnimated'):
                print(f"   ✓ Animated")
            if item.get('staffpickedAt'):
                print(f"   ★ Staff Pick")
        
        if args.json:
            print(f"\n\nRaw JSON:")
            print(json.dumps(data, indent=2))
        
        return 0
        
    except requests.RequestException as e:
        print(f"Error searching: {e}")
        return 1
