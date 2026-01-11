# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_privacy(args):
    """Display cookie consent categories."""
    
    print(HEADERS['cookie_consent'])
    print("=" * 60)
    print(SUBHEADERS['onetrust_gdpr'])
    print()
    
    for code, cat in CONSENT_CATEGORIES.items():
        required = "✓ Required" if cat['required'] else "○ Optional"
        print(f"\n{code} - {cat['name']} [{required}]")
        print(f"  {cat['description']}")
    
    print(f"\n\n{PRIVACY_LABELS['usage_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['consent_usage'])
    
    return 0
