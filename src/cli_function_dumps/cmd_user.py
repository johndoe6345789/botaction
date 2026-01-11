# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_user(args):
    """Look up a Sketchfab user."""
    try:
        import requests
    except ImportError:
        print("Error: requests library required. Install with: pip install requests")
        return 1
    
    username = args.username.lstrip('@')
    print(f"Looking up user: {username}")
    
    api_url = f"{SKETCHFAB_API_BASE}/users/{username}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        user = response.json()
        
        print("\nUser Information:")
        print("=" * 50)
        print(f"  Username: {user.get('username', 'N/A')}")
        print(f"  Display Name: {user.get('displayName', 'N/A')}")
        print(f"  UID: {user.get('uid', 'N/A')}")
        
        if user.get('bio'):
            bio = user['bio'][:100] + '...' if len(user.get('bio', '')) > 100 else user.get('bio', '')
            print(f"  Bio: {bio}")
        
        if user.get('location'):
            print(f"  Location: {user.get('location')}")
        if user.get('website'):
            print(f"  Website: {user.get('website')}")
        
        print(f"\nStats:")
        print(f"  Models: {user.get('modelCount', 0):,}")
        print(f"  Followers: {user.get('followerCount', 0):,}")
        print(f"  Following: {user.get('followingCount', 0):,}")
        print(f"  Likes: {user.get('likeCount', 0):,}")
        
        print(f"\nStatus:")
        if user.get('isVerified'):
            print(f"  ✓ Verified")
        if user.get('isPro'):
            print(f"  ★ Pro Account")
        if user.get('isStaff'):
            print(f"  ⚡ Staff")
        
        print(f"\nProfile URL: {SKETCHFAB_BASE_URL}/@{username}")
        print(f"Models URL: {SKETCHFAB_BASE_URL}/@{username}/models")
        
        if args.models:
            # Fetch user's models
            models_url = f"{SKETCHFAB_API_BASE}/users/{username}/models"
            models_response = requests.get(models_url, headers=headers, timeout=10)
            models_response.raise_for_status()
            models_data = models_response.json()
            
            models = models_data.get('results', [])
            print(f"\nRecent Models ({len(models)} shown):")
            print("-" * 40)
            for model in models[:10]:
                name = model.get('name', 'Unknown')
                uid = model.get('uid', '')
                views = format_number(model.get('viewCount', 0))
                print(f"  - {name} ({views} views)")
                print(f"    ID: {uid}")
        
        if args.json:
            print(f"\nRaw JSON:")
            print(json.dumps(user, indent=2))
        
        return 0
        
    except requests.RequestException as e:
        print(f"Error fetching user: {e}")
        return 1
