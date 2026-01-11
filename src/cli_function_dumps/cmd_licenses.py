# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_licenses(args):
    """Display Creative Commons license information."""
    
    if args.license:
        # Show specific license
        if args.license not in LICENSE_TYPES:
            print(ERROR_MESSAGES['unknown_license'].format(license=args.license))
            print(
                ERROR_MESSAGES['available_licenses'].format(
                    list=', '.join(LICENSE_TYPES.keys())
                )
            )
            return 1
        
        lic = LICENSE_TYPES[args.license]
        print(f"{LICENSE_LABELS['name']} {lic['name']}")
        print("=" * 60)
        if lic['url']:
            print(f"{LICENSE_LABELS['url']} {lic['url']}")
        allows = ', '.join(lic['allows']) if lic['allows'] else MAIN_LABELS['none']
        requires = ', '.join(lic['requires']) if lic['requires'] else MAIN_LABELS['none']
        print(f"\n{LICENSE_LABELS['allows']} {allows}")
        print(f"{LICENSE_LABELS['requires']} {requires}")
        return 0
    
    print(HEADERS['cc_licenses'])
    print("=" * 60)
    print(SUBHEADERS['used_for_licensing'])
    print()
    
    for code, lic in LICENSE_TYPES.items():
        print(f"\n{code}")
        print(f"  {LICENSE_LABELS['name']} {lic['name']}")
        allows = ', '.join(lic['allows']) if lic['allows'] else 'None'
        requires = ', '.join(lic['requires']) if lic['requires'] else 'None'
        print(f"  {LICENSE_LABELS['allows']} {allows}")
        print(f"  {LICENSE_LABELS['requires']} {requires}")
    
    print(f"\n\n{LICENSE_LABELS['permission_types_header']}")
    print("-" * 40)
    for perm in PERMISSION_TYPES:
        print(f"  {perm['name']:15} - {perm['description']}")
    
    return 0
