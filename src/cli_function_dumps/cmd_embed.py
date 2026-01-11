# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_embed(args):
    """Generate embed URL or iframe code for a Sketchfab model."""
    model_id = extract_model_id(args.model_id_or_url)
    
    if not model_id:
        print(
            ERROR_MESSAGES['model_id_extract_failed'].format(
                input=args.model_id_or_url
            )
        )
        return 1
    
    # Build embed parameters
    params = {}
    
    if args.autostart:
        params['autostart'] = 1
    if args.autospin is not None:
        params['autospin'] = args.autospin
    if args.no_ui:
        params['ui_controls'] = 0
        params['ui_infos'] = 0
        params['ui_inspector'] = 0
    if not args.watermark:
        params['ui_watermark'] = 0
    if args.transparent:
        params['transparent'] = 1
    if args.no_scrollwheel:
        params['scrollwheel'] = 0
    if args.animation_autoplay:
        params['animation_autoplay'] = 1
    if args.annotation is not None:
        params['annotation'] = args.annotation
    if args.preload:
        params['preload'] = 1
    
    # Build URL
    embed_url = f"{SKETCHFAB_BASE_URL}/models/{model_id}/embed"
    if params:
        embed_url += '?' + urlencode(params)
    
    print(f"Model ID: {model_id}")
    print(f"\nEmbed URL:")
    print(f"  {embed_url}")
    
    if args.iframe:
        width = args.width or 640
        height = args.height or 480
        iframe = f'''<iframe title="Sketchfab Model" width="{width}" height="{height}" src="{embed_url}" frameborder="0" allow="autoplay; fullscreen; xr-spatial-tracking" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>'''
        print(f"\niFrame Code:")
        print(f"  {iframe}")
    
    if args.copy:
        try:
            import pyperclip
            pyperclip.copy(embed_url if not args.iframe else iframe)
            print("\n✓ Copied to clipboard!")
        except ImportError:
            print("\n(Install pyperclip to enable clipboard copy: pip install pyperclip)")
    
    return 0
