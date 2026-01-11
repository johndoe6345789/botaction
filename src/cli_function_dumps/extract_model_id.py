# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def extract_model_id(url_or_id):
    """Extract model ID from URL or return if already an ID."""
    # If it's already just an ID (alphanumeric, 32 chars)
    if re.match(r'^[a-f0-9]{32}$', url_or_id, re.IGNORECASE):
        return url_or_id
    
    # Try to extract from URL patterns
    patterns = [
        r'sketchfab\.com/(?:3d-)?models/[^/]+-([a-f0-9]{32})',  # /models/name-id
        r'sketchfab\.com/(?:3d-)?models/([a-f0-9]{32})',         # /models/id
        r'sketchfab\.com/models/([a-f0-9]{32})',                  # Direct model ID
        r'/([a-f0-9]{32})(?:/embed)?(?:\?|$)',                    # ID in path
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None
