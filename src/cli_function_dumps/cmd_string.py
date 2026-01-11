# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_string(args):
    """String manipulation utilities inspired by Sketchfab's JS utilities."""
    text = args.text
    
    if args.slugify:
        # Convert to URL-friendly slug
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        print(f"{STRING_CONVERSIONS['slug']} {slug}")
        return 0
    
    if args.camel:
        # Convert to camelCase
        words = re.split(r'[-_\s]+', text)
        result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        print(f"{STRING_CONVERSIONS['camelcase']} {result}")
        return 0
    
    if args.kebab:
        # Convert to kebab-case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
        result = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
        result = re.sub(r'[-_\s]+', '-', result)
        print(f"{STRING_CONVERSIONS['kebabcase']} {result}")
        return 0
    
    if args.snake:
        # Convert to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        result = re.sub(r'[-_\s]+', '_', result)
        print(f"{STRING_CONVERSIONS['snakecase']} {result}")
        return 0
    
    if args.title:
        # Convert to Title Case
        result = text.replace('-', ' ').replace('_', ' ').title()
        print(f"{STRING_CONVERSIONS['titlecase']} {result}")
        return 0
    
    if args.truncate:
        max_len = args.truncate
        if len(text) <= max_len:
            print(text)
        else:
            print(f"{text[:max_len-3]}...")
        return 0
    
    # Default: show all conversions
    print(f"{STRING_CONVERSIONS['original']} {text}")
    print("-" * 40)
    
    # Slug
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    print(f"{STRING_CONVERSIONS['slug']:14} {slug}")
    
    # camelCase
    words = re.split(r'[-_\s]+', text)
    camel = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    print(f"{STRING_CONVERSIONS['camelcase']:14} {camel}")
    
    # kebab-case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
    kebab = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    kebab = re.sub(r'[-_\s]+', '-', kebab)
    print(f"{STRING_CONVERSIONS['kebabcase']:14} {kebab}")
    
    # snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    snake = re.sub(r'[-_\s]+', '_', snake)
    print(f"{STRING_CONVERSIONS['snakecase']:14} {snake}")
    
    # Title Case
    title = text.replace('-', ' ').replace('_', ' ').title()
    print(f"{STRING_CONVERSIONS['titlecase']:14} {title}")
    
    return 0
