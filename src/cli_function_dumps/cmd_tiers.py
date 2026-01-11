# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_tiers(args):
    """Display subscription tier information."""
    print("Sketchfab Subscription Tiers")
    print("=" * 60)
    
    for tier_id, tier_info in SUBSCRIPTION_TIERS.items():
        print(f"\n{tier_info['name'].upper()}")
        if tier_info.get('badgeColor'):
            print(f"  Badge Color: {tier_info['badgeColor']}")
        print(f"  Features:")
        for feature, value in tier_info['features'].items():
            display_value = '✓' if value is True else ('✗' if value is False else value)
            print(f"    {feature}: {display_value}")
    
    print("\n\nVisibility Options by Tier:")
    print("-" * 40)
    for vis_type, desc in VISIBILITY_TYPES.items():
        print(f"  {vis_type}: {desc}")
    
    return 0
