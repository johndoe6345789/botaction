# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_info(args):
    """Show information about available commands."""
    info = get_info_strings()
    sep = info['separator'] * info['separator_length']

    print(info['title'])
    print(sep)
    print()

    # Print each section
    for section_key, section in info['sections'].items():
        print(section['title'])
        for cmd in section['commands']:
            print(f"  {cmd['name']:14}- {cmd['description']}")
        print()

    print(INFO_CONFIG['config_constants_header'])
    print(f"  {INFO_CONFIG['api_base_url']} {SKETCHFAB_API_BASE}")
    print(
        INFO_CONFIG['embed_options_count'].format(
            count=len(EMBED_OPTIONS)
        )
    )
    print(
        INFO_CONFIG['quality_presets_list'].format(
            list=', '.join(QUALITY_PRESETS.keys())
        )
    )
    print(
        INFO_CONFIG['environment_presets_list'].format(
            list=', '.join(ENVIRONMENT_PRESETS.keys())
        )
    )
    print(
        INFO_CONFIG['ai_providers_list'].format(
            list=', '.join(AI_PROVIDERS.keys())
        )
    )
    print(
        INFO_CONFIG['download_formats_list'].format(
            list=', '.join(DOWNLOAD_FORMATS)
        )
    )
    print(
        INFO_CONFIG['brand_colors_count'].format(
            count=len(BRAND_COLORS)
        )
    )
    print(
        INFO_CONFIG['breakpoints_info'].format(
            count=len(BREAKPOINTS),
            list=', '.join(BREAKPOINTS.keys())
        )
    )
    print(
        INFO_CONFIG['license_types_count'].format(
            count=len(LICENSE_TYPES)
        )
    )
    print(
        INFO_CONFIG['spring_presets_count'].format(
            count=len(SPRING_PRESETS)
        )
    )
    print()
    print(info['footer'])
