# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_ai_info(args):
    """Display information about Sketchfab AI tools and providers."""
    
    print("Sketchfab AI Tools")
    print("=" * 60)
    print("\nSupported AI Actions:")
    print("-" * 40)
    for action, desc in AI_ACTIONS.items():
        print(f"  {action}:")
        print(f"    {desc}")
    
    print("\n\nAI Providers:")
    print("-" * 40)
    for provider, info in AI_PROVIDERS.items():
        print(f"  {provider}:")
        print(f"    Supported actions: {', '.join(info['actions'])}")
    
    print("\n\nText-to-3D Providers:")
    print("-" * 40)
    text_to_3d = [p for p, i in AI_PROVIDERS.items() if 'text_to_3d' in i['actions']]
    print(f"  {', '.join(text_to_3d)}")
    
    print("\nImage-to-3D Providers:")
    print("-" * 40)
    img_to_3d = [p for p, i in AI_PROVIDERS.items() if 'image_to_3d' in i['actions']]
    print(f"  {', '.join(img_to_3d)}")
    
    return 0
