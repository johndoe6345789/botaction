# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_parse_url(args):
    """Parse and analyze Sketchfab URLs."""
    url = args.url
    
    print(f"Parsing: {url}")
    print("=" * 60)
    
    # Parse URL components
    parsed = urlparse(url)
    print(f"\nURL Components:")
    print(f"  Scheme: {parsed.scheme}")
    print(f"  Host: {parsed.netloc}")
    print(f"  Path: {parsed.path}")
    
    if parsed.query:
        print(f"  Query: {parsed.query}")
        query_params = parse_qs(parsed.query)
        print(f"  Query Parameters:")
        for key, values in query_params.items():
            print(f"    {key}: {', '.join(values)}")
    
    if parsed.fragment:
        print(f"  Fragment: {parsed.fragment}")
    
    # Try to extract model ID
    model_id = extract_model_id(url)
    if model_id:
        print(f"\n  Extracted Model ID: {model_id}")
        print(f"  Direct URL: {SKETCHFAB_BASE_URL}/models/{model_id}")
        print(f"  Embed URL: {SKETCHFAB_BASE_URL}/models/{model_id}/embed")
        print(f"  API URL: {SKETCHFAB_API_BASE}/models/{model_id}")
    
    # Check for embed parameters
    if '/embed' in parsed.path and parsed.query:
        print(f"\nEmbed Options Detected:")
        for key, values in query_params.items():
            if key in EMBED_OPTIONS:
                info = EMBED_OPTIONS[key]
                print(f"  {key} = {values[0]} ({info['desc']})")
            else:
                print(f"  {key} = {values[0]} (custom)")
    
    return 0
