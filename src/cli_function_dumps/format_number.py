# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def format_number(num):
    """Format large numbers with K, M suffixes."""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)
