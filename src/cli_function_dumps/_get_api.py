# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def _get_api():
    global _api_config
    if _api_config is None:
        _api_config = get_api_config()
    return _api_config
