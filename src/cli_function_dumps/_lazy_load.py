# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def _lazy_load(getter_func, cache_attr):
    """Helper to lazy-load data from JSON."""
    cache = {}
    def wrapper():
        if cache_attr not in cache:
            cache[cache_attr] = getter_func()
        return cache[cache_attr]
    return wrapper
