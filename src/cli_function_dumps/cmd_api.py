# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_api(args):
    """Display API endpoint information and utilities."""
    
    if args.list_endpoints:
        print("Sketchfab API Endpoints:")
        print("=" * 60)
        print(f"Base URL: {SKETCHFAB_API_BASE}")
        print()
        for name, endpoint in API_ENDPOINTS.items():
            full_url = SKETCHFAB_API_BASE + endpoint
            print(f"  {name}:")
            print(f"    {full_url}")
        return 0
    
    if args.build_url:
        endpoint_name = args.build_url
        if endpoint_name not in API_ENDPOINTS:
            print(f"Error: Unknown endpoint '{endpoint_name}'")
            print(f"Available: {', '.join(API_ENDPOINTS.keys())}")
            return 1
        
        endpoint = API_ENDPOINTS[endpoint_name]
        
        # Replace placeholders
        if args.model_id:
            endpoint = endpoint.replace('{model_id}', args.model_id)
        if args.username:
            endpoint = endpoint.replace('{username}', args.username)
        
        # Add query parameters
        params = {}
        if args.params:
            for param in args.params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        
        url = SKETCHFAB_API_BASE + endpoint
        if params:
            url += '?' + urlencode(params)
        
        print(f"API URL: {url}")
        
        if args.curl:
            curl_cmd = f'curl -X GET "{url}"'
            if args.token:
                curl_cmd += f' -H "Authorization: Token {args.token}"'
            print(f"\ncURL command:\n  {curl_cmd}")
        
        return 0
    
    if args.formats:
        print("Available Download Formats:")
        print("=" * 40)
        for fmt in DOWNLOAD_FORMATS:
            print(f"  - {fmt}")
        return 0
    
    if args.visibility:
        print("Visibility Types:")
        print("=" * 40)
        for vis_type, desc in VISIBILITY_TYPES.items():
            print(f"  {vis_type}: {desc}")
        return 0
    
    # Default
    print("API Information Commands:")
    print("  --list-endpoints   Show all API endpoints")
    print("  --build-url NAME   Build a specific API URL")
    print("  --formats          Show download formats")
    print("  --visibility       Show visibility types")
    return 0
